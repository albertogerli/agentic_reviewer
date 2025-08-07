import asyncio
from pathlib import Path

from agentic.__main__ import build_orchestrator
from agentic.utils.ingest import ingest


async def _run(file_path: str):
    orch = build_orchestrator(model=None, verbose=False)
    doc = ingest(path=file_path)
    report = await orch.analyze(doc.text)
    return report


def test_examples_integration(tmp_path):
    # Run on all three example docs and assert reasonable outputs
    base = Path("examples")
    files = [base / "contract.txt", base / "paper.txt", base / "invoice.txt"]

    reports = []
    for p in files:
        rep = asyncio.run(_run(str(p)))
        reports.append(rep)

    assert any(r.document_type == "contract" for r in reports)
    assert any(r.document_type == "research_paper" for r in reports)
    assert any(r.document_type == "invoice" for r in reports)

    # All reports should have 0 <= confidence <= 1
    for r in reports:
        assert 0.0 <= r.confidence <= 1.0
        # ensure synthesis not empty
        assert isinstance(r.synthesis, str) and len(r.synthesis) > 0
