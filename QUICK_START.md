# Quick Start Guide 🚀

## Hai ora DUE sistemi di review potenti!

---

## 1️⃣ Paper Reviewer (Articoli Scientifici)

### Quando usarlo
✅ Paper di ricerca scientifica  
✅ Articoli accademici  
✅ Tesi e dissertazioni  

### Come usarlo
```bash
python3 main.py tuo_paper.pdf
```

### Cosa ottieni
- 🔬 Review Metodologia
- 📊 Analisi Risultati
- 📚 Contesto Letteratura
- ✍️ Struttura e Chiarezza
- 💡 Impatto e Innovazione
- 🔍 Checker Contraddizioni
- ⚖️ Etica e Integrità
- 🤖 Detector AI
- 🚨 Detector Allucinazioni
- 🎯 Coordinatore
- ✅ Decisione Editoriale

---

## 2️⃣ Generic Reviewer (Qualsiasi Documento)

### Quando usarlo
✅ Business plan e proposte  
✅ Contratti e documenti legali  
✅ Documentazione tecnica  
✅ Contenuti marketing  
✅ Articoli e blog  
✅ Report finanziari  
✅ **Qualsiasi altro documento!**

### Come usarlo
```bash
python3 generic_reviewer.py tuo_documento.pdf
```

### Cosa fa
1. **Classifica automaticamente** il tipo di documento
2. **Crea dinamicamente** 5-10 agenti specializzati appropriati
3. **Esegue review completa** con esperti del settore
4. **Genera report** dettagliati e dashboard interattiva

### Esempio con Business Proposal
```bash
python3 generic_reviewer.py business_plan.pdf --title "Piano Strategico Q4"
```

**Agenti auto-selezionati:**
- 💼 Business Analyst
- 💰 Financial Analyst
- ⚠️ Risk Assessor
- 🏆 Competitor Analyst
- 💡 Impact Assessor
- 🔍 Fact Checker

---

## Demo Mode (Senza API Key)

Vuoi vedere come funziona senza spendere?

```bash
python3 demo_generic_reviewer.py example_business_proposal.txt
```

Mostra:
- Come viene classificato il documento
- Quali agenti vengono selezionati
- Struttura output attesa

---

## Setup Veloce

### 1. Installa dipendenze
```bash
pip install -r requirements.txt
```

### 2. Configura API Key
```bash
export OPENAI_API_KEY='tua-api-key-qui'
```

### 3. Esegui review!
```bash
# Paper scientifico
python3 main.py paper.pdf

# Qualsiasi altro documento
python3 generic_reviewer.py documento.pdf
```

---

## Tipi di Documento Supportati dal Generic Reviewer

| Tipo | Esempi | Agenti Tipici |
|------|--------|---------------|
| 📊 **Business** | Piani, proposte, report | Business Analyst, Financial Analyst, Risk Assessor |
| ⚖️ **Legal** | Contratti, accordi, policy | Legal Expert, Risk Assessor, Ethics Reviewer |
| ⚙️ **Technical** | Docs, API, manuali | Technical Expert, Security Analyst, UX Expert |
| 🎯 **Marketing** | Campagne, strategie, content | Content Strategist, SEO Specialist, UX Expert |
| 🔬 **Scientific** | Papers, research | Methodology Expert, Data Analyst, Fact Checker |
| 📝 **Content** | Blog, articoli, essays | Style Editor, Fact Checker, Impact Assessor |

**+ Altri 7 tipi riconosciuti automaticamente!**

---

## Output Generati

Entrambi i sistemi generano:

### 📁 File di Output
```
output_paper_review/
├── review_[agente].txt          # Review individuali
├── review_coordinator.txt        # Sintesi
├── review_final_evaluator.txt    # Valutazione finale (solo Generic)
├── review_editor.txt             # Decisione editoriale (solo Paper)
├── review_report_[timestamp].md  # Report Markdown
├── dashboard_[timestamp].html    # Dashboard HTML interattiva
└── review_results_[timestamp].json # Dati completi JSON
```

### 🌐 Dashboard HTML
Apri nel browser per:
- Vista overview con statistiche
- Review espandibili
- Navigazione facile
- Design professionale

---

## Comandi Utili

### Paper Reviewer
```bash
# Base
python3 main.py paper.pdf

# Con custom output
python3 main.py paper.pdf --output-dir my_review

# Debug mode
python3 main.py paper.pdf --log-level DEBUG
```

### Generic Reviewer
```bash
# Base
python3 generic_reviewer.py documento.pdf

# Con titolo custom
python3 generic_reviewer.py doc.txt --title "Mio Documento"

# Custom output directory
python3 generic_reviewer.py doc.pdf --output-dir reviews/business

# Demo mode (no API)
python3 demo_generic_reviewer.py documento.txt
```

### Rigenera Dashboard
Se hai già le review e vuoi solo aggiornare la dashboard:
```bash
python3 regenerate_dashboard.py
```

---

## Scelta Rapida

```
Il tuo documento è un paper scientifico/accademico?
│
├─ SÌ  → python3 main.py paper.pdf
│         (9 esperti accademici specializzati)
│
└─ NO  → python3 generic_reviewer.py documento.pdf
          (Classificazione automatica + agenti appropriati)
```

---

## 📚 Documentazione Completa

- **`GENERIC_REVIEWER_README.md`** - Guida completa Generic Reviewer
- **`COMPARISON_GUIDE.md`** - Confronto dettagliato tra i sistemi
- **`README.md`** - Documentazione Paper Reviewer

---

## 🎯 Esempi Pratici

### Esempio 1: Review Paper di Ricerca
```bash
python3 main.py "Deep_Learning_Cancer_Detection.pdf"
```

### Esempio 2: Review Business Proposal
```bash
python3 generic_reviewer.py business_proposal.pdf --title "ServiceAI Funding"
```

### Esempio 3: Review Contratto
```bash
python3 generic_reviewer.py contract.pdf
```

### Esempio 4: Review Documentazione API
```bash
python3 generic_reviewer.py api_documentation.md --title "API v2.0"
```

---

## 💡 Tips

1. **Per paper scientifici**: Usa sempre `main.py`
2. **Per tutto il resto**: Usa `generic_reviewer.py`
3. **Vuoi entrambe le prospettive?**: Esegui entrambi i sistemi!
4. **Test senza costi**: Usa `demo_generic_reviewer.py`
5. **Dashboard vecchia?**: Rigenera con `regenerate_dashboard.py`

---

## ⚡ One-Liner

```bash
# Paper scientifico → main.py
# Tutto il resto → generic_reviewer.py
```

---

## 💬 Modalità Interattiva 🆕

### Cosa Fa?

Attiva `--interactive` per permettere al sistema di **chiedere informazioni o file supplementari** durante il miglioramento.

### Come Usarla

```bash
python3 generic_reviewer.py documento.pdf --iterative --interactive
```

### Cosa Ti Può Chiedere

- 📊 **File Excel/CSV**: Dati finanziari, statistiche, calcoli
- 📄 **PDF/Word**: Documenti di riferimento, case studies
- 💬 **Informazioni**: Dati specifici che mancano nel documento

### Esempio Reale

```
🤔 RICHIESTE DI INFORMAZIONI AGGIUNTIVE
================================================================================

1. (Richiesto)
   Domanda: Puoi fornire il file Excel con le proiezioni finanziarie?
   Motivo: Per validare i calcoli e migliorare la credibilità
   Tipo file: xlsx, csv
   Inserisci il path del file (o INVIO per saltare):
   > /Users/me/Desktop/financial_model.xlsx
   ✅ File caricato e processato!

2. (Opzionale)
   Domanda: Qual è stato il fatturato effettivo nel Q3 2023?
   Motivo: Il Data Validator ha trovato un'incongruenza
   La tua risposta (o INVIO per saltare):
   > 2.450.000 euro
   ✅ Informazione ricevuta!
```

### Benefici

✅ **Qualità finale +50%** rispetto a modalità non-interattiva  
✅ **Dati esterni integrati** automaticamente nel documento  
✅ **Documenti più robusti** e verificabili  
✅ **Fonti citate** correttamente  

### Formati File Supportati

| Formato | Estensioni | Uso |
|---------|-----------|-----|
| Excel | `.xlsx`, `.xls`, `.csv` | Dati finanziari, tabelle |
| PDF | `.pdf` | Documenti di riferimento |
| Word | `.docx`, `.doc` | Contenuti supplementari |
| Testo | `.txt`, `.md`, `.json` | Note, dati strutturati |

### Installazione Dipendenze Opzionali

Per supportare tutti i formati:

```bash
# Excel/CSV
pip install pandas openpyxl

# Word
pip install python-docx
```

### Guide Complete

📖 **Guida dettagliata**: `MODALITA_INTERATTIVA.md`  
🎬 **Esempio pratico**: `ESEMPIO_INTERATTIVO.md`

---

## 🆘 Problemi Comuni

### ❌ "API key not configured"
**Soluzione:**
```bash
export OPENAI_API_KEY='tua-chiave-api'
```

### ❌ "Module not found"
**Soluzione:**
```bash
pip install -r requirements.txt
```

### ❌ "File not found"
**Soluzione:** Verifica il path del file sia corretto

---

## 📞 File Importanti

- `main.py` - Paper Reviewer
- `generic_reviewer.py` - Generic Reviewer  
- `demo_generic_reviewer.py` - Demo senza API
- `regenerate_dashboard.py` - Rigenera dashboard

---

**Buon reviewing! 🚀📋**

Per qualsiasi dubbio, consulta i README dettagliati!
