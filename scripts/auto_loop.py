from __future__ import annotations

import argparse
import asyncio
import json
import signal
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from scripts.load_env import load_env
from agentic.utils.ingest import ingest
from agentic.orchestrator.core import Orchestrator, OrchestratorReport
from agentic.utils.llm import EchoJSONLLM
from agentic.utils.classifier import DocumentClassifier, ClassificationResult, LLMClient as ClassifierLLMProtocol


class HeuristicClassifierLLM(ClassifierLLMProtocol):
    """A tiny heuristic LLM stub that implements the `complete` method used by
    DocumentClassifier. It detects the document type using simple keyword rules
    and returns a strict JSON string with `label` and `reason`.

    This avoids depending on a real external LLM while enabling the pipeline to run.
    """

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        # Extract the section after "Document to Classify:" if present
        text = prompt
        marker = "Document to Classify:\n"
        if marker in prompt:
            text = prompt.split(marker, 1)[1]
        text_l = text.lower()

        label = "Generic"
        reason = "Fallback generic classification."

        # Very lightweight keyword heuristics
        if any(k in text_l for k in ["agreement", "governing law", "indemnity", "termination", "party"]):
            label = "Contract"
            reason = "Detected legal terms common in contracts (e.g., governing law, termination)."
        elif any(k in text_l for k in ["abstract", "method", "dataset", "results", "experiment", "references"]):
            label = "Research Paper"
            reason = "Detected academic structure/terms (abstract, method, results, references)."
        elif any(k in text_l for k in ["invoice", "bill to", "total due", "qty", "unit price", "payment terms", "net 30"]):
            label = "Invoice"
            reason = "Detected invoice-like fields (bill to, totals, payment terms)."
        elif any(k in text_l for k in ["experience", "skills", "education", "resume", "curriculum vitae", "cv"]):
            label = "Resume"
            reason = "Detected resume-related sections (experience, skills, education)."

        return json.dumps({"label": label, "reason": reason})


def build_orchestrator() -> Orchestrator:
    # Agent layer uses a generate() interface -> use the provided EchoJSONLLM stub by default
    analysis_llm = EchoJSONLLM()

    # Classifier layer expects an object with complete() -> provide a heuristic stub
    classifier_llm = HeuristicClassifierLLM()

    classifier = DocumentClassifier(
        llm=classifier_llm,
        model=None,
        temperature=0.0,
    )

    orch = Orchestrator(
        classifier=classifier,
        analysis_llm=analysis_llm,
        max_feedback_rounds=1,
        run_parallel=True,
    )
    return orch


def augment_with_previous_synthesis(text: str, prev_synthesis: Optional[str]) -> str:
    if not prev_synthesis:
        return text
    return (
        f"{text}\n\n---\nPrevious Synthesis Context (for iterative improvement):\n"
        f"{prev_synthesis}\n\nEnd previous synthesis."
    )


def save_iteration_artifacts(run_dir: Path, iteration: int, base_text: str, report: OrchestratorReport) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "iteration": iteration,
        "input_text_preview": base_text[:1000],
        "report": {
            "document_type": report.document_type,
            "classification": asdict(report.classification),
            "synthesis": report.synthesis,
            "per_agent": [
                {
                    "name": r.name,
                    "summary": r.summary,
                    "comments": r.comments,
                    "score": r.score,
                    "suggestions": r.suggestions,
                    "metadata": r.metadata,
                }
                for r in report.per_agent
            ],
            "confidence": report.confidence,
            "metadata": report.metadata,
        },
    }
    (run_dir / f"iter_{iteration:02d}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # Save synthesis as a separate text for quick inspection
    (run_dir / f"iter_{iteration:02d}_synthesis.txt").write_text(report.synthesis, encoding="utf-8")


async def run_auto_loop(
    *,
    source_path: Optional[str],
    raw_text: Optional[str],
    epsilon: float,
    max_iterations: int,
    run_dir: Path,
) -> OrchestratorReport:
    if not source_path and not raw_text:
        raise ValueError("Provide either --input-file or --text")

    # Ingest the initial document
    if source_path:
        doc = ingest(path=source_path)
    else:
        doc = ingest(raw=raw_text.encode("utf-8"), filename="input.txt")

    base_text = doc.text
    orchestrator = build_orchestrator()

    best_report: Optional[OrchestratorReport] = None
    prev_conf: Optional[float] = None
    prev_synthesis: Optional[str] = None

    # Ctrl-C friendly flag via signal
    stop_requested = False

    def _handle_sigint(signum, frame):  # type: ignore[no-untyped-def]
        nonlocal stop_requested
        stop_requested = True

    old_handler = signal.signal(signal.SIGINT, _handle_sigint)

    try:
        for i in range(1, max_iterations + 1):
            text_with_context = augment_with_previous_synthesis(base_text, prev_synthesis)
            report = await orchestrator.analyze(text_with_context)

            save_iteration_artifacts(run_dir, i, text_with_context, report)

            if best_report is None or report.confidence > (best_report.confidence if best_report else -1):
                best_report = report

            if prev_conf is not None:
                improvement = report.confidence - prev_conf
                if improvement < epsilon:
                    break
            prev_conf = report.confidence
            prev_synthesis = report.synthesis

            if stop_requested:
                break
    finally:
        signal.signal(signal.SIGINT, old_handler)

    assert best_report is not None
    # Save final best report
    (run_dir / "final_best.json").write_text(
        json.dumps(
            {
                "document_type": best_report.document_type,
                "classification": asdict(best_report.classification),
                "synthesis": best_report.synthesis,
                "confidence": best_report.confidence,
                "metadata": best_report.metadata,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "final_best_synthesis.txt").write_text(best_report.synthesis, encoding="utf-8")
    return best_report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Auto loop driver for iterative improvement.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input-file", type=str, help="Path to input document file to ingest.")
    src.add_argument("--text", type=str, help="Raw input text to analyze.")
    p.add_argument("--epsilon", type=float, default=0.01, help="Min improvement in confidence to continue (default: 0.01)")
    p.add_argument("--max-iters", type=int, default=5, help="Maximum iterations (default: 5)")
    p.add_argument(
        "--runs-dir",
        type=str,
        default="runs",
        help="Directory where run artifacts are stored (default: runs)",
    )
    p.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="Optional timestamp string for run folder; defaults to current time.",
    )
    p.add_argument(
        "--no-env",
        action="store_true",
        help="Do not attempt to load .env from project root.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if not args.no_env:
        load_env()

    ts = args.timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(args.runs_dir) / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save run config
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "epsilon": args.epsilon,
                "max_iters": args.max_iters,
                "input_file": args.input_file,
                "text_preview": (args.text[:1000] if args.text else None),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    best_report = asyncio.run(
        run_auto_loop(
            source_path=args.input_file,
            raw_text=args.text,
            epsilon=args.epsilon,
            max_iterations=args.max_iters,
            run_dir=run_dir,
        )
    )

    # Print a brief summary to stdout
    print(
        f"Completed. Best confidence={best_report.confidence:.3f}, type={best_report.document_type}. "
        f"Artifacts in: {run_dir}"
    )


if __name__ == "__main__":
    main()

