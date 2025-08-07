from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

try:  # optional
    import webbrowser  # noqa: F401
except Exception:  # pragma: no cover
    webbrowser = None  # type: ignore

from ..agents import AgentReport
from ..orchestrator.core import OrchestratorReport


def _score_to_color(score: float) -> str:
    # Accept either 0-1 or 0-100 inputs; normalize to 0-100 scale
    s = float(score)
    if s <= 1.0:
        s = max(0.0, min(1.0, s)) * 100.0
    # thresholds
    if s >= 75:
        return "green"
    if s >= 50:
        return "yellow"
    return "red"


def _score_display(score: float) -> str:
    s = float(score)
    if s <= 1.0:
        return f"{s*100:.0f}%"
    return f"{s:.0f}"


def _pretty_json(data: Any) -> str:
    try:
        if is_dataclass(data):
            data = asdict(data)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        try:
            return json.dumps(str(data), ensure_ascii=False, indent=2)
        except Exception:
            return str(data)


def render_dashboard(
    report: OrchestratorReport,
    *,
    document: Optional[Any] = None,
    output_dir: str | os.PathLike = "runs",
    open_in_browser: bool = False,
) -> Path:
    """
    Render an HTML dashboard for an OrchestratorReport into runs/<timestamp>/report.html.
    Optionally opens in the default browser.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(output_dir) / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "report.html"

    # Jinja2 env
    templates_path = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_path)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("dashboard.html")

    # Build doc metadata
    doc_meta: Dict[str, Any] = {}
    doc_source: Optional[str] = None
    if isinstance(document, dict):
        doc_meta = {k: v for k, v in document.items() if k != "text"}
        doc_source = document.get("source_path")
    else:
        try:
            from ..utils.ingest import Document as IngestDocument  # type: ignore

            if isinstance(document, IngestDocument):
                doc_meta = document.metadata or {}
                doc_source = document.source_path
        except Exception:
            pass

    # Prepare agents block
    agents_view: List[Dict[str, Any]] = []
    for r in (report.per_agent or []):
        if not isinstance(r, AgentReport):
            # best effort mapping
            try:
                r = AgentReport(**r)  # type: ignore[arg-type]
            except Exception:
                pass
        agents_view.append(
            {
                "name": getattr(r, "name", "Agent"),
                "summary": getattr(r, "summary", ""),
                "comments": list(getattr(r, "comments", []) or []),
                "suggestions": list(getattr(r, "suggestions", []) or []),
                "score_display": _score_display(getattr(r, "score", 0.0)),
                "score_color": _score_to_color(getattr(r, "score", 0.0)),
                "metadata": getattr(r, "metadata", None),
                "metadata_pretty": _pretty_json(getattr(r, "metadata", None)) if getattr(r, "metadata", None) else None,
            }
        )

    confidence = float(getattr(report, "confidence", 0.0))
    confidence_pct = confidence * 100.0 if confidence <= 1.0 else confidence
    ctx = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document_type": getattr(report, "document_type", "unknown"),
        "classification_label": getattr(report.classification, "label", "unknown"),
        "classification_reason": getattr(report.classification, "reason", None),
        "confidence_pct": f"{confidence_pct:.0f}",
        "confidence_color": _score_to_color(confidence),
        "doc_meta": doc_meta,
        "doc_meta_pretty": _pretty_json(doc_meta) if doc_meta else "",
        "doc_source": doc_source,
        "synthesis": getattr(report, "synthesis", ""),
        "agents": agents_view,
    }

    html = template.render(**ctx)
    out_path.write_text(html, encoding="utf-8")

    if open_in_browser and webbrowser is not None:
        try:
            webbrowser.open_new_tab(out_path.as_uri())
        except Exception:
            pass

    return out_path

