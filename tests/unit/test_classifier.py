import json
from dataclasses import dataclass

import pytest

from agentic.utils.classifier import DocumentClassifier, ClassificationResult, LLMClient


@dataclass
class DummyLLM:
    response: str

    def complete(self, prompt: str, *, model=None, temperature: float = 0.0, max_tokens=None) -> str:
        return self.response


def test_classifier_parsing_valid_json():
    llm = DummyLLM(response=json.dumps({"label": "Invoice", "reason": "Has totals."}))
    clf = DocumentClassifier(llm)
    res = clf.classify("Invoice #1 Total Due: $10")
    assert isinstance(res, ClassificationResult)
    assert res.label == "Invoice"
    assert res.reason == "Has totals."


def test_classifier_parsing_invalid_falls_back_generic():
    llm = DummyLLM(response="not json")
    clf = DocumentClassifier(llm)
    res = clf.classify("random text")
    assert res.label == "Generic"


def test_classifier_cache_roundtrip(tmp_path):
    # two calls with same content use cache; emulate by counting
    calls = {"n": 0}

    class CountingLLM:
        def complete(self, prompt: str, *, model=None, temperature: float = 0.0, max_tokens=None) -> str:
            calls["n"] += 1
            return json.dumps({"label": "Resume"})

    clf = DocumentClassifier(CountingLLM(), cache_dir=tmp_path)
    text = "Skills: Python. Experience: ..."
    r1 = clf.classify(text)
    r2 = clf.classify(text)
    assert r1.label == "Resume"
    assert r2.label == "Resume"
    assert calls["n"] == 1  # second came from cache


def test_classifier_label_normalization():
    llm = DummyLLM(response=json.dumps({"label": "cv"}))
    clf = DocumentClassifier(llm)
    res = clf.classify("Curriculum Vitae")
    assert res.label == "Resume"
