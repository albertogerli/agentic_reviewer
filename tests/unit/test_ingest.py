import io
import json
from pathlib import Path
import tempfile
import os

import pytest

from agentic.utils.ingest import ingest, Document, _normalize_text


def test_ingest_plain_text_bytes():
    raw = b"Hello, world!\nThis is a test.\r\nWith Windows newlines.\rEnd.\n\n\nExtra."
    doc = ingest(raw=raw, filename="note.txt")
    assert isinstance(doc, Document)
    assert "Hello, world!" in doc.text
    # normalized newlines, collapsed extra
    assert "\r" not in doc.text
    assert "\n\n\n" not in doc.text
    assert doc.metadata.get("mime").startswith("text/")
    assert doc.metadata.get("encoding") in {"utf-8", "ascii", None}  # chardet optional


def test_ingest_json_bytes_roundtrip():
    payload = {"a": 1, "b": [1, 2], "ok": True}
    raw = json.dumps(payload).encode("utf-8")
    doc = ingest(raw=raw, filename="data.json")
    # pretty printed JSON should contain fields
    assert '"a": 1' in doc.text
    assert '"ok": true' in doc.text
    assert doc.metadata["mime"] == "application/json"


def test_ingest_html_bytes_without_bs4(monkeypatch):
    # Simulate BeautifulSoup missing
    import agentic.utils.ingest as ing

    monkeypatch.setattr(ing, "BeautifulSoup", None, raising=False)
    html = b"<html><head><title>T</title></head><body><script>x=1</script><h1>Hi</h1>Body</body></html>"
    doc = ingest(raw=html, filename="page.html")
    # falls back to raw decode when bs4 not available
    assert "<h1>Hi</h1>" in doc.text or "Hi" in doc.text


def test_ingest_from_path_tmpfile(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("Line1\n\n\nLine2\r\nEnd", encoding="utf-8")
    doc = ingest(path=str(p))
    assert doc.source_path == str(p)
    assert doc.metadata["filename"] == "sample.txt"
    assert "\n\n\n" not in doc.text


def test_normalize_text():
    s = "A\r\nB\rC\n\n\nD  \n"
    out = _normalize_text(s)
    assert out == "A\nB\nC\n\nD"
