# 🌐 Web Research Agents - Real-Time Fact Checking

## ✨ Nuova Funzionalità v3.1

Il sistema ora include **agenti con accesso a Internet in tempo reale** che possono:
- ✅ Verificare fatti e statistiche
- ✅ Controllare informazioni aggiornate per il 2025
- ✅ Validare citazioni e fonti
- ✅ Cercare dati di mercato attuali
- ✅ Fornire URL di fonti autorevoli

---

## 🎯 Come Funziona

Usa la **OpenAI Responses API** con il tool nativo `web_search`:
- **Non richiede API esterne** (tutto integrato in OpenAI)
- **Citazioni automatiche** tramite URL annotations
- **Multi-turn conversations** con contesto mantenuto
- **Completamente asincrono** e parallelo

---

## 🚀 Utilizzo

### Comando Base con Web Research

```bash
python3 generic_reviewer.py documento.pdf --enable-web-research
```

### Comando Completo (Tutte le Features)

```bash
python3 generic_reviewer.py documento.pdf \
    --enable-web-research \
    --enable-python-tools \
    --iterative \
    --max-iterations 3 \
    --output-language Italian
```

### GUI Mode con Web Research

```bash
# Lancia senza argomenti per GUI
python3 generic_reviewer.py

# Poi aggiungi --enable-web-research manualmente se vuoi
```

---

## 🤖 Due Nuovi Agenti

### 1. **Web Researcher** 🌐

**Scopo**: Ricerca e verifica informazioni online

**Cosa fa**:
- Cerca statistiche e dati di mercato aggiornati
- Verifica claim fattuali
- Trova fonti autorevoli
- Controlla informazioni tecniche
- Valida date e fatti storici

**Output**:
```
Claim: "Il mercato LED raggiungerà $100B nel 2025"
Status: ✅ VERIFIED
Finding: Secondo multiple fonti, il mercato LED globale è proiettato 
         a $105.8B nel 2025 (fonte: MarketsandMarkets)
Sources:
  1. https://www.marketsandmarkets.com/...
  2. https://www.grandviewresearch.com/...
```

### 2. **Fact Checker** ✓

**Scopo**: Validazione accuratezza documento

**Cosa fa**:
- Verifica TUTTI i claim verificabili
- Assegna stato: VERIFIED / PARTIALLY VERIFIED / UNVERIFIED / FALSE
- Fornisce correzioni con fonti
- Valuta qualità delle citazioni
- Dà confidence score (0-100%)

**Output**:
```
Summary: Overall accuracy: 85% (17/20 claims verified)

Verified Claims:
✅ Revenue growth 150% → Confirmed by company reports
✅ Market size $50M → Verified with industry data
...

Issues Found:
❌ "Top 3 in Europe" → Actually ranked #5 (source: Statista)
⚠️ "2024 data" → Data is from 2023, updated figures available
...

Confidence Score: 82/100
```

---

## 📋 Quando Vengono Usati

Gli agenti web research vengono **automaticamente selezionati** per:

### Business Documents
- Business proposals
- Market research
- Financial reports
- Investment pitch

→ Verifica dati di mercato, statistiche finanziarie, claim aziendali

### Technical Documents
- Technical specifications
- Product documentation
- Research papers
- Patents

→ Verifica specifiche tecniche, claim di performance, citazioni

### Marketing Materials
- White papers
- Case studies
- Press releases

→ Verifica claim di marketing, statistiche citate, comparazioni

---

## 🔧 Architettura Tecnica

### Responses API (non Chat Completions)

```python
from openai import OpenAI

client = OpenAI()

# Usa Responses API, non Chat Completions!
response = client.responses.create(
    model="gpt-4o",  # o "gpt-4.1", "o4-mini"
    input=[
        {"role": "system", "content": [{"type": "input_text", "text": prompt}]},
        {"role": "user", "content": [{"type": "input_text", "text": query}]}
    ],
    tools=[{"type": "web_search"}],  # ← Web search nativo!
)

# Estrai citazioni URL
msg = response.output[0]
text = msg.content[0].text
citations = [a.url for a in msg.content[0].annotations 
             if a.type == "url_citation"]
```

### File Coinvolti

```
web_research_agent.py          ← Core logic
  ├── WebResearchAgent         ← Classe principale
  ├── search()                 ← Single search
  ├── follow_up()              ← Multi-turn
  ├── verify_claim()           ← Fact checking
  └── execute_web_research_agent()  ← Integration helper

generic_reviewer.py
  ├── Import web_research_agent
  ├── Template "web_researcher"
  ├── Template "fact_checker"
  ├── create_agent() ← Web research handling
  └── _execute_agent_with_optional_tools() ← Execution
```

---

## 💡 Esempi di Output

### Esempio 1: Business Proposal

```
🌐 Web Researcher Report:

VERIFIED CLAIMS (8/10):
✅ "SaaS market growing 20% CAGR"
   Finding: Verified at 18-22% across multiple sources
   Sources: Gartner, IDC, Forrester
   
✅ "Competitor X has 30% market share"
   Finding: Confirmed by Q4 2024 earnings report
   Sources: Company investor relations, SeekingAlpha

UNVERIFIED CLAIMS (1/10):
❓ "Our solution is 50% faster"
   Finding: No independent benchmarks found
   Recommendation: Provide benchmark data or remove claim

FALSE CLAIMS (1/10):
❌ "We're the only provider in the region"
   Finding: Found 3 other providers (Company A, B, C)
   Correction: "We're among the leading providers"
   Sources: Industry directory, Crunchbase

RECOMMENDATION: Update 2 claims before presentation
```

### Esempio 2: Technical Specification

```
✓ Fact Checker Assessment:

Technical Claims Verified:
✅ "Supports OAuth 2.0" → Confirmed in official docs
✅ "99.9% uptime SLA" → Verified in service agreement
✅ "GDPR compliant" → Certification found

Data Points Verified:
✅ "10,000 requests/sec" → Matches benchmark results
⚠️ "Sub-100ms latency" → Achievable but environment-dependent

Outdated Information:
❌ "Latest version: 2.5" → Current version is 3.1 (Jan 2025)
   Update recommendation: Specify version 3.1

Confidence Score: 88/100

Sources (12 URLs provided)
```

---

## ⚙️ Configurazione

### Modelli Supportati

```python
# In order of preference:
"gpt-4o"      # ← Raccomandato (bilanciato)
"gpt-4.1"     # High-end
"o4-mini"     # Budget-friendly
```

### Requisiti

```bash
# Libreria OpenAI (già installata)
pip install openai>=1.0.0

# Nessuna API esterna richiesta!
# web_search è nativo nella Responses API
```

### Variabili Ambiente

```bash
# Solo OpenAI API key (già configurata)
export OPENAI_API_KEY="sk-..."

# Nessuna configurazione aggiuntiva necessaria!
```

---

## 🎛️ Opzioni Avanzate

### Specificare Agenti Manualmente

Se vuoi forzare l'uso di web research anche per documenti che normalmente non lo avrebbero:

```python
# Nel codice (per sviluppatori):
document_type.suggested_agents.append("web_researcher")
document_type.suggested_agents.append("fact_checker")
```

### Combinare con Python Tools

```bash
python3 generic_reviewer.py documento.pdf \
    --enable-web-research \
    --enable-python-tools

# Web Researcher: verifica claim online
# Data Validator: esegue calcoli Python
# → Copertura completa: web + math!
```

### Debug Web Search

```bash
python3 generic_reviewer.py documento.pdf \
    --enable-web-research \
    --log-level DEBUG

# Vedrai:
# DEBUG - 🌐 Executing Web_Researcher with WEB SEARCH
# DEBUG - Raw response: {"text": "...", "citations": [...]}
# DEBUG - Found 5 URL citations
```

---

## 📊 Output nei Report

### JSON Report

```json
{
  "reviews": {
    "Web_Researcher": {
      "content": "...report text...",
      "citations": [
        "https://source1.com/...",
        "https://source2.com/..."
      ],
      "verified_claims": 15,
      "false_claims": 2
    },
    "Fact_Checker": {
      "content": "...report text...",
      "confidence_score": 85,
      "sources_count": 18
    }
  }
}
```

### Markdown Report

```markdown
## 🌐 Web Research Findings

### Verified Claims
- **Claim 1**: Market size $100M
  - ✅ Status: VERIFIED
  - 📚 Source: https://...

### Issues Found
- **Claim 5**: "Top provider globally"
  - ❌ Status: FALSE
  - 📚 Correction: Regional top 5, not global
  - 🔗 Sources: [1](https://...), [2](https://...)
```

### HTML Dashboard

Il dashboard include sezione dedicata con:
- 📊 Grafico verifiche (verified/unverified/false)
- 🔗 Lista cliccabile di tutte le fonti
- ⚠️ Highlight dei claim problematici

---

## 🚨 Limitazioni Note

### 1. **Rate Limits**
- La Responses API ha rate limits standard OpenAI
- Per documenti grandi, potrebbero volerci più chiamate
- **Soluzione**: Il sistema gestisce automaticamente con retry

### 2. **Qualità Fonti**
- Il modello cerca fonti autorevoli ma non è infallibile
- **Raccomandazione**: Verifica manualmente le citazioni critiche

### 3. **Costo**
- Web search usa token aggiuntivi (ricerca + risultati)
- **Stima**: +30-50% token rispetto a review standard
- **Mitigazione**: Usa `--enable-web-research` solo quando serve

### 4. **Tempo Esecuzione**
- Ricerche web aggiungono latenza (2-5 sec per claim)
- **Totale**: +30-60 secondi per documento con 10-20 claim
- **Benefit**: Accuracy aumenta significativamente

---

## 🎯 Best Practices

### ✅ DO

```bash
# ✅ Usa per business documents con claim verificabili
python3 generic_reviewer.py pitch.pdf --enable-web-research

# ✅ Combina con iterative per miglioramenti basati su dati reali
python3 generic_reviewer.py report.pdf \
    --enable-web-research \
    --iterative \
    --max-iterations 3

# ✅ Usa per aggiornare documenti con dati vecchi
python3 generic_reviewer.py whitepaper_2023.pdf \
    --enable-web-research \
    --interactive
```

### ❌ DON'T

```bash
# ❌ Non usare per opinioni o contenuti creativi
python3 generic_reviewer.py essay.txt --enable-web-research
# (Non c'è nulla da verificare online)

# ❌ Non usare per documenti interni confidenziali
python3 generic_reviewer.py internal_strategy.pdf --enable-web-research
# (Le info potrebbero non essere pubbliche)

# ❌ Non aspettarti verifiche di contenuti recenti (ultimi giorni)
# (Web search ha qualche giorno di lag)
```

---

## 🧪 Test Rapido

```bash
# 1. Crea documento di test
cat > test_claims.txt << 'EOF'
Market Analysis

The global LED market reached $75 billion in 2024.
Apple Inc. is headquartered in Cupertino, California.
The Earth has 3 moons.
Python was first released in 1991.
EOF

# 2. Esegui review con web search
python3 generic_reviewer.py test_claims.txt --enable-web-research

# 3. Controlla l'output
# Dovrebbe verificare:
# ✅ LED market (con fonti)
# ✅ Apple HQ (verificato)
# ❌ 3 moons (FALSE - ha 1 luna!)
# ✅ Python 1991 (verificato)
```

---

## 🔮 Prossimi Sviluppi

### In Roadmap

- [ ] **Domain Filtering**: Limitare ricerche a domini specifici
- [ ] **Citation Quality Score**: Valutare autorevolezza fonti
- [ ] **Historical Data**: Confronto claim con dati storici
- [ ] **Fact Cache**: Cache locale per claim già verificati
- [ ] **Source Diversity**: Assicurare fonti multiple indipendenti

### Sperimentale

```python
# Code Interpreter + Web Search combo
tools=[
    {"type": "web_search"},
    {"type": "code_interpreter"}
]

# Agent può:
# 1. Cercare dati online
# 2. Analizzarli con Python
# 3. Generare grafici
# 4. Fornire report completo
```

---

## 📚 Risorse

- [OpenAI Responses API Docs](https://platform.openai.com/docs/api-reference/responses)
- [Web Search Tool Guide](https://platform.openai.com/docs/guides/web-search)
- [Cookbook Examples](https://cookbook.openai.com)

---

## ✅ Checklist Implementazione

```
✅ web_research_agent.py creato
✅ WebResearchAgent class implementata
✅ Integration in generic_reviewer.py
✅ Template web_researcher aggiunto
✅ Template fact_checker aggiunto
✅ CLI argument --enable-web-research
✅ Execution logic in _execute_agent_with_optional_tools
✅ Graceful degradation se non disponibile
✅ Error handling completo
✅ Logging dettagliato
✅ Documentazione completa
```

---

## 🎉 Quick Start

```bash
# 1. Attiva web research per il tuo documento
python3 generic_reviewer.py documento_aziendale.pdf --enable-web-research

# 2. Aspetta la review (potrebbe richiedere 1-2 min)

# 3. Controlla l'output:
cd documento_aziendale_YYYYMMDD_HHMMSS/
cat review_report.md  # Cerca sezione "Web Researcher"

# 4. Verifica le fonti
grep "http" review_report.md  # Lista tutte le URL
```

**Fatto! Il tuo documento è stato verificato con fonti in tempo reale!** ✅

---

## 💬 Support

Problemi? Controlla:
1. ✅ OpenAI API key configurata?
2. ✅ Libreria `openai` aggiornata? (`pip install --upgrade openai`)
3. ✅ Argomento `--enable-web-research` passato?
4. ✅ Log per errori? (`--log-level DEBUG`)

**Enjoy real-time fact-checking!** 🌐✨

