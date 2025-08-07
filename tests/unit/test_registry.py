import types

import pytest

from agentic.agents.base import Agent, register_agent, get_registered_agents, get_registry_snapshot


def test_register_and_get_agents_isolated(monkeypatch):
    # isolate registry by pointing name to a new default dict
    import agentic.agents.base as base

    monkeypatch.setattr(base, "_AgentRegistry", base.defaultdict(list))

    class A(Agent):
        name = "A"

        def analyze(self, document):  # pragma: no cover - not used
            raise NotImplementedError

    class B(Agent):
        name = "B"

        def analyze(self, document):  # pragma: no cover - not used
            raise NotImplementedError

    register_agent("contract", A)
    register_agent("contract", B)
    register_agent("invoice", B)

    assert [cls.__name__ for cls in get_registered_agents("contract")] == ["A", "B"]
    snap = get_registry_snapshot()
    assert set(snap.keys()) == {"contract", "invoice"}
    assert snap["invoice"] == ["B"]


def test_register_agent_validation(monkeypatch):
    import agentic.agents.base as base

    monkeypatch.setattr(base, "_AgentRegistry", base.defaultdict(list))

    with pytest.raises(ValueError):
        register_agent("", Agent)  # type: ignore[arg-type]

    class NotAgent:  # not subclass
        pass

    with pytest.raises(TypeError):
        register_agent("x", NotAgent)  # type: ignore[arg-type]
