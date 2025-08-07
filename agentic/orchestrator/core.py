from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import asyncio

from ..agents import Agent, AgentReport, get_registered_agents
from ..utils.classifier import ClassificationResult, DocumentClassifier
from ..utils.llm import LLMClient as AnalysisLLMClient


@dataclass(slots=True)
class OrchestratorReport:
    """Final result of orchestration across multiple agents.

    Attributes:
        document_type: Normalized document type key used to select agents.
        classification: Raw classification result from the classifier (label + reason).
        synthesis: A synthesized summary across all agents.
        per_agent: Ordered list of the final report from each agent (post-feedback round).
        confidence: Global confidence score (0.0 - 1.0), derived from agent scores.
        metadata: Optional dictionary for any extra info (e.g., run mode, timings).
    """

    document_type: str
    classification: ClassificationResult
    synthesis: str
    per_agent: List[AgentReport] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Coordinates specialized agents to analyze a document end-to-end.

    Flow:
      1) Classify document to pick relevant agents.
      2) Run agents in parallel or sequentially.
      3) Aggregate their reports.
      4) Share peer summaries and allow a single feedback rerun (configurable).
      5) Produce an OrchestratorReport with synthesis and global confidence.
    """

    def __init__(
        self,
        classifier: DocumentClassifier,
        analysis_llm: Optional[AnalysisLLMClient] = None,
        *,
        max_feedback_rounds: int = 1,
        run_parallel: bool = True,
    ) -> None:
        self._classifier = classifier
        self._llm = analysis_llm
        self._max_feedback_rounds = max(0, int(max_feedback_rounds))
        self._run_parallel = bool(run_parallel)

    # -------------------------- Public API --------------------------
    async def analyze(self, document: Any) -> OrchestratorReport:
        """Run the full orchestration pipeline and return the final report."""
        text = str(document)
        classification = self._classifier.classify(text)
        doc_key = self._normalize_label_to_key(classification.label)

        agent_classes = get_registered_agents(doc_key)
        agents = [self._instantiate_agent(cls) for cls in agent_classes]

        # 1) Initial round
        initial_reports = await self._run_agents(agents, document)

        # 2) Optionally perform feedback rounds (at most one round as per spec, but parameterized)
        final_reports = initial_reports
        for round_idx in range(self._max_feedback_rounds):
            peer_summaries = self._summarize_peers(final_reports)
            feedback_docs = [self._make_feedback_document(a.name, document, peer_summaries) for a in agents]
            rerun_reports = await self._run_agents(agents, feedback_docs)
            final_reports = rerun_reports
            # single rerun per spec; break after one loop
            break

        # 3) Synthesize and compute global confidence
        synthesis = self._synthesize(final_reports)
        confidence = self._global_confidence(final_reports)

        return OrchestratorReport(
            document_type=doc_key,
            classification=classification,
            synthesis=synthesis,
            per_agent=final_reports,
            confidence=confidence,
            metadata={
                "run_parallel": self._run_parallel,
                "max_feedback_rounds": self._max_feedback_rounds,
                "num_agents": len(agents),
            },
        )

    # -------------------------- Internals --------------------------
    def _instantiate_agent(self, cls: type[Agent]) -> Agent:
        # Try best-effort to pass llm in constructor, else set attribute if present
        try:
            if self._llm is not None:
                return cls(llm=self._llm)  # type: ignore[call-arg]
        except TypeError:
            pass
        agent = cls()  # type: ignore[call-arg]
        if self._llm is not None and hasattr(agent, "llm"):
            try:
                setattr(agent, "llm", self._llm)
            except Exception:
                pass
        return agent

    async def _run_agents(self, agents: Sequence[Agent], document_or_docs: Any | Sequence[Any]) -> List[AgentReport]:
        # Support passing either a single shared document or a per-agent list of docs
        if isinstance(document_or_docs, (list, tuple)):
            docs: List[Any] = list(document_or_docs)
            if len(docs) != len(agents):
                raise ValueError("Length of documents must match number of agents when passing a sequence")
        else:
            docs = [document_or_docs for _ in agents]

        if not self._run_parallel or len(agents) <= 1:
            results: List[AgentReport] = []
            for agent, doc in zip(agents, docs):
                results.append(await asyncio.to_thread(agent.analyze, doc))
            return results

        tasks = [asyncio.to_thread(agent.analyze, doc) for agent, doc in zip(agents, docs)]
        reports: List[AgentReport] = list(await asyncio.gather(*tasks))
        return reports

    def _summarize_peers(self, reports: Sequence[AgentReport]) -> Dict[str, Dict[str, Any]]:
        """Build a compact summary of each agent's findings to share with others."""
        summary: Dict[str, Dict[str, Any]] = {}
        for r in reports:
            summary[r.name] = {
                "summary": r.summary,
                "top_comments": r.comments[:5] if r.comments else [],
                "score": r.score,
                "suggestions": r.suggestions[:5] if r.suggestions else [],
            }
        return summary

    def _make_feedback_document(self, agent_name: str, original_document: Any, peer_summaries: Dict[str, Dict[str, Any]]) -> str:
        # Create a lightweight augmentation of the original document that includes peer findings.
        lines = [str(original_document), "\n\n---\nPeers' Findings Summary (for feedback round):"]
        for name, data in peer_summaries.items():
            if name == agent_name:
                continue
            lines.append(f"\n[{name}] Score={data.get('score', 0)}")
            if data.get("summary"):
                lines.append(f"Summary: {data['summary']}")
            comments = data.get("top_comments") or []
            if comments:
                lines.append("Top comments:")
                for c in comments[:3]:
                    lines.append(f" - {c}")
            suggestions = data.get("suggestions") or []
            if suggestions:
                lines.append("Suggestions:")
                for s in suggestions[:3]:
                    lines.append(f" - {s}")
        lines.append("\nEnd of peers' summary.")
        return "\n".join(lines)

    def _synthesize(self, reports: Sequence[AgentReport]) -> str:
        if not reports:
            return "No agents available for this document type; no synthesis produced."
        # Simple heuristic synthesis: combine summaries and highlight top suggestions
        parts: List[str] = ["Synthesis across agents:"]
        for r in reports:
            parts.append(f"- {r.name}: {r.summary}")
        # Collate top suggestions
        suggestions: List[str] = []
        for r in reports:
            if r.suggestions:
                suggestions.extend(r.suggestions[:2])
        if suggestions:
            parts.append("Top cross-agent suggestions:")
            for s in suggestions[:5]:
                parts.append(f" • {s}")
        return "\n".join(parts)

    def _global_confidence(self, reports: Sequence[AgentReport]) -> float:
        if not reports:
            return 0.0
        scores: List[float] = []
        for r in reports:
            s = float(r.score)
            # Normalize if looks like 0-100
            if s > 1.0:
                s = max(0.0, min(100.0, s)) / 100.0
            scores.append(max(0.0, min(1.0, s)))
        return sum(scores) / len(scores)

    def _normalize_label_to_key(self, label: str) -> str:
        l = label.strip().lower()
        mapping = {
            "contract": "contract",
            "research paper": "research_paper",
            "invoice": "invoice",
            "resume": "resume",
            "generic": "generic",
        }
        return mapping.get(l, l.replace(" ", "_"))

