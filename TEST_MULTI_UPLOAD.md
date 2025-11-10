# 🧪 Test Multi-Document Upload

## 🚀 Quick Test (2 minuti)

### Prerequisiti
✅ Backend: http://localhost:8000
✅ Frontend: http://localhost:3000

---

## Test 1: Upload Singolo (Backward Compatibility)

```bash
# Apri browser
open http://localhost:3000
```

1. **Drag & drop** 1 documento PDF
2. ✅ Verifica: File appare nella lista
3. ✅ Verifica: Pulsante dice **"Start AI Review"**
4. Clicca **"Start AI Review"**
5. ✅ Verifica: Analisi parte normalmente

**Tempo**: ~30 secondi

---

## Test 2: Upload Multipli (3 documenti)

```bash
# Prepara 3 file di test (se non li hai):
cd /tmp
echo "Document 1 content" > doc1.txt
echo "Document 2 content" > doc2.txt
echo "Document 3 content" > doc3.txt
```

1. **Ricarica** la pagina (⌘+R o Ctrl+R)
2. **Seleziona multipli file**: 
   - Clicca nell'area upload
   - Seleziona `doc1.txt`, `doc2.txt`, `doc3.txt` con ⌘ (Mac) o Ctrl (Windows)
3. ✅ Verifica: 3 file appaiono nella lista
4. ✅ Verifica: Ogni file mostra nome e dimensione
5. ✅ Verifica: Titolo: **"📋 Review Options (3 documents)"**
6. ✅ Verifica: Pulsante: **"Start Batch Review (3 documents)"**

**Tempo**: ~1 minuto

---

## Test 3: Drag & Drop Multipli

1. **Apri Finder** (Mac) o **Explorer** (Windows)
2. **Seleziona** 4-5 file (PDF, DOCX, TXT, MD)
3. **Drag & drop** nell'area di upload
4. ✅ Verifica: Tutti i file appaiono nella lista
5. ✅ Verifica: Counter: **"📄 X documents to analyze"**
6. ✅ Verifica: Pulsante: **"Start Batch Review (X documents)"**

**Tempo**: ~30 secondi

---

## Test 4: Rimozione File

1. **Carica** 5 documenti
2. **Hover** su un file nella lista
3. ✅ Verifica: Appare icona **X** rossa
4. **Clicca** l'icona X
5. ✅ Verifica: File rimosso, counter aggiornato
6. **Clicca** "Clear All"
7. ✅ Verifica: Lista vuota

**Tempo**: ~30 secondi

---

## Test 5: Reference Documents

1. **Carica** 2 documenti input
2. **Scroll down** → vedi sezione **"📚 Reference Documents (Optional)"**
3. **Clicca** "Choose File"
4. **Seleziona** 2-3 documenti reference
5. ✅ Verifica: Appaiono nella lista reference (sfondo viola)
6. ✅ Verifica: Badge: **"3"** vicino al titolo
7. **Clicca** "Start Batch Review"
8. ✅ Verifica: Analisi usa i reference

**Tempo**: ~1 minuto

---

## Test 6: Batch Review Completo

```bash
# Prepara documenti di test
cd /tmp
for i in {1..5}; do
  echo "This is test document $i with some content for analysis." > test_doc_$i.txt
done
```

1. **Drag & drop** tutti e 5 i file
2. **Configura** opzioni:
   - Output Language: **Italiano**
   - Deep Review: **✅**
3. **Clicca** "Start Batch Review (5 documents)"
4. **Osserva** il progresso:
   ```
   ⏳ Processing document 1/5: test_doc_1.txt
   ⏳ Processing document 2/5: test_doc_2.txt
   ⏳ Processing document 3/5: test_doc_3.txt
   ⏳ Processing document 4/5: test_doc_4.txt
   ⏳ Processing document 5/5: test_doc_5.txt
   ✅ Batch review complete! 5/5 successful
   ```
5. ✅ Verifica: Tab **"Summary"** mostra risultati aggregati
6. ✅ Verifica: Ogni documento ha la sua cartella in `outputs/`

**Tempo**: ~5-10 minuti (dipende dalla dimensione)

---

## 📊 Checklist Visiva

### Upload Area

| Element | Expected | ✅ |
|---------|----------|---|
| Drag & drop zone | Bordo dashed, icona documento | |
| isDragActive | Bordo blu, bg blu chiaro, scale 1.05 | |
| File counter | "📄 X document(s) to analyze" | |
| Clear All button | Rosso, in alto a destra | |
| File list | Grid 2 colonne, card bianche | |
| File card hover | Bordo primary-300 | |
| Remove button | X rossa, opacity 0 → 100% on hover | |

### Reference Section

| Element | Expected | ✅ |
|---------|----------|---|
| Background | Gradient viola-blu | |
| Title | "📚 Reference Documents (Optional)" | |
| Badge | Viola, numero documenti | |
| File list | Grid 2 colonne, bordo viola | |
| Clear All | Rosso, stesso stile input | |

### Review Options

| Element | Expected | ✅ |
|---------|----------|---|
| Title | "📋 Review Options" | |
| Title (multi) | "📋 Review Options (X documents)" | |
| Start button (single) | "Start AI Review" | |
| Start button (multi) | "Start Batch Review (X documents)" | |

---

## 🎨 Screenshots Attesi

### Before Upload
```
┌────────────────────────────────────────────┐
│                                            │
│         📄 Drag & drop your documents      │
│            or click to browse              │
│                                            │
│         PDF  DOCX  TXT  MD                 │
└────────────────────────────────────────────┘
```

### After Upload (3 docs)
```
┌────────────────────────────────────────────┐
│ 📄 3 documents to analyze    [Clear All]  │
├────────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐        │
│ │ 📄 doc1.pdf  │  │ 📄 doc2.docx │        │
│ │ 2.5 MB    [X]│  │ 1.8 MB    [X]│        │
│ └──────────────┘  └──────────────┘        │
│ ┌──────────────┐                           │
│ │ 📄 doc3.txt  │                           │
│ │ 0.1 MB    [X]│                           │
│ └──────────────┘                           │
│                                            │
│ 📂 Click or drag to add more (max 10)     │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ 📚 Reference Documents (Optional) [3]      │
│                               [Clear All]  │
├────────────────────────────────────────────┤
│ [Choose File]                              │
│                                            │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ 📄 guide.pdf │  │ 📄 template  │        │
│ │ 1.2 KB    [X]│  │ 0.5 KB    [X]│        │
│ └──────────────┘  └──────────────┘        │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ 📋 Review Options (3 documents)            │
│ ...                                        │
│ [Start Batch Review (3 documents)]         │
└────────────────────────────────────────────┘
```

### During Batch Processing
```
⏳ Processing document 2/5: report.pdf
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40%

🔬 Subject Matter Expert analyzing...
```

---

## ✅ Risultato Finale

Se **tutti i test** passano:

🎉 **Multi-Document Upload funziona perfettamente!**

### Cosa Hai Testato:
- ✅ Upload singolo (backward compatible)
- ✅ Upload multipli (via select)
- ✅ Drag & drop multipli
- ✅ Rimozione individuale
- ✅ Clear all
- ✅ Reference documents
- ✅ Batch processing
- ✅ Progress tracking
- ✅ UI dinamica (counter, button text)

---

## 🐛 Troubleshooting Rapido

### Pulsante "Start" disabilitato
**Causa**: Nessun file caricato
**Fix**: Controlla che `inputFiles.length > 0`

### File non appare dopo upload
**Causa**: Hot reload ha perso lo stato
**Fix**: Ricarica la pagina (⌘+R)

### Batch review non parte
**Causa**: Backend offline
**Fix**: Verifica `http://localhost:8000/docs`

### Progress non si aggiorna
**Causa**: WebSocket disconnesso
**Fix**: Controlla console browser per errori WS

---

## 📦 Output Atteso

### Struttura File (Batch di 3)
```
outputs/
├── batch_review_20251110_123456/
│   └── batch_results.json
├── doc1_20251110_123457/
│   ├── review_results.json
│   ├── review_report.md
│   └── dashboard.html
├── doc2_20251110_123458/
│   ├── review_results.json
│   ├── review_report.md
│   └── dashboard.html
└── doc3_20251110_123459/
    ├── review_results.json
    ├── review_report.md
    └── dashboard.html
```

### batch_results.json
```json
{
  "batch_review_id": "review_20251110_123456",
  "total_documents": 3,
  "successful": 3,
  "failed": 0,
  "documents": [
    {
      "file": "doc1.pdf",
      "status": "success",
      "output_dir": "outputs/doc1_20251110_123457",
      "summary": "..."
    },
    ...
  ],
  "timestamp": "2025-11-10T12:34:56Z"
}
```

---

**Ready to Test!** 🚀

Tempo totale: **~10-15 minuti** per tutti i test

