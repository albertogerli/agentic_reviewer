# 📚 Multi-Document & Reference Context - Guida Completa

## 🎯 Nuove Funzionalità

### 1️⃣ **Analisi Multipli Documenti (Batch)**
Analizza più documenti contemporaneamente da:
- 📁 Directory (tutti i file supportati)
- 📦 File ZIP (estrae e analizza automaticamente)
- ⚡ Processing parallelo o sequenziale
- 📊 Statistiche aggregate

### 2️⃣ **Documenti di Riferimento (Context)**
Carica documenti di riferimento come base/contesto:
- 📋 Template (strutture, formati)
- 📜 Guidelines (policy aziendali, standard)
- ⭐ Esempi (documenti di successo precedenti)
- 📊 Data sheets (specifiche tecniche, dati prodotto)
- ✍️ Style guides (tono, formattazione)

---

## 🚀 Quick Start

### Batch Processing

```bash
# Analizza tutti i documenti in una directory
python3 generic_reviewer.py \
    --batch-dir /path/to/documents/ \
    --iterative

# Analizza documenti in ZIP
python3 generic_reviewer.py \
    --batch-zip /path/to/documents.zip \
    --iterative \
    --parallel

# Con reference documents
python3 generic_reviewer.py \
    --batch-dir /path/to/documents/ \
    --reference-dir /path/to/templates/ \
    --reference-type template
```

---

## 📁 1. Batch Processing

### Caso d'Uso: Team Review

**Scenario:** Devi revieware 10 proposte commerciali per un cliente.

```bash
# Struttura directory
proposals/
├── proposal_client_A.pdf
├── proposal_client_B.pdf
├── proposal_client_C.pdf
└── ... (7 more)

# Comando
python3 generic_reviewer.py \
    --batch-dir proposals/ \
    --project "Q4 Client Proposals" \
    --iterative \
    --parallel \
    --max-concurrent 3

# Output
batch_reviews/
└── batch_20241104_150000/
    ├── batch_summary.json              ← Summary di tutto
    ├── comparison_report.md            ← Confronto tra documenti
    ├── proposal_client_A/
    │   ├── dashboard_*.html
    │   ├── review_*.json
    │   └── ...
    ├── proposal_client_B/
    │   └── ...
    └── ...
```

### Batch Summary

```json
{
  "batch_id": "batch_20241104_150000",
  "total_documents": 10,
  "successful": 9,
  "failed": 1,
  "processing_time": 342.5,
  "aggregate_stats": {
    "total_processed": 9,
    "scores": {
      "mean": 78.3,
      "min": 65.0,
      "max": 89.0
    }
  }
}
```

### Comparison Report

Automaticamente generato per confrontare i documenti:

```markdown
# Cross-Document Comparison Report

**Total Documents:** 9
**Average Score:** 78.3/100
**Best Score:** 89.0/100
**Worst Score:** 65.0/100

## Document Rankings

| Rank | Document | Score |
|------|----------|-------|
| 1 | proposal_client_C.pdf | 89.0/100 |
| 2 | proposal_client_A.pdf | 84.5/100 |
| 3 | proposal_client_F.pdf | 81.2/100 |
...
```

---

## 📦 2. Processing da ZIP

### Caso d'Uso: Archivio Documenti

**Scenario:** Hai un archivio ZIP con documenti sparsi in sottocartelle.

```bash
# Struttura ZIP
documents.zip
├── chapter1/
│   ├── intro.pdf
│   └── methodology.pdf
├── chapter2/
│   ├── results.pdf
│   └── analysis.pdf
└── appendix/
    └── data.pdf

# Comando
python3 generic_reviewer.py \
    --batch-zip documents.zip \
    --project "PhD Thesis Chapters" \
    --iterative

# Il sistema:
1. Estrae ZIP in temp directory
2. Scopre tutti i PDF
3. Li processa uno ad uno
4. Crea output strutturato
5. Pulisce temp directory
```

---

## 📋 3. Reference Documents

### Cosa Sono?

Documenti che forniscono **contesto** per la review:

| Tipo | Quando Usare | Esempio |
|------|--------------|---------|
| **Template** | Vuoi che il documento segua una struttura specifica | Template proposta aziendale |
| **Guideline** | Hai policy/standard da rispettare | Company writing guidelines |
| **Example** | Mostra documenti di successo come riferimento | Proposte vincenti precedenti |
| **Style Guide** | Definisci tono e stile | Brand voice guide |
| **Data** | Fornisci dati tecnici di riferimento | Product specifications |

### Come Funziona?

1. **Carichi reference documents** (template, guidelines, etc.)
2. **Sistema li include nel contesto** della review
3. **AI confronta** documento da revieware con i references
4. **Feedback include** confronto con standards/template

---

## 💡 Casi d'Uso Reali

### Caso 1: Proposte Commerciali con Template Aziendale

```bash
# Setup
company_templates/
├── proposal_template.docx       # Struttura standard
└── pricing_guidelines.pdf       # Policy pricing

proposals_to_review/
├── proposal_client_X.pdf
├── proposal_client_Y.pdf
└── proposal_client_Z.pdf

# Comando
python3 generic_reviewer.py \
    --batch-dir proposals_to_review/ \
    --reference-dir company_templates/ \
    --reference-type template \
    --iterative

# Risultato
✅ Ogni proposta viene confrontata con il template
✅ AI verifica se struttura corrisponde
✅ Controlla se pricing segue guidelines
✅ Suggerisce modifiche per allineamento
```

**Review Output (esempio):**
```
📋 Template Compliance Analysis:

✅ Structure matches company template (8/10 sections)
❌ Missing section: "Risk Assessment" (required in template)
⚠️  Pricing section format differs from guideline
    → Template uses tables, document uses bullet points
    → Recommend: Convert to table format

Suggestions:
1. Add "Risk Assessment" section (template sec. 7)
2. Reformat pricing as per guideline Table 3.2
3. Include standard disclaimer (template appendix A)
```

### Caso 2: Tesi con Style Guide Universitario

```bash
# Setup
university_guides/
├── thesis_requirements.pdf      # Requisiti formali
└── citation_style.pdf           # Stile citazioni

thesis_chapters/
├── chapter1_intro.pdf
├── chapter2_literature.pdf
└── chapter3_methodology.pdf

# Comando
python3 generic_reviewer.py \
    --batch-dir thesis_chapters/ \
    --reference-dir university_guides/ \
    --reference-type guideline \
    --iterative \
    --interactive

# Risultato
✅ Verifica conformità a requisiti universitari
✅ Controlla stile citazioni
✅ Valida formattazione
✅ Suggerisce correzioni per compliance
```

### Caso 3: Report Tecnici con Product Specs

```bash
# Setup
product_specs/
├── model_X_datasheet.pdf        # Specifiche prodotto
└── technical_standards.pdf      # Standard tecnici

reports/
├── installation_guide.pdf
├── maintenance_manual.pdf
└── troubleshooting_guide.pdf

# Comando
python3 generic_reviewer.py \
    --batch-dir reports/ \
    --reference-dir product_specs/ \
    --reference-type data \
    --iterative

# Risultato
✅ Verifica accuratezza dati tecnici vs datasheet
✅ Controlla riferimenti a specifiche corrette
✅ Valida numeri e parametri tecnici
✅ Segnala discrepanze con specs ufficiali
```

**Review Output (esempio):**
```
🔢 Data Accuracy Check:

✅ Operating temperature: -20°C to +60°C (matches datasheet)
❌ Power consumption: Document states "150W max"
    → Datasheet specifies: 120W typical, 140W max
    → Correction needed: Update to "120W typical (140W max)"

⚠️  Model number inconsistency:
    → Document: "Model X-2000"
    → Datasheet: "Model X-2000B" (B variant includes feature Y)
    → Clarify which variant is being documented
```

### Caso 4: Marketing Content con Brand Guidelines

```bash
# Setup
brand_guidelines/
├── brand_voice_guide.pdf        # Tono e stile
├── visual_standards.pdf         # Standard visivi
└── approved_messaging.docx      # Messaging approvato

marketing_drafts/
├── campaign_email_1.txt
├── campaign_email_2.txt
├── landing_page_copy.txt
└── social_posts.txt

# Comando
python3 generic_reviewer.py \
    --batch-dir marketing_drafts/ \
    --reference-dir brand_guidelines/ \
    --reference-type style_guide \
    --iterative \
    --output-language Italian

# Risultato
✅ Valuta tono vs brand voice
✅ Verifica messaging alignment
✅ Controlla compliance con guidelines
✅ Suggerisce modifiche per brand consistency
```

---

## 🎮 Comandi Completi

### Batch Processing Semplice

```bash
# Directory
python3 generic_reviewer.py --batch-dir /path/to/docs/

# ZIP
python3 generic_reviewer.py --batch-zip /path/to/docs.zip

# Con progetto
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --project "Q4 Reviews"
```

### Batch con Iterative Mode

```bash
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --iterative \
    --max-iterations 3 \
    --target-score 85
```

### Batch Parallelo (più veloce)

```bash
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --parallel \
    --max-concurrent 5 \
    --iterative
```

### Con Reference Documents

```bash
# Single reference file
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --reference /path/to/template.pdf \
    --reference-type template

# Reference directory
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --reference-dir /path/to/guidelines/ \
    --reference-type guideline

# Reference ZIP
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --reference-zip /path/to/examples.zip \
    --reference-type example

# Multiple reference sources
python3 generic_reviewer.py \
    --batch-dir /path/to/docs/ \
    --reference-dir /path/to/templates/ \
    --reference-type template \
    --reference-dir /path/to/guidelines/ \
    --reference-type guideline
```

### Setup Completo

```bash
python3 generic_reviewer.py \
    --batch-dir proposals/ \
    --project "Client Proposals Q4" \
    --reference-dir templates/ \
    --reference-type template \
    --reference-dir guidelines/ \
    --reference-type guideline \
    --iterative \
    --interactive \
    --parallel \
    --max-concurrent 3 \
    --max-iterations 5 \
    --target-score 90 \
    --output-language Italian
```

---

## 📊 Output Structure

### Without References

```
batch_reviews/batch_20241104_150000/
├── batch_summary.json           # Overall summary
├── comparison_report.md         # Cross-document comparison
├── document_1/
│   ├── dashboard_*.html
│   ├── review_*.json
│   └── review_*.md
├── document_2/
│   └── ...
└── document_3/
    └── ...
```

### With References

```
batch_reviews/batch_20241104_150000/
├── batch_summary.json
├── comparison_report.md
├── reference_context.txt        # ← Reference documents used
├── reference_summary.json       # ← Reference metadata
├── document_1/
│   ├── dashboard_*.html
│   ├── review_*.json           # ← Includes reference comparison
│   ├── review_*.md
│   └── template_compliance.md   # ← Compliance analysis
└── ...
```

---

## 🎯 Best Practices

### 1. Organizza References per Tipo

```
references/
├── templates/
│   ├── proposal_template.docx
│   └── report_template.pdf
├── guidelines/
│   ├── company_standards.pdf
│   └── writing_guidelines.md
├── examples/
│   ├── successful_proposal_1.pdf
│   └── successful_proposal_2.pdf
└── data/
    └── product_specifications.pdf
```

### 2. Usa Nomi File Descrittivi

```bash
# ✅ Bene
company_proposal_template_v2024.docx
technical_writing_guidelines.pdf
successful_proposal_clientA_2023.pdf

# ❌ Male
template.docx
doc1.pdf
example.pdf
```

### 3. Batch Processing Progressivo

```bash
# Test first su sample
python3 generic_reviewer.py \
    --batch-dir docs/ \
    --sample 3  # Process only first 3

# Se OK, lancia full batch
python3 generic_reviewer.py \
    --batch-dir docs/ \
    --parallel
```

### 4. Reference Context Size

```bash
# Default: max 50K chars di references
# Se hai molti references, prioritizza:

# Solo templates critici
--reference-dir templates/ --reference-type template

# O limita dimensione
--reference-max-chars 30000
```

---

## 📈 Performance

### Batch Processing

| Docs | Sequential | Parallel (3x) | Parallel (5x) |
|------|-----------|---------------|---------------|
| 5 | ~25 min | ~12 min | ~10 min |
| 10 | ~50 min | ~20 min | ~15 min |
| 20 | ~100 min | ~40 min | ~25 min |

**Raccomandazione:** Usa `--parallel --max-concurrent 3` per best results.

### With References

| Reference Size | Impact | Recommendation |
|----------------|--------|----------------|
| < 10KB | Minimal (+5%) | ✅ Always include |
| 10-30KB | Moderate (+15%) | ✅ Recommended |
| 30-50KB | Noticeable (+30%) | ⚠️ For important docs |
| > 50KB | Significant (+50%) | ❌ Split or prioritize |

---

## 🔍 Troubleshooting

### Issue: Out of Memory

```bash
# Se processamento parallelo causa OOM:
--max-concurrent 2  # Riduci concurrent processes
# O
--parallel false    # Disabilita parallelismo
```

### Issue: References Too Large

```bash
# Limita dimensione context
--reference-max-chars 20000

# O seleziona solo references critici
--reference-dir templates/ --reference-type template
# (ometti altri types)
```

### Issue: ZIP Extraction Fails

```bash
# Check ZIP integrity
unzip -t documents.zip

# Usa directory invece
unzip documents.zip -d temp/
python3 generic_reviewer.py --batch-dir temp/
```

---

## 💡 Advanced Use Cases

### Use Case 1: Continuous Document Review

```bash
# Setup cron job per review automatica
0 0 * * * python3 /path/to/generic_reviewer.py \
    --batch-dir /company/new_documents/ \
    --reference-dir /company/standards/ \
    --reference-type guideline \
    --iterative \
    --project "Daily Auto-Review"
```

### Use Case 2: Multi-Language Projects

```bash
# Italian documents with English guidelines
python3 generic_reviewer.py \
    --batch-dir docs_italian/ \
    --reference-dir guidelines_english/ \
    --reference-type guideline \
    --output-language Italian
```

### Use Case 3: Version Comparison

```bash
# Review multiple versions of same doc
versions/
├── proposal_v1.pdf
├── proposal_v2.pdf
└── proposal_v3.pdf

python3 generic_reviewer.py \
    --batch-dir versions/ \
    --project "Proposal Evolution"

# Comparison report shows improvements across versions
```

---

## 📚 Riferimenti

- `multi_document_processor.py` - Batch processing engine
- `reference_context.py` - Reference document system
- `generic_reviewer.py` - Main CLI (updated with batch support)

---

## ✅ Summary

### Prima
```
❌ Un documento alla volta
❌ Nessun contesto/riferimento
❌ Nessun confronto tra documenti
```

### Adesso
```
✅ Batch processing (directory/ZIP)
✅ Parallelo o sequenziale
✅ Reference documents come contesto
✅ Cross-document comparison
✅ Aggregate statistics
✅ Template compliance analysis
```

---

**Analizza interi progetti con contesto aziendale! 📚🚀📊**

