# 🤖 AI Document Reviewer - Sistema di Revisione Documenti con Intelligenza Artificiale

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-green.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Panoramica

Sistema avanzato di revisione documenti alimentato da IA che utilizza un team di agenti specializzati AI (GPT-5, GPT-5-mini, GPT-5-nano) per analizzare qualsiasi tipo di documento e fornire feedback professionale.

**🚀 Prova la Demo Live**: [Web UI](http://localhost:7860) (dopo l'installazione)

## 🎯 Caratteristiche Principali

### 🌟 Core Features
- 📄 **Analisi Multi-Documento**: Supporta PDF, Word, Markdown, TXT
- 🤖 **30+ Agenti Specializzati**: Sistema multi-agente con esperti di dominio
- 🌍 **Multi-Lingua**: Rilevamento automatico lingua + output personalizzato
- ✨ **Miglioramento Iterativo**: Raffinazione automatica del documento
- 🔍 **Ricerca Web & Accademica**: Fact-checking e ricerca letteratura (Semantic Scholar)
- 📊 **Dashboard Interattiva**: Visualizzazione risultati con grafici

### 🎨 Interfaccia Web Moderna
- 💻 **Gradio Web UI**: Interfaccia drag-and-drop user-friendly
- 📈 **Progress Tracking**: Barre di progresso real-time
- 📥 **Download Reports**: Markdown, JSON, HTML
- 🎯 **3-Tier System**: Core, Document-Specific, Deep-Dive specialists

### 🔧 Features Avanzate
- 🐍 **Esecuzione Python**: Validazione calcoli e dati
- 💬 **Modalità Interattiva**: Agenti richiedono info aggiuntive
- 📚 **Reference Context**: Template, linee guida, esempi
- 🗄️ **Database Tracking**: SQLite per storico versioni
- ⏸️ **Pause/Resume**: Checkpoint-based system
- 📦 **Batch Processing**: Analisi parallela multipli documenti

## 🚀 Quick Start

### Prerequisiti
- Python 3.9 o superiore
- OpenAI API Key (GPT-5)

### Installazione

```bash
# Clone del repository
git clone https://github.com/albertogerli/agentic_reviewer.git
cd agentic_reviewer

# Installa dipendenze base
pip install openai pyyaml python-dotenv

# Installa dipendenze web UI (opzionale)
pip install -r requirements_web.txt

# Installa dipendenze avanzate (opzionale)
pip install -r requirements_optional.txt
pip install -r requirements_academic.txt
pip install -r requirements_tavily.txt
```

### Configurazione

```bash
# Crea file .env
echo "OPENAI_API_KEY=your-api-key-here" > .env

# (Opzionale) Crea config.yaml personalizzato
cp config_example.yaml config.yaml
# Modifica config.yaml con le tue impostazioni
```

### 🖥️ Avvio Web UI (Raccomandato)

```bash
python web_ui.py
```

Apri il browser su: `http://localhost:7860`

### 📝 Uso da CLI

```bash
# Analisi standard
python generic_reviewer.py document.pdf --output-language Italian

# Modalità iterativa (auto-miglioramento)
python generic_reviewer.py document.pdf --iterative --max-iterations 5

# Deep review (Tier 3 agents)
python generic_reviewer.py document.pdf --deep-review

# Con ricerca web
python generic_reviewer.py document.pdf --enable-web-research

# Batch processing
python generic_reviewer.py --batch-dir ./documents --parallel

# Modalità interattiva
python generic_reviewer.py document.pdf --interactive
```

## 📊 Struttura del Sistema

### Modelli AI (3-Tier System)

| Tier | Modello | Complessità | Uso |
|------|---------|-------------|-----|
| 🔥 **Tier 1** | GPT-5 | Alta (>0.80) | Core analysis, sintesi |
| ⚡ **Tier 2** | GPT-5-mini | Media (0.60-0.80) | Document-specific |
| 🚀 **Tier 3** | GPT-5-nano | Bassa (<0.60) | Task semplici |

### 🤖 Agenti Disponibili (50+)

**Core Agents (Sempre attivi)**:
- Style Editor, Consistency Checker, Fact Checker
- Logic Checker, Technical Expert

**Document-Specific Agents**:
- Academic Reviewer, Business Analyst, Legal Expert
- Technical Writer, Data Scientist, SEO Specialist
- ...e molti altri

**Deep-Dive Specialists (Tier 3)**:
- Peer Review Simulator, Literature Review Expert
- Grant Proposal Reviewer, Market Intelligence
- GDPR Compliance, API Documentation Reviewer
- Academic Researcher (con Semantic Scholar)
- ...e molti altri

## 📁 Struttura Output

```
output_[document]_[timestamp]/
├── review_report.md           # Report completo in Markdown
├── review_results.json        # Risultati strutturati
├── dashboard.html             # Dashboard interattiva
├── version_1/                 # (se iterativo)
│   ├── document_v1.txt
│   └── iteration_1_results.json
└── best_version/
    └── document_best.txt
```

## 🎓 Esempi d'Uso

### Web UI

1. Carica documento (drag & drop)
2. Seleziona lingua output
3. (Opzionale) Abilita features avanzate:
   - ✨ Auto-Improve (iterativo)
   - 🔬 Deep Analysis (Tier 3)
   - 🌐 Web Research
   - 💬 Interactive Mode
4. Clicca "Analyze My Document"
5. Scarica reports generati

### Python API

```python
from generic_reviewer import GenericReviewOrchestrator, Config

# Configura sistema
config = Config()
config.model_powerful = "gpt-5"
config.model_standard = "gpt-5-mini"
config.model_basic = "gpt-5-nano"

# Crea orchestratore
orchestrator = GenericReviewOrchestrator(
    config=config,
    output_language="Italian",
    deep_review=True,
    enable_web_research=True
)

# Esegui review
results = await orchestrator.execute_review_process(
    document_text="...",
    output_dir="./output"
)

print(f"Score: {results['final_score']}")
```

## 🔧 Configurazione Avanzata

### config.yaml

```yaml
models:
  powerful: gpt-5
  standard: gpt-5-mini
  basic: gpt-5-nano

review:
  max_concurrent_agents: 5
  timeout_per_agent: 120

iterative:
  max_iterations: 5
  target_score: 85

output:
  format: ["markdown", "json", "html"]
  include_agent_reasoning: true
```

### Variabili d'Ambiente

```bash
OPENAI_API_KEY=sk-...           # Obbligatorio
TAVILY_API_KEY=tvly-...         # Opzionale (web search)
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
```

## 📚 Documentazione

- [Quick Start Guide](QUICK_START.md)
- [Sistema 3-Tier](SISTEMA_3_TIER.md)
- [Modalità Iterativa](MODALITA_ITERATIVA_README.md)
- [Web Research](WEB_RESEARCH_README.md)
- [Academic Search](ACADEMIC_SEARCH_README.md)
- [Agent Tools](AGENT_TOOLS_README.md)
- [Funzionalità Avanzate](FUNZIONALITA_AVANZATE.md)

## 🧪 Testing

```bash
# Test moduli individuali
python test_agent_tools.py
python test_web_search.py
python test_academic_search.py

# Demo senza API key
python demo_generic_reviewer.py
```

## 📈 Performance

- **Analisi Standard**: 3-5 minuti
- **Deep Review**: 8-15 minuti
- **Iterative (5 iterations)**: 15-30 minuti
- **Batch (10 docs)**: 20-40 minuti (parallelo)

## 🤝 Contributi

Contributi benvenuti! Per favore:
1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📝 License

Questo progetto è rilasciato sotto licenza MIT. Vedi [LICENSE](LICENSE) per dettagli.

## 🙏 Riconoscimenti

- **OpenAI** per i modelli GPT-5
- **Semantic Scholar** per l'API di ricerca accademica
- **Gradio** per il framework Web UI
- **Tavily** per il web search API

## 📧 Contatti

**Alberto Giovanni Gerli**
- GitHub: [@albertogerli](https://github.com/albertogerli)
- Email: alberto@albertogerli.it

## 🔗 Links Utili

- [Documentazione Completa](./PROJECT_SUMMARY.md)
- [Changelog](./NOVITA_SISTEMA.md)
- [Examples](./examples/)
- [Troubleshooting](./WEB_SEARCH_SETUP.md)

---

**⭐ Se questo progetto ti è utile, lascia una stella su GitHub!**

Realizzato con ❤️ e 🤖 AI

