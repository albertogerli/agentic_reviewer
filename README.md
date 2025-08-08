# Agentic

Agentic document analysis system with an orchestrator that coordinates specialist agents. Includes ingestion utilities, document classification, agent registry, orchestrator with peer feedback, and a CLI with HTML report rendering.

- Status: alpha (0.1.0)
- Python: >= 3.10

## Installation

- Editable install for local development:
  - pip install -e .

- Optional tools:
  - pip install -r requirements.txt

- Environment variables (optional for real LLMs):
  - export OPENAI_API_KEY={{OPENAI_API_KEY}}

## CLI Usage

After installing (-e recommended), the command `agentic` is available.

- One-shot analysis:
  - agentic analyze path/to/file --open-browser --verbose

- Iterative loop (default 5 iterations):
  - agentic loop path/to/file --max 5 --open-browser --verbose

### Model selection and tiering
- Tier set: { gpt-5 (max), gpt-5-mini, gpt-5-nano (min) }
- If you do NOT pass --model (no cap):
  - Ogni agente riceve un tier assegnato dinamicamente dall’orchestrator in base alla complessità del documento e agli "agent-hints" (vedi sotto).
  - Il classificatore usa per default gpt-5-mini (o gpt-5-nano se necessario).
- Se passi --model come cap globale (uno tra gpt-5, gpt-5-mini, gpt-5-nano):
  - Nessun agente potrà superare quel tier (es. cap=gpt-5-mini declassa gpt-5 → gpt-5-mini).
- Se OPENAI_API_KEY non è impostata o il client non si inizializza, il sistema usa stub locali (nessuna chiamata API).

#### Agent tier hints
Gli agenti possono dichiarare suggerimenti a livello di classe per influenzare il tier minimo/preferito:

- Inherit da agentic.agents.base.Agent e opzionalmente impostare:
  - min_tier: il tier minimo accettabile (gpt-5-nano | gpt-5-mini | gpt-5)
  - preferred_tier: il tier preferito (stessa scelta)

Esempio:

- class LegalComplianceAgent(Agent):
    min_tier = "gpt-5-mini"
    preferred_tier = "gpt-5"

L’orchestrator segue l’ordine di decisione:
1) Calcola una score di complessità [0,1] su euristiche (lunghezza, cifre, marker di sezione, ricchezza vocabolario) e propone un base_tier.
2) Applica i hints dell’agente per portare il tier almeno a min_tier e, se possibile, fino al preferred_tier.
3) Applica il cap globale se fornito via --model.

Examples:
- OPENAI_API_KEY={{OPENAI_API_KEY}} agentic analyze examples/contract.txt --verbose
- OPENAI_API_KEY={{OPENAI_API_KEY}} agentic analyze examples/contract.txt --model gpt-4o
- OPENAI_API_KEY={{OPENAI_API_KEY}} agentic analyze examples/contract.txt --model gpt-5-mini

## Python API (outline)

- from agentic.orchestrator import Orchestrator
- from agentic.utils.classifier import DocumentClassifier
- from agentic.utils.ingest import ingest

Example outline:
- doc = ingest(path="examples/contract.txt")
- orch = Orchestrator(...)
- report = await orch.analyze(doc.text)

## Architecture

```mermaid
flowchart TD
  subgraph Client
    U[User / App]
  end

  subgraph Core
    O[Orchestrator]
    A1[Agents]
    UTI[Utils]
  end

  subgraph Integrations
    OAI[OpenAI]
  end

  U -->|requests| O
  O -->|delegates| A1
  A1 -->|helpers| UTI
  O --> OAI
```

- Orchestrator: central coordinator for workflows (classification → agents → feedback → synthesis)
- Agents: specialized workers per document type
- Utils: ingestion, classification, LLM adapters, HTML report rendering

## Development

- Code style
  - Ruff and Black via pyproject.toml (line length 100)

- Testing
  - pytest -q

## Packaging

- Build a wheel and sdist
  - python -m build

- Editable install (recommended for local dev)
  - pip install -e .

## Versioning and Releases

- Semantic versioning; current version in pyproject.toml
- Tagging a release
  - git tag -a v0.1.0 -m "Release v0.1.0"
  - git push origin v0.1.0

See CHANGELOG.md for release notes.

## Contributing

- Branching
  - git checkout -b feat/short-description

- Commit conventions
  - Conventional commits when possible (feat:, fix:, docs:, refactor:, test:, chore:)

- Pull requests
  - Include tests; update documentation
  - Ensure lint and tests pass locally

## License

- See LICENSE (if present) or specify your chosen license.

