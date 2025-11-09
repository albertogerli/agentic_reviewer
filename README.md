# 🤖 AI Document Reviewer - Sistema di Revisione Documenti con Intelligenza Artificiale

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-green.svg)](https://openai.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Panoramica

Sistema avanzato di revisione documenti alimentato da IA che utilizza un team di agenti specializzati AI (GPT-5, GPT-5-mini, GPT-5-nano) per analizzare qualsiasi tipo di documento e fornire feedback professionale con **aggiornamenti in tempo reale**.

**🚀 Due Interfacce Disponibili**:
- 🎨 **React UI Modern** (Raccomandato): http://localhost:3000
- 💻 **Gradio Web UI** (Alternativa): http://localhost:7860

## 🎯 Caratteristiche Principali

### 🌟 Core Features
- 📄 **Analisi Multi-Documento**: Supporta PDF, Word, Markdown, TXT
- 🤖 **50+ Agenti Specializzati**: Sistema multi-agente con esperti di dominio
- 🌍 **Multi-Lingua**: Rilevamento automatico lingua + output personalizzato
- ✨ **Miglioramento Iterativo**: Raffinazione automatica del documento
- 🔍 **Ricerca Web & Accademica**: Fact-checking e ricerca letteratura (Semantic Scholar)
- 📊 **Dashboard Interattiva**: Visualizzazione risultati con grafici

### 🎨 Interfaccia React Modern (NEW!)
- ⚡ **WebSocket Real-Time**: Aggiornamenti live mentre gli agenti lavorano
- 🎬 **Live Progress**: Vedi ogni agente che analizza in tempo reale
- 📊 **Three-Panel Layout**: Issues, Document Viewer, Evidence Panel
- 🗺️ **Risk Heatmap**: Visualizzazione rischi per categoria
- ✏️ **Redline Editor**: Modifica proposte con accept/reject
- 📈 **Analytics & History**: Tracciamento performance e trend
- 🎯 **Evidence-First UI**: Focus su problemi con severity/confidence

### 🔧 Features Avanzate
- 🐍 **Esecuzione Python**: Validazione calcoli e dati (sandbox sicuro)
- 💬 **Modalità Interattiva**: Agenti richiedono info aggiuntive
- 📚 **Reference Context**: Template, linee guida, esempi
- 🗄️ **Database Tracking**: SQLite per storico versioni
- ⏸️ **Pause/Resume**: Checkpoint-based system
- 📦 **Batch Processing**: Analisi parallela multipli documenti
- 🌐 **Web Search Integrato**: Citazioni automatiche con fonti

## 🚀 Quick Start

### Prerequisiti
- Python 3.9 o superiore
- Node.js 18+ (per React UI)
- OpenAI API Key (GPT-5)

### Installazione

```bash
# Clone del repository
git clone https://github.com/albertogerli/agentic_reviewer.git
cd agentic_reviewer

# Installa dipendenze Python
pip install openai pyyaml python-dotenv fastapi uvicorn python-multipart

# Installa dipendenze web UI (Gradio - opzionale)
pip install -r requirements_web.txt

# Installa dipendenze avanzate (opzionale)
pip install -r requirements_optional.txt
pip install -r requirements_academic.txt
pip install -r requirements_tavily.txt

# Installa dipendenze React UI (raccomandato)
cd frontend
npm install
cd ..
```

### Configurazione

```bash
# Crea file config.yaml
cp config_example.yaml config.yaml

# Modifica config.yaml con la tua API key
# api_key: "sk-your-openai-api-key-here"
```

### 🎨 Avvio React UI + Backend (Raccomandato)

**Terminale 1 - Backend FastAPI**:
```bash
python backend/app.py
```

**Terminale 2 - Frontend React**:
```bash
cd frontend
npm run dev
```

Apri il browser su: **http://localhost:3000** 🎉

### 🖥️ Avvio Gradio UI (Alternativa)

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

## 📊 Architettura del Sistema

### Stack Tecnologico

**Backend**:
- 🐍 **FastAPI**: REST API + WebSocket
- 🔄 **Asyncio**: Esecuzione parallela agenti
- 📊 **SQLite**: Database storico versioni
- 🌐 **OpenAI Responses API**: Web search integrato

**Frontend**:
- ⚛️ **React 18** + **Next.js 14**: Framework moderno
- 🎨 **Tailwind CSS**: Styling responsive
- 📊 **Recharts**: Visualizzazioni dati
- 🔄 **Zustand**: State management
- ⚡ **WebSocket**: Real-time updates

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
- Financial Analyst, Risk Assessor, Content Strategist
- ...e molti altri

**Deep-Dive Specialists (Tier 3)**:
- Peer Review Simulator, Literature Review Expert
- Grant Proposal Reviewer, Market Intelligence
- GDPR Compliance, Contract Clause Analyzer
- API Documentation Reviewer, Academic Researcher
- Sustainability Assessor, Crisis Communication
- ...e molti altri

**Web Research Agents**:
- 🌐 **Web Researcher**: Ricerca generale con citazioni
- ✅ **Fact Checker**: Verifica affermazioni specifiche

## 📁 Struttura Output

```
outputs/[document]_[timestamp]/
├── review_report.md           # Report completo in Markdown
├── review_results.json        # Risultati strutturati con issues/changes
├── dashboard.html             # Dashboard interattiva
├── individual_reviews/        # Review di ogni agente
│   ├── style_editor.txt
│   ├── fact_checker.txt
│   └── ...
├── version_1/                 # (se iterativo)
│   ├── document_v1.txt
│   └── iteration_1_results.json
└── best_version/
    └── document_best.txt
```

## 🎓 Guida Uso React UI

### 1️⃣ Upload Documento
- Drag & drop o click per selezionare
- Supporta: PDF, DOCX, TXT, MD

### 2️⃣ Configurazione
- **Output Language**: Scegli lingua review
- **Iterative Mode**: Auto-miglioramento (max iterations, target score)
- **Deep Analysis**: Abilita Tier 3 specialists
- **Web Research**: Fact-checking online
- **Interactive**: Agenti chiedono info aggiuntive
- **Python Tools**: Validazione numerica
- **Reference Documents**: Upload template/linee guida

### 3️⃣ Live Analysis
Vedi in tempo reale:
```
🤖 Deploying 12 AI agents...
✍️ Style Editor analyzing...
✅ Style Editor completed (1/12)
🔍 Fact Checker analyzing...
✅ Fact Checker completed (2/12)
...
```

### 4️⃣ Risultati
**Tab Summary**:
- Overall Score
- Total Issues/Suggestions
- Document Type & Title

**Tab Evidence Explorer**:
- 📊 Risk Heatmap (per categoria)
- 🎯 Three-Panel Layout:
  - Issues List (filtrabili per severity/category)
  - Document Viewer (con highlight)
  - Evidence Panel (dettagli issue selezionato)

**Tab Redline Editor**:
- Lista modifiche proposte (delete/insert/replace)
- Accept/Reject individuale o batch
- Generate Revised Document

**Tab Agent Reports**:
- Review dettagliata di ogni agente
- Icons e badges per tipo agent

**Tab Raw Data**:
- JSON completo con tutti i dati
- Copy to clipboard

**Tab Analytics** (da menu):
- Review History
- Score Trends (grafico)
- Agent Performance
- Document Comparison

## 🔧 Configurazione Avanzata

### config.yaml

```yaml
api_key: "sk-your-openai-api-key"

models:
  powerful: gpt-5
  standard: gpt-5-mini
  basic: gpt-5-nano

output_dir: "./outputs"

tavily_api_key: ""  # Opzionale per web search fallback
```

### Backend API Endpoints

```
GET  /                          # Health check
POST /api/review/upload         # Upload documento + config
POST /api/review/{review_id}/start  # Avvia analisi
GET  /api/review/{review_id}/status # Status analisi
GET  /api/review/{review_id}/results # Risultati
GET  /api/review/{review_id}/download/{file_type} # Download file
WS   /ws                        # WebSocket real-time updates
GET  /api/analytics/history     # Storico review
GET  /api/analytics/trends      # Trend score
GET  /api/analytics/comparison  # Confronto versioni
GET  /api/analytics/agents-performance # Performance agenti
POST /api/review/{review_id}/apply-changes # Applica modifiche
```

### Variabili d'Ambiente

```bash
OPENAI_API_KEY=sk-...           # Obbligatorio
TAVILY_API_KEY=tvly-...         # Opzionale (web search fallback)
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
```

## 🎬 Demo Video

1. **Upload**: Drag & drop documento
2. **Configure**: Seleziona opzioni (Deep Analysis, Web Research)
3. **Live Progress**: Vedi ogni agente lavorare in tempo reale
4. **Explore Results**: Three-panel layout con issues evidenziate
5. **Edit**: Accept/Reject modifiche proposte
6. **Download**: Report MD/JSON/HTML

## 📚 Documentazione

### Guide Principali
- [Quick Start Guide](QUICK_START.md)
- [Sistema 3-Tier](SISTEMA_3_TIER.md)
- [Modalità Iterativa](MODALITA_ITERATIVA_README.md)
- [Web Research](WEB_RESEARCH_README.md)
- [Academic Search](ACADEMIC_SEARCH_README.md)
- [Agent Tools](AGENT_TOOLS_README.md)
- [Funzionalità Avanzate](FUNZIONALITA_AVANZATE.md)

### Setup & Troubleshooting
- [React UI Setup](REACT_SETUP.md)
- [Web Search Setup](WEB_SEARCH_SETUP.md)
- [Troubleshooting](QUICK_FIX_GUIDE.md)

### Changelog
- [UI Improvements](RIEPILOGO_MIGLIORAMENTI_UI.md)
- [Web Search Fixes](WEB_SEARCH_CITATIONS_FIX.md)
- [React Migration](REACT_MIGRATION_COMPLETE.md)

## 🧪 Testing

```bash
# Test moduli individuali
python test_agent_tools.py
python test_web_search.py
python test_academic_search.py
python test_web_search_citations.py

# Test backend API
bash test_backend.sh

# Demo senza API key
python demo_generic_reviewer.py
```

## 📈 Performance

| Modalità | Tempo | Agenti | Note |
|----------|-------|--------|------|
| **Analisi Standard** | 3-5 min | 8-12 | Core + Document-specific |
| **Deep Review** | 8-15 min | 15-20 | + Tier 3 specialists |
| **Iterative (5 iterations)** | 15-30 min | 8-12/iter | Auto-improvement loop |
| **Batch (10 docs)** | 20-40 min | - | Parallel processing |
| **Web Research** | +30-60s/agent | 2 | Fact checking online |

### Costi Stimati (OpenAI)

| Review Type | Tokens (avg) | Cost (GPT-5) |
|-------------|--------------|--------------|
| Standard | 50K-100K | $0.25-$0.50 |
| Deep | 150K-250K | $0.75-$1.25 |
| Iterative (3x) | 150K-300K | $0.75-$1.50 |

*Nota: Usa GPT-5-mini/nano per ridurre costi (threshold configurable)*

## 🐛 Troubleshooting

### Backend non parte
```bash
# Verifica porta 8000 libera
lsof -ti:8000 | xargs kill -9

# Riavvia
python backend/app.py
```

### Frontend non compila
```bash
# Pulisci e reinstalla
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### WebSocket non funziona
- Verifica backend sia attivo su porta 8000
- Controlla browser console per errori WebSocket
- Prova a ricaricare la pagina

### Agenti non completano
- Controlla `backend.log` per errori API
- Verifica API key valida in `config.yaml`
- Aumenta timeout se documento molto lungo

## 🤝 Contributi

Contributi benvenuti! Per favore:
1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

### Development Setup

```bash
# Backend
pip install -r requirements_dev.txt

# Frontend
cd frontend
npm install --include=dev

# Pre-commit hooks
pre-commit install
```

## 📝 License

Questo progetto è rilasciato sotto licenza MIT. Vedi [LICENSE](LICENSE) per dettagli.

## 🙏 Riconoscimenti

- **OpenAI** per i modelli GPT-5 e Responses API
- **Semantic Scholar** per l'API di ricerca accademica
- **Gradio** per il framework Web UI
- **Tavily** per il web search API fallback
- **Vercel** per Next.js framework
- **Tailwind CSS** per lo styling moderno

## 📧 Contatti

**Alberto Giovanni Gerli**
- GitHub: [@albertogerli](https://github.com/albertogerli)
- Email: alberto@albertogerli.it
- Repository: [agentic_reviewer](https://github.com/albertogerli/agentic_reviewer)

## 🔗 Links Utili

- [Demo Live](http://localhost:3000) (dopo setup)
- [Documentazione Completa](./PROJECT_SUMMARY.md)
- [Examples](./examples/)
- [Issues](https://github.com/albertogerli/agentic_reviewer/issues)
- [Discussions](https://github.com/albertogerli/agentic_reviewer/discussions)

## 🌟 Features Roadmap

- [ ] PDF Annotation Editor integrato
- [ ] Multi-user collaboration
- [ ] Cloud deployment (Docker + K8s)
- [ ] Mobile app (React Native)
- [ ] Plugin per Word/Google Docs
- [ ] API pubblica con rate limiting
- [ ] Template marketplace
- [ ] AI model fine-tuning

---

**⭐ Se questo progetto ti è utile, lascia una stella su GitHub!**

**Made with ❤️ and 🤖 AI** | Powered by GPT-5, React, FastAPI

*Last updated: November 2025*
