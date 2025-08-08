from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple
import asyncio

from ..agents import Agent, AgentReport, get_registered_agents
from ..utils.classifier import ClassificationResult, DocumentClassifier
from ..utils.llm import LLMClient


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
      2) Assign an LLM tier per agent (gpt-5 / gpt-5-mini / gpt-5-nano) dynamically.
      3) Run agents in parallel or sequentially.
      4) Share peer summaries and allow a single feedback rerun (configurable).
      5) Produce an OrchestratorReport with synthesis and global confidence.
    """

    def __init__(
        self,
        classifier: DocumentClassifier,
        *,
        llm_factory: Callable[[str], LLMClient],
        max_feedback_rounds: int = 1,
        run_parallel: bool = True,
        model_cap: Optional[str] = None,
    ) -> None:
        self._classifier = classifier
        self._llm_factory = llm_factory
        self._max_feedback_rounds = max(0, int(max_feedback_rounds))
        self._run_parallel = bool(run_parallel)
        self._model_cap = (model_cap or "").strip() or None

    # -------------------------- Public API --------------------------
    async def analyze(self, document: Any) -> OrchestratorReport:
        """Run the full orchestration pipeline and return the final report."""
        text = str(document)
        classification = self._classifier.classify(text)
        doc_key = self._normalize_label_to_key(classification.label)

        agent_classes = get_registered_agents(doc_key)
        # Decide tiers and instantiate agents with per-agent LLMs
        complexity = self._assess_complexity(text)
        tiers: Dict[str, str] = {}
        agents: List[Agent] = []
        for cls in agent_classes:
            agent_name = getattr(cls, "name", cls.__name__)
            base_tier = self._select_tier(agent_name, complexity)
            # Respect agent hints
            min_hint = getattr(cls, "min_tier", None)
            pref_hint = getattr(cls, "preferred_tier", None)
            hinted = self._respect_hints(base_tier, min_hint, pref_hint)
            tier = self._apply_cap(hinted)
            tiers[agent_name] = tier
            llm = self._llm_factory(tier)
            agents.append(self._instantiate_agent(cls, llm))

        # 1) Initial round
        initial_reports = await self._run_agents(agents, document)
        # Track chosen tiers in metadata
        per_agent_models = tiers.copy()

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
                "per_agent_models": per_agent_models,
            },
        )

    # -------------------------- Internals --------------------------
    def _instantiate_agent(self, cls: type[Agent], llm: Optional[LLMClient]) -> Agent:
        # Try best-effort to pass llm in constructor, else set attribute if present
        try:
            if llm is not None:
                return cls(llm=llm)  # type: ignore[call-arg]
        except TypeError:
            pass
        agent = cls()  # type: ignore[call-arg]
        if llm is not None and hasattr(agent, "llm"):
            try:
                setattr(agent, "llm", llm)
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

    # ---------------- Tiering logic ----------------
    def _assess_complexity(self, text: str) -> float:
        """Return a complexity score in [0,1] using lightweight heuristics.
        Factors: length, numeric density, section markers, unique tokens.
        """
        import math
        t = text or ""
        n = len(t)
        # length factor (up to 20k chars)
        f_len = min(1.0, n / 20000.0)
        # digit density
        digits = sum(ch.isdigit() for ch in t)
        f_num = min(1.0, digits / max(1, n) * 50)  # scale
        # section markers (indicate structure)
        markers = ["abstract", "method", "results", "conclusion", "terms", "clause", "invoice", "total"]
        f_sections = min(1.0, sum(1 for m in markers if m in t.lower()) / 6.0)
        # crude vocabulary richness
        words = [w for w in t.lower().split() if w.isalpha()]
        uniq = len(set(words))
        f_vocab = min(1.0, (uniq / max(1, len(words))) * 5.0)
        score = max(0.0, min(1.0, 0.45 * f_len + 0.2 * f_num + 0.2 * f_sections + 0.15 * f_vocab))
        return score

    def _select_tier(self, agent_name: str, complexity: float) -> str:
        """Map complexity to a tier. Simple thresholds; can be extended or learned."""
        if complexity >= 0.66:
            return "gpt-5"
        if complexity >= 0.33:
            return "gpt-5-mini"
        return "gpt-5-nano"

    def _apply_cap(self, tier: str) - str:
        cap = (self._model_cap or "").strip()
        order = {"gpt-5-nano": 0, "gpt-5-mini": 1, "gpt-5": 2}
        if not cap or cap not in order:
            return tier
        return tier if order[tier] = order[cap] else cap

    def _respect_hints(self, base_tier: str, min_tier: Optional[str], preferred_tier: Optional[str]) - str:
        order = {"gpt-5-nano": 0, "gpt-5-mini": 1, "gpt-5": 2}
        tier = base_tier if base_tier in order else "gpt-5-mini"
        # Apply minimum hint
        if min_tier in order and order[tier] < order[min_tier]:
            tier = min_tier  # upgrade to min
        # Apply preferred if higher than current
        if preferred_tier in order and order[tier] < order[preferred_tier]:
            tier = preferred_tier
        return tier

