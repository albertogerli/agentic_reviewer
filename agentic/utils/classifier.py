import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Protocol, Tuple


class LLMClient(Protocol):
    """Minimal protocol for an LLM client used by DocumentClassifier.

    Any client must implement a `complete` method that takes a prompt string
    and returns the model's raw text completion as a string.
    """

    def complete(self, prompt: str, *, model: Optional[str] = None, temperature: float = 0.0, max_tokens: Optional[int] = None) -> str:  # pragma: no cover - protocol
        ...


@dataclass(frozen=True)
class ClassificationResult:
    label: str
    reason: Optional[str] = None


class DocumentClassifier:
    """Classify a document's text into a type label using an LLM with few-shot prompting.

    Labels include: Contract, Research Paper, Invoice, Resume, Generic.

    Results are cached in .cache/ to minimize repeat calls.
    """

    DEFAULT_LABELS: Tuple[str, ...] = (
        "Contract",
        "Research Paper",
        "Invoice",
        "Resume",
        "Generic",
    )

    def __init__(
        self,
        llm: LLMClient,
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        labels: Iterable[str] | None = None,
        cache_dir: str | os.PathLike = ".cache",
    ) -> None:
        self._llm = llm
        self._model = model
        self._temperature = float(temperature)
        self._labels = tuple(labels) if labels is not None else self.DEFAULT_LABELS
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------- Public API ----------------------
    def classify(self, text: str) -> ClassificationResult:
        """Return the predicted label for the given document text.

        The LLM is queried with a deterministic, few-shot prompt. Results are
        cached using a content hash of the input text and settings.
        """
        key = self._make_cache_key(text)
        cached = self._read_cache(key)
        if cached is not None:
            return cached

        prompt = self._build_prompt(text)
        raw = self._llm.complete(prompt, model=self._model, temperature=self._temperature, max_tokens=256)
        parsed = self._parse_output(raw)
        # Fallback to Generic if parsing fails or label invalid
        if parsed is None or parsed.label not in self._labels:
            parsed = ClassificationResult(label="Generic", reason="Unrecognized or invalid label; defaulted to Generic")

        self._write_cache(key, parsed)
        return parsed

    # ---------------------- Internals ----------------------
    def _make_cache_key(self, text: str) -> str:
        h = hashlib.sha256()
        h.update(text.encode("utf-8"))
        h.update("|".encode("utf-8"))
        h.update(",".join(self._labels).encode("utf-8"))
        h.update("|".encode("utf-8"))
        h.update(str(self._model or "").encode("utf-8"))
        h.update("|".encode("utf-8"))
        h.update(str(self._temperature).encode("utf-8"))
        return h.hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self._cache_dir / f"doc_class_{key}.json"

    def _read_cache(self, key: str) -> Optional[ClassificationResult]:
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            label = data.get("label")
            reason = data.get("reason")
            if isinstance(label, str):
                return ClassificationResult(label=label, reason=reason if isinstance(reason, str) else None)
        except Exception:
            return None
        return None

    def _write_cache(self, key: str, result: ClassificationResult) -> None:
        path = self._cache_path(key)
        try:
            payload = {"label": result.label}
            if result.reason:
                payload["reason"] = result.reason
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            # Best-effort caching; ignore errors
            pass

    def _build_prompt(self, text: str) -> str:
        labels_str = ", ".join(self._labels)
        examples = [
            (
                "This Agreement is made between Alpha Corp (the \"Company\") and Beta LLC (the \"Vendor\"). The parties agree as follows: 1) Term; 2) Indemnification; 3) Governing Law...",
                "Contract",
                "Contains parties, terms, indemnification, governing law—hallmarks of a legal agreement.",
            ),
            (
                "In this paper, we propose a novel transformer-based architecture. We evaluate on the MNIST and CIFAR-10 datasets and compare results...",
                "Research Paper",
                "Structure with abstract-like language, experiments, datasets, and comparisons typical of academic papers.",
            ),
            (
                "Invoice #10293\nBill To: ACME Inc.\nDate: 2023-09-01\nItems:\n- Consulting Services (10 hours) $2000\nTotal Due: $2000\nPayment Terms: Net 30",
                "Invoice",
                "Has invoice number, bill-to, line items, totals, and payment terms—typical invoice fields.",
            ),
            (
                "John Doe\nEmail: john@example.com\nExperience: Software Engineer at XYZ (2019–2023). Skills: Python, ML, AWS. Education: B.Sc. Computer Science...",
                "Resume",
                "Includes contact info, experience, skills, and education sections consistent with a CV/resume.",
            ),
            (
                "Yesterday I went to the store and bought some groceries. The weather was nice and I decided to take a walk in the park...",
                "Generic",
                "Narrative free-form text without structured fields matching the other categories.",
            ),
        ]

        # Trim input to a reasonable size for classification prompt
        snippet = text.strip()
        if len(snippet) > 4000:
            snippet = snippet[:4000] + "\n...[truncated]"

        example_blocks = []
        for ex_text, ex_label, ex_reason in examples:
            example_blocks.append(
                f"Example Document:\n{ex_text}\nClassification: {ex_label}\nReason: {ex_reason}\n---"
            )
        examples_str = "\n".join(example_blocks)

        instruction = (
            "You are a document type classifier. Given a document snippet, choose exactly one label "
            f"from: {labels_str}. Respond in strict JSON with fields 'label' and 'reason'."
        )

        return (
            f"{instruction}\n\n"
            f"Few-shot Examples:\n{examples_str}\n\n"
            f"Document to Classify:\n{snippet}\n\n"
            "Return JSON only, no extra text."
        )

    def _parse_output(self, raw: str) -> Optional[ClassificationResult]:
        if not raw:
            return None
        raw = raw.strip()
        # Try to locate JSON substring if the model added extra text.
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start : end + 1]
        else:
            candidate = raw
        try:
            data = json.loads(candidate)
            label = data.get("label")
            reason = data.get("reason")
            if isinstance(label, str):
                # Normalize capitalization to match configured labels where possible
                norm = self._normalize_label(label)
                return ClassificationResult(label=norm, reason=reason if isinstance(reason, str) else None)
        except Exception:
            return None
        return None

    def _normalize_label(self, label: str) -> str:
        # Exact match first
        if label in self._labels:
            return label
        lower = label.lower().strip()
        # Attempt loose matching
        mapping = {l.lower(): l for l in self._labels}
        if lower in mapping:
            return mapping[lower]
        # Common synonyms
        synonyms = {
            "paper": "Research Paper",
            "research": "Research Paper",
            "cv": "Resume",
            "curriculum vitae": "Resume",
            "bill": "Invoice",
            "receipt": "Invoice",
            "agreement": "Contract",
            "contract": "Contract",
        }
        if lower in synonyms and synonyms[lower] in self._labels:
            return synonyms[lower]
        return label

__all__ = ["DocumentClassifier", "ClassificationResult", "LLMClient"]

