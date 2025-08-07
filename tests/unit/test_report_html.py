from pathlib import Path

from agentic.utils.report import render_dashboard
from agentic.orchestrator.core import OrchestratorReport
from agentic.utils.classifier import ClassificationResult
from agentic.agents.base import AgentReport


def test_render_dashboard_generates_html(tmp_path: Path):
    report = OrchestratorReport(
        document_type="contract",
        classification=ClassificationResult(label="Contract", reason="keywords"),
        synthesis="Synthesis across agents:\n- A: ok",
        per_agent=[
            AgentReport(name="A", summary="ok", comments=["c1", "c2"], score=0.8, suggestions=["s1"])  # type: ignore[arg-type]
        ],
        confidence=0.85,
    )

    out = render_dashboard(report, document=None, output_dir=tmp_path, open_in_browser=False)
    html = out.read_text(encoding="utf-8")

    assert html.startswith("<!DOCTYPE html>")
    assert "Agentic Analysis Dashboard" in html
    assert "Orchestrator Synthesis" in html
    assert "Agents" in html
    assert "Global Confidence" in html
