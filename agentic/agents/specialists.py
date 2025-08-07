from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ..agents import Agent, AgentReport, register_agent
from ..utils.llm import LLMClient


# -------------- Contracts Agents --------------

@dataclass
class LegalComplianceAgent(Agent):
    name: str = "LegalComplianceAgent"
    llm: LLMClient | None = None

    def analyze(self, document: Any) -> AgentReport:
        text = str(document)
        prompt = (
            "You are a contract compliance reviewer. Analyze the contract text for legal compliance risks,"
            " focusing on governing law, termination, confidentiality, IP, liability, indemnity, and dispute resolution."
            " Return a strict JSON object with keys: summary (string), comments (array of strings), score (0-100),"
            " suggestions (array of strings). Do not include any extra text.\n\n"
            "Contract Text:\n" + text + "\n\nJSON_RESPONSE_START\n"
        )
        raw = self.llm.generate(prompt) if self.llm else "{}"
        data: Dict[str, Any]
        try:
            import json

            data = json.loads(raw or "{}")
        except Exception:
            data = {}

        return AgentReport(
            name=self.name,
            summary=str(data.get("summary", "No summary produced.")),
            comments=list(map(str, data.get("comments", []))),
            score=float(data.get("score", 0.0)),
            suggestions=list(map(str, data.get("suggestions", []))) or None,
        )


@dataclass
class ClauseExtractorAgent(Agent):
    name: str = "ClauseExtractorAgent"
    llm: LLMClient | None = None

    def analyze(self, document: Any) -> AgentReport:
        text = str(document)
        prompt = (
            "You are a contract clause extraction expert. Extract key clauses: Parties, Term, Termination,"
            " Payment Terms, Confidentiality, IP, Liability, Indemnity, Governing Law, Dispute Resolution."
            " Return strict JSON with keys: summary, comments (array: each 'ClauseName: extracted text'),"
            " score (0-100 completeness), suggestions (array). No extra text.\n\n"
            "Contract Text:\n" + text + "\n\nJSON_RESPONSE_START\n"
        )
        raw = self.llm.generate(prompt) if self.llm else "{}"
        try:
            import json

            data = json.loads(raw or "{}")
        except Exception:
            data = {}

        return AgentReport(
            name=self.name,
            summary=str(data.get("summary", "No summary produced.")),
            comments=list(map(str, data.get("comments", []))),
            score=float(data.get("score", 0.0)),
            suggestions=list(map(str, data.get("suggestions", []))) or None,
        )


# Auto-register for document type 'contract'
register_agent("contract", LegalComplianceAgent)
register_agent("contract", ClauseExtractorAgent)


# -------------- Research Paper Agents --------------

@dataclass
class CitationCheckAgent(Agent):
    name: str = "CitationCheckAgent"
    llm: LLMClient | None = None

    def analyze(self, document: Any) -> AgentReport:
        text = str(document)
        prompt = (
            "You are a scholarly citation auditor. Identify missing references, broken citations, or format issues"
            " (APA/MLA/Chicago). Return strict JSON with: summary, comments (array - each a concrete issue),"
            " score (0-100 accuracy/coverage), suggestions (array actionable fixes). No extra text.\n\n"
            "Paper Text:\n" + text + "\n\nJSON_RESPONSE_START\n"
        )
        raw = self.llm.generate(prompt) if self.llm else "{}"
        try:
            import json

            data = json.loads(raw or "{}")
        except Exception:
            data = {}

        return AgentReport(
            name=self.name,
            summary=str(data.get("summary", "No summary produced.")),
            comments=list(map(str, data.get("comments", []))),
            score=float(data.get("score", 0.0)),
            suggestions=list(map(str, data.get("suggestions", []))) or None,
        )


@dataclass
class MethodologyAgent(Agent):
    name: str = "MethodologyAgent"
    llm: LLMClient | None = None

    def analyze(self, document: Any) -> AgentReport:
        text = str(document)
        prompt = (
            "You are a research methodology reviewer. Evaluate the study design, sample size, data collection,"
            " statistical methods, replication details, limitations, and ethics. Return strict JSON with: summary,"
            " comments (array of findings), score (0-100 rigor/transparency), suggestions (array actionable)."
            " No extra text.\n\n"
            "Paper Text:\n" + text + "\n\nJSON_RESPONSE_START\n"
        )
        raw = self.llm.generate(prompt) if self.llm else "{}"
        try:
            import json

            data = json.loads(raw or "{}")
        except Exception:
            data = {}

        return AgentReport(
            name=self.name,
            summary=str(data.get("summary", "No summary produced.")),
            comments=list(map(str, data.get("comments", []))),
            score=float(data.get("score", 0.0)),
            suggestions=list(map(str, data.get("suggestions", []))) or None,
        )


# Auto-register for document type 'research_paper'
register_agent("research_paper", CitationCheckAgent)
register_agent("research_paper", MethodologyAgent)


# -------------- Invoice Agents --------------

@dataclass
class TotalsValidatorAgent(Agent):
    name: str = "TotalsValidatorAgent"
    llm: LLMClient | None = None

    def analyze(self, document: Any) -> AgentReport:
        text = str(document)
        prompt = (
            "You are an invoice totals validator. Cross-check line items, quantities, unit prices, taxes, discounts,"
            " and compute subtotal, tax, and grand total. Identify mismatches and rounding issues."
            " Return strict JSON: summary, comments (array of discrepancies found), score (0-100 correctness),"
            " suggestions (array). No extra text.\n\n"
            "Invoice Text or JSON:\n" + text + "\n\nJSON_RESPONSE_START\n"
        )
        raw = self.llm.generate(prompt) if self.llm else "{}"
        try:
            import json

            data = json.loads(raw or "{}")
        except Exception:
            data = {}

        return AgentReport(
            name=self.name,
            summary=str(data.get("summary", "No summary produced.")),
            comments=list(map(str, data.get("comments", []))),
            score=float(data.get("score", 0.0)),
            suggestions=list(map(str, data.get("suggestions", []))) or None,
        )


# Auto-register for document type 'invoice'
register_agent("invoice", TotalsValidatorAgent)

