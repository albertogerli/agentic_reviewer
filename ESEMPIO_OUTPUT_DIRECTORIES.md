# 📁 Struttura Directory Output

## 🎯 Sistema Nuovo (Non Sovrascrive!)

Ogni review viene salvata in una **cartella unica** con nome documento + timestamp.

### Struttura

```
output_paper_review/
├── Business_Plan_2024_20241104_103045/
│   ├── dashboard_*.html
│   ├── review_*.txt
│   └── ...
│
├── Business_Plan_2024_20241104_154522/    ← Stessa doc, review diversa!
│   ├── dashboard_*.html
│   ├── review_*.txt
│   └── ...
│
├── Research_Paper_AI_20241104_091234/
│   ├── dashboard_*.html
│   ├── review_*.txt
│   └── ...
│
└── example_business_proposal_20241104_163011/
    ├── dashboard_*.html
    ├── review_*.txt
    └── ...
```

### Formato Nome Cartella

```
{DOCUMENT_NAME}_{TIMESTAMP}/

Dove:
- DOCUMENT_NAME: Nome file (max 50 caratteri, solo alphanumerici)
- TIMESTAMP: YYYYMMDD_HHMMSS
```

---

## 📝 Esempi Reali

### Esempio 1: Stesso Documento, Review Diverse

```bash
# Prima review
python3 generic_reviewer.py business_plan.pdf
→ output_paper_review/business_plan_20241104_100000/

# Seconda review (2 ore dopo)
python3 generic_reviewer.py business_plan.pdf
→ output_paper_review/business_plan_20241104_120000/

# Modalità iterativa
python3 generic_reviewer.py business_plan.pdf --iterative
→ output_paper_review/business_plan_20241104_140000/
```

**Risultato:** 3 cartelle separate, nessun file sovrascritto! ✅

### Esempio 2: Documenti Diversi

```bash
# Business plan
python3 generic_reviewer.py business_plan.pdf
→ output_paper_review/business_plan_20241104_100000/

# Research paper
python3 generic_reviewer.py research_paper.pdf
→ output_paper_review/research_paper_20241104_100530/

# Contract
python3 generic_reviewer.py service_contract.pdf
→ output_paper_review/service_contract_20241104_101045/
```

**Risultato:** Ogni documento nella sua cartella! ✅

### Esempio 3: Titolo Custom

```bash
python3 generic_reviewer.py doc.pdf --title "Strategic Plan Q4 2024"
→ output_paper_review/Strategic_Plan_Q4_2024_20241104_100000/
```

**Risultato:** Nome leggibile e descrittivo! ✅

---

## 🔍 Contenuto Tipico Cartella

### Modalità Standard

```
business_plan_20241104_100000/
├── dashboard_20241104_100812.html           ← Dashboard principale
├── review_report_20241104_100812.md         ← Report Markdown
├── review_results_20241104_100812.json      ← Dati JSON
├── executive_summary_20241104_100812.md     ← Executive summary
│
├── document_classification.json              ← Classificazione doc
├── paper_info.json                           ← Info estratte
│
├── review_business_analyst.txt               ← Review individuali
├── review_financial_analyst.txt
├── review_data_validator.txt
├── review_risk_assessor.txt
├── review_coordinator.txt
├── review_final_evaluator.txt
└── ...
```

### Modalità Iterativa

```
business_plan_20241104_140000/
├── iterative_dashboard_20241104_141523.html  ← Dashboard iterativa
├── iterative_comparison_20241104_141523.md   ← Report comparativo
├── iterative_results_20241104_141523.json    ← Dati completi
│
├── document_iteration_1_improved.txt         ← Versioni intermedie
├── document_iteration_2_improved.txt
├── document_iteration_3_improved.txt
├── document_best_version_iter3.txt           ← Best version
│
├── document_classification.json
├── review_business_analyst.txt               ← Review iter 1
├── review_financial_analyst.txt
└── ...
```

---

## 💡 Vantaggi

### ✅ Non Sovrascrive Mai
Ogni review è in una cartella separata con timestamp unico.

### ✅ Storico Completo
Puoi confrontare review dello stesso documento in momenti diversi:
```
business_plan_20241104_100000/  → Versione mattina
business_plan_20241104_150000/  → Versione pomeriggio (dopo modifiche)
```

### ✅ Organizzazione Automatica
Tutte le review raggruppate per documento:
```bash
ls -lt output_paper_review/
# Mostra cartelle ordinate per data (più recente prima)
```

### ✅ Nome Leggibile
```
Strategic_Plan_Q4_2024_20241104_100000/
↑                      ↑
Nome descrittivo       Timestamp preciso
```

---

## 🔧 Gestione Directory

### Trovare Review Specifiche

```bash
# Review più recente di un documento
ls -t output_paper_review/business_plan_* | head -1

# Tutte le review di un documento
ls -d output_paper_review/business_plan_*/

# Review di oggi
ls -d output_paper_review/*_$(date +%Y%m%d)_*/
```

### Pulizia Vecchie Review

```bash
# Elimina review più vecchie di 30 giorni
find output_paper_review/ -type d -mtime +30 -exec rm -rf {} +

# Mantieni solo ultime 5 review per documento
# (script custom necessario)
```

### Backup

```bash
# Backup di tutte le review
tar -czf reviews_backup_$(date +%Y%m%d).tar.gz output_paper_review/

# Backup review specifiche
tar -czf business_plan_reviews.tar.gz output_paper_review/business_plan_*/
```

---

## �� Confronto Versioni

### Prima (Sistema Vecchio) ❌

```
output_paper_review/
├── dashboard.html          ← SOVRASCRITTO ogni volta!
├── review_results.json     ← SOVRASCRITTO ogni volta!
└── review_*.txt            ← SOVRASCRITTI ogni volta!

Problema: Perdita dati precedenti!
```

### Ora (Sistema Nuovo) ✅

```
output_paper_review/
├── doc1_20241104_100000/   ← Review 1 (preservata)
├── doc1_20241104_120000/   ← Review 2 (preservata)
├── doc1_20241104_140000/   ← Review 3 (preservata)
└── doc2_20241104_100000/   ← Altro doc (preservato)

Vantaggio: Storico completo mantenuto!
```

---

## 🎯 Best Practices

### 1. Titoli Descrittivi

```bash
# Meglio
python3 generic_reviewer.py doc.pdf --title "Business Plan Q4 2024"
→ output_paper_review/Business_Plan_Q4_2024_20241104_100000/

# Invece di
python3 generic_reviewer.py doc.pdf
→ output_paper_review/doc_20241104_100000/
```

### 2. Naming Convention

Per documenti ricorrenti, usa naming consistente:
```
Business_Plan_Q1_2024
Business_Plan_Q2_2024
Business_Plan_Q3_2024
Business_Plan_Q4_2024
```

### 3. Backup Periodico

Importante per review production:
```bash
# Script backup automatico
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf ~/backups/reviews_$DATE.tar.gz output_paper_review/
```

---

## 🔍 Ricerca Veloce

### Trova Review Specifiche

```bash
# Review di un documento specifico
find output_paper_review/ -type d -name "business_plan_*"

# Review di oggi
find output_paper_review/ -type d -name "*_$(date +%Y%m%d)_*"

# Review in modalità iterativa (contengono iterative_dashboard)
find output_paper_review/ -name "iterative_dashboard_*.html"

# Best versions
find output_paper_review/ -name "document_best_version_*.txt"
```

---

## 📋 Summary

### Prima della Modifica
❌ Ogni review sovrascriveva la precedente  
❌ Perdita storico review  
❌ Impossibile confrontare versioni  

### Dopo la Modifica
✅ Ogni review in cartella unica  
✅ Storico completo preservato  
✅ Facile confronto tra versioni  
✅ Nome cartella leggibile  
✅ Timestamp preciso  
✅ Organizzazione automatica  

---

**Sistema robusto per gestione professionale review! 📁✅**
