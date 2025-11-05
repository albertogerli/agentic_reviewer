# 🔄 Modalità Iterativa - Quick Reference

## 🎯 In Breve

**Il documento si auto-migliora attraverso iterazioni automatiche!**

```
Iterazione 1: Score 45/100 → Migliora → Salva
Iterazione 2: Score 72/100 → Migliora → Salva  
Iterazione 3: Score 87/100 → ✅ TARGET RAGGIUNTO!
```

---

## ⚡ Quick Start

### Base (3 iterazioni, target 85)
```bash
python3 generic_reviewer.py documento.pdf --iterative
```

### Personalizzato
```bash
python3 generic_reviewer.py documento.pdf --iterative \
    --max-iterations 5 \
    --target-score 90
```

---

## 📊 Come Funziona

```
┌──────────────┐
│  ITERAZIONE  │
├──────────────┤
│ 1. Review    │ → 30 agenti analizzano
│ 2. Score     │ → Punteggio 0-100
│ 3. Improve   │ → Modifiche applicate
└──────────────┘
      ↓ repeat
```

**Stop quando:**
- ✅ Score >= target E critici == 0
- ⚠️ Max iterazioni raggiunto

---

## 🎛️ Parametri

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--iterative` | Off | Attiva modalità |
| `--max-iterations` | 3 | Max iterazioni (1-10) |
| `--target-score` | 85 | Target qualità (0-100) |

---

## 📈 Scale Qualità

| Score | Qualità | Azione |
|-------|---------|--------|
| 90-100 | 🟢 Excellent | Pubblicabile |
| 75-89 | 🔵 Good | Minori fix |
| 60-74 | 🟡 Fair | Revisione moderata |
| 40-59 | 🟠 Poor | Revisione maggiore |
| 0-39 | 🔴 Bad | Riscrittura |

---

## 📁 Output

```
output_paper_review/
├── iterative_dashboard_*.html        ← APRI QUESTO! ⭐
├── iterative_comparison_*.md         ← Report comparativo
├── iterative_results_*.json          ← Dati completi
│
├── document_iteration_1_improved.txt ← Versione 1
├── document_iteration_2_improved.txt ← Versione 2
├── document_iteration_3_improved.txt ← Versione 3
└── document_best_version_iter3.txt   ← MIGLIORE ⭐
```

---

## 💡 Esempi Pratici

### Business Plan
```bash
python3 generic_reviewer.py business_plan.pdf --iterative \
    --max-iterations 5 --target-score 90
```
**Risultato:** Errori calcolo corretti, struttura migliorata

### Paper Scientifico
```bash
python3 generic_reviewer.py paper.pdf --iterative \
    --target-score 88
```
**Risultato:** Metodologia rafforzata, citazioni aggiunte

### Presentazione
```bash
python3 generic_reviewer.py slides.pdf --iterative \
    --output-language Italian
```
**Risultato:** Grafici migliorati, layout professionale

---

## 🔥 Features Killer

✅ **Document Scorer**
- Valuta qualità 0-100
- Identifica problemi critici
- Traccia miglioramenti

✅ **Document Refiner**  
- Applica modifiche automatiche
- Corregge errori identificati
- Migliora struttura e contenuto

✅ **Tracking Storico**
- Salva tutte le versioni
- Compara evoluzione
- Identifica best version

✅ **Dashboard Interattiva**
- Grafico evoluzione score
- Tabella comparativa iterazioni
- Export HTML professionale

---

## ⏱️ Performance

| Iterazioni | Tempo | Costo |
|------------|-------|-------|
| 2 | ~20 min | $6-15 |
| 3 | ~35 min | $9-25 |
| 5 | ~60 min | $15-40 |

**ROI:** Risparmio 8-16 ore lavoro manuale ✅

---

## 🎓 Quando Usare

### ✅ USA se:
- Documento con molti errori
- Serve versione production-ready
- Hai 30-60 minuti disponibili
- Budget $10-30 ok

### ❌ NON usare se:
- Serve solo feedback veloce
- Documento già ottimo
- Tempo/budget limitato
- Preferisci controllo manuale

---

## 🚨 Tips

1. **Doc scarso?** → `--max-iterations 5`
2. **Doc medio?** → `--max-iterations 3`  
3. **Doc buono?** → `--max-iterations 2`
4. **Target realistico:** 80-88 per maggior parte docs
5. **Monitora log** per vedere progresso real-time

---

## 📖 Documentazione Completa

Leggi `MODALITA_ITERATIVA_README.md` per:
- Architettura dettagliata
- Casi d'uso completi
- Troubleshooting
- Best practices

---

**Trasforma documenti mediocri in eccellenza, automaticamente! 🔄🚀**

```bash
python3 generic_reviewer.py tuo_documento.pdf --iterative
```
