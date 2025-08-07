# Agent architecture base interfaces and registry
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, DefaultDict
from collections import defaultdict


@dataclass(slots=True)
class AgentReport:
    """Standardized output of an Agent analysis.

    Attributes:
        name: Name of the agent emitting the report.
        summary: One-paragraph high-level summary of the findings.
        comments: A list of detailed comments/observations.
        score: A numeric score (e.g., 0.0 - 1.0 or 0 - 100) representing quality/compliance.
        suggestions: Optional, actionable suggestions or next steps.
        metadata: Optional per-agent metadata, used by orchestrator for context.
    """

    name: str
    summary: str
    comments: List[str] = field(default_factory=list)
    score: float = 0.0
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class Agent(ABC):
    """Abstract base class for specialized analysis agents.

    Subclasses should implement `analyze` to process an input document and
    return an AgentReport.
    """

    name: str = "Agent"

    @abstractmethod
    def analyze(self, document: Any) -> AgentReport:
        """Analyze a document and return a structured report.

        Args:
            document: An object representing the document to analyze. The exact
                      structure depends on the document type and agent.
        Returns:
            AgentReport: The structured findings from the analysis.
        """
        raise NotImplementedError


# Registry: maps document type identifiers to lists of Agent classes
# Example keys might be: "markdown", "python", "json", etc.
_AgentRegistry: DefaultDict[str, List[Type[Agent]]] = defaultdict(list)


def register_agent(document_type: str, agent_cls: Type[Agent]) -> None:
    """Register an Agent class for a given document type.

    Args:
        document_type: Identifier of the document type this agent specializes in.
        agent_cls: The Agent subclass to register.
    """
    if not isinstance(document_type, str) or not document_type:
        raise ValueError("document_type must be a non-empty string")
    if not isinstance(agent_cls, type) or not issubclass(agent_cls, Agent):
        raise TypeError("agent_cls must be a subclass of Agent")

    # Avoid duplicate registration of the same class for the same type
    if agent_cls not in _AgentRegistry[document_type]:
        _AgentRegistry[document_type].append(agent_cls)


def get_registered_agents(document_type: str) -> List[Type[Agent]]:
    """Retrieve the list of Agent classes registered for a document type."""
    return list(_AgentRegistry.get(document_type, []))


def get_registry_snapshot() -> Dict[str, List[str]]:
    """Return a read-friendly snapshot of the registry.

    Returns:
        Dict mapping document type to list of agent class names.
    """
    return {dtype: [cls.__name__ for cls in classes] for dtype, classes in _AgentRegistry.items()}

