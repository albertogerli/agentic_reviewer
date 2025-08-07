from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .utils.ingest import ingest
from .utils.report import render_dashboard
from .orchestrator.core import Orchestrator, OrchestratorReport
from .utils.llm import EchoJSONLLM
from .utils.classifier import DocumentClassifier, LLMClient as ClassifierLLMProtocol


class HeuristicClassifierLLM(ClassifierLLMProtocol):
    """Tiny heuristic stub to satisfy DocumentClassifier's LLM dependency.

    It inspects the provided prompt for a section that contains the document
    and returns a JSON string with `label` and `reason`.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        self._model = model  # kept for CLI parity; not used by heuristic

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        import json as _json

        text = prompt
        marker = "Document to Classify:\n"
        if marker in prompt:
            text = prompt.split(marker, 1)[1]
        text_l = text.lower()

        label = "Generic"
        reason = "Fallback generic classification."

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

        return _json.dumps({"label": label, "reason": reason})


def build_orchestrator(model: Optional[str], *, verbose: bool) -> Orchestrator:
    # Analysis LLM stub (generate interface)
    analysis_llm = EchoJSONLLM()

    # Classifier LLM stub (complete interface)
    classifier_llm = HeuristicClassifierLLM(model=model)

    classifier = DocumentClassifier(
        llm=classifier_llm,
        model=model,
        temperature=0.0,
    )

    orch = Orchestrator(
        classifier=classifier,
        analysis_llm=analysis_llm,
        max_feedback_rounds=1,
        run_parallel=True,
    )
    if verbose:
        print("[agentic] Orchestrator initialized (parallel=True, feedback_rounds=1)")
    return orch


async def run_once(file_path: str, *, model: Optional[str], open_browser: bool, verbose: bool) -> OrchestratorReport:
    if verbose:
        print(f"[agentic] Ingesting file: {file_path}")
    doc = ingest(path=file_path)

    if verbose:
        print("[agentic] Building orchestrator…")
    orch = build_orchestrator(model, verbose=verbose)

    if verbose:
        print("[agentic] Running analysis…")
    report = await orch.analyze(doc.text)

    if verbose:
        print("[agentic] Rendering dashboard…")
    out_path = render_dashboard(report, document=doc, open_in_browser=open_browser)
    if verbose:
        print(f"[agentic] Report saved to: {out_path}")

    return report


async def run_loop(
    file_path: str,
    *,
    model: Optional[str],
    open_browser: bool,
    verbose: bool,
    max_iters: int,
) -> OrchestratorReport:
    if verbose:
        print(f"[agentic] Ingesting file: {file_path}")
    doc = ingest(path=file_path)
    base_text = doc.text

    orch = build_orchestrator(model, verbose=verbose)

    best: Optional[OrchestratorReport] = None
    prev_conf: Optional[float] = None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("runs") / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "config.json").write_text(
        json.dumps({
            "mode": "loop",
            "max_iters": max_iters,
            "file": file_path,
            "model": model,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for i in range(1, max_iters + 1):
        if verbose:
            print(f"[agentic] Loop iteration {i}/{max_iters}…")
        report = await orch.analyze(base_text if i == 1 else base_text + "\n\n(Iterative context applied)")

        # Persist artifacts per iteration
        iter_payload: dict[str, Any] = {
            "iteration": i,
            "report": {
                "document_type": report.document_type,
                "classification": asdict(report.classification),
                "synthesis": report.synthesis,
                "confidence": report.confidence,
                "metadata": report.metadata,
            },
        }
        (run_dir / f"iter_{i:02d}.json").write_text(
            json.dumps(iter_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        if best is None or report.confidence > best.confidence:
            best = report

        # simple stopping rule: if confidence improvement < 0.005, stop early
        if prev_conf is not None and (report.confidence - prev_conf) < 0.005:
            if verbose:
                print("[agentic] Early stop: negligible improvement in confidence")
            break
        prev_conf = report.confidence

    assert best is not None

    # Final dashboard for the best report
    out_path = render_dashboard(best, document=doc, open_in_browser=open_browser)
    if verbose:
        print(f"[agentic] Final best report saved to: {out_path}")

    return best


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agentic", description="Agentic document analysis CLI")
    sub = p.add_subparsers(dest="command", required=True)

    # analyze subcommand
    p_an = sub.add_parser("analyze", help="One-shot analysis of a document")
    p_an.add_argument("file", type=str, help="Path to the input file")
    p_an.add_argument("--open-browser", action="store_true", help="Open the HTML report in the default browser")
    p_an.add_argument("--verbose", action="store_true", help="Verbose logging")
    p_an.add_argument("--model", type=str, default="gpt-4o", help="Model name for classification (default: gpt-4o)")

    # loop subcommand
    p_lp = sub.add_parser("loop", help="Iterative auto-loop analysis")
    p_lp.add_argument("file", type=str, help="Path to the input file")
    p_lp.add_argument("--max", dest="max_iters", type=int, default=5, help="Maximum iterations (default: 5)")
    p_lp.add_argument("--open-browser", action="store_true", help="Open the final HTML report in the default browser")
    p_lp.add_argument("--verbose", action="store_true", help="Verbose logging")
    p_lp.add_argument("--model", type=str, default="gpt-4o", help="Model name for classification (default: gpt-4o)")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        report = asyncio.run(
            run_once(
                args.file,
                model=args.model,
                open_browser=args.open_browser,
                verbose=args.verbose,
            )
        )
        if args.verbose:
            print(
                f"[agentic] Done. confidence={report.confidence:.3f}, type={report.document_type}"
            )
        return 0

    if args.command == "loop":
        report = asyncio.run(
            run_loop(
                args.file,
                model=args.model,
                open_browser=args.open_browser,
                verbose=args.verbose,
                max_iters=args.max_iters,
            )
        )
        if args.verbose:
            print(
                f"[agentic] Done. best_confidence={report.confidence:.3f}, type={report.document_type}"
            )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

