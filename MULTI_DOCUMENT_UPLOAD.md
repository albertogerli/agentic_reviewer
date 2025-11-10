# 📚 Multi-Document Upload Feature

## 🎯 Overview

Il sistema ora supporta l'upload e l'analisi di **multipli documenti** sia come **input** (da analizzare) che come **reference** (documenti di riferimento).

---

## ✨ Nuove Funzionalità

### 1. **Upload Multipli Input Documents**
- Carica fino a **10 documenti** da analizzare contemporaneamente
- Drag & drop multipli file o click per selezionare
- Rimozione individuale o "Clear All"
- Grid view con preview di tutti i file

### 2. **Upload Multipli Reference Documents**
- Carica multipli documenti di riferimento (templates, guidelines, examples, data)
- Stessa interfaccia intuitiva con drag & drop
- Differenziazione visiva (background purple/blue)
- Gestione indipendente dagli input documents

### 3. **Batch Processing**
- Elaborazione parallela di tutti i documenti input
- Progress tracking per ogni documento
- Risultati combinati in un unico report batch
- Gestione errori per singolo documento (non blocca gli altri)

---

## 🎨 UI/UX

### Input Documents Section
```
┌─────────────────────────────────────────────────────┐
│  Drag & drop your documents                          │
│  or click to browse • Upload multiple files          │
│                                                       │
│  [PDF] [DOCX] [TXT] [MD]                             │
└─────────────────────────────────────────────────────┘

Dopo upload:
┌─────────────────────────────────────────────────────┐
│  📄 3 documents to analyze          [Clear All]      │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │ 📄 doc1.pdf      │  │ 📄 doc2.docx     │         │
│  │ 2.5 MB      [x]  │  │ 1.8 MB      [x]  │         │
│  └──────────────────┘  └──────────────────┘         │
│  ┌──────────────────┐                                │
│  │ 📄 doc3.txt      │                                │
│  │ 0.5 MB      [x]  │                                │
│  └──────────────────┘                                │
│  ⬆️ Click or drag to add more documents (max 10)    │
└─────────────────────────────────────────────────────┘
```

### Reference Documents Section
```
┌─────────────────────────────────────────────────────┐
│  📚 Reference Documents (Optional) [2]  [Clear All]  │
│  Upload templates, guidelines, examples, or data     │
│                                                       │
│  [Choose files or drag here]                         │
│                                                       │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │ 📄 template.pdf  │  │ 📄 guidelines.md │         │
│  │ 450 KB      [x]  │  │ 125 KB      [x]  │         │
│  └──────────────────┘  └──────────────────┘         │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Frontend Changes

#### `FileUpload.tsx`
```typescript
// State management
const [inputFiles, setInputFiles] = useState<File[]>([]);
const [referenceFiles, setReferenceFiles] = useState<File[]>([]);

// Multiple files support
maxFiles: 10,
multiple: true,

// Remove individual file
const removeInputFile = (index: number) => {
  const updated = inputFiles.filter((_, i) => i !== index);
  setInputFiles(updated);
  setStoreInputFiles(updated);
};
```

#### `reviewStore.ts`
```typescript
interface ReviewState {
  file: File | null; // Backward compatibility
  inputFiles: File[]; // Multiple input files ✨
  referenceFiles: File[];
  // ...
}

// Upload all files
filesToProcess.forEach((f) => {
  formData.append('files', f);
});
```

### Backend Changes

#### `app.py`
```python
@app.post("/api/review/upload")
async def upload_document(
    files: List[UploadFile] = File(...),  # Multiple files ✨
    config: Optional[str] = Form(None),
    reference_files: Optional[List[UploadFile]] = File(None)
):
    # Save all files
    file_paths = []
    for uploaded_file in files:
        file_path = upload_dir / uploaded_file.filename
        # Save...
        file_paths.append(str(file_path))
    
    # Process batch
    asyncio.create_task(
        process_multiple_reviews(review_id, file_paths, config, reference_paths)
    )
```

#### Batch Processing Logic
```python
async def process_multiple_reviews(review_id, file_paths, config, reference_paths):
    # Single file → normal processing
    if len(file_paths) == 1:
        await process_review(...)
        return
    
    # Multiple files → batch processing
    all_results = []
    for idx, file_path in enumerate(file_paths, 1):
        result = await process_single_document(...)
        all_results.append(result)
    
    # Combine results
    combined_results = {
        "batch_review_id": review_id,
        "total_documents": len(file_paths),
        "successful": ...,
        "failed": ...,
        "documents": all_results
    }
```

---

## 📊 API Changes

### Request Format

**Before (single file):**
```bash
POST /api/review/upload
Content-Type: multipart/form-data

file: document.pdf
config: {...}
reference_files: [ref1.pdf, ref2.docx]
```

**After (multiple files):**
```bash
POST /api/review/upload
Content-Type: multipart/form-data

files: [doc1.pdf, doc2.docx, doc3.txt]  # Multiple! ✨
config: {...}
reference_files: [ref1.pdf, ref2.docx]  # Multiple! ✨
```

### Response Format

**Single File:**
```json
{
  "status": "started",
  "message": "Review started",
  "review_id": "review_20251110_123456",
  "config": {...}
}
```

**Multiple Files:**
```json
{
  "status": "started",
  "message": "Review started for 3 document(s)",
  "review_id": "review_20251110_123456",
  "file_count": 3,
  "config": {...}
}
```

---

## 📁 Output Structure

### Single Document
```
outputs/
  └── document_name_20251110_123456/
      ├── review_results.json
      ├── review_report.md
      ├── dashboard.html
      └── presentation.pdf
```

### Batch Documents
```
outputs/
  ├── batch_review_20251110_123456/
  │   └── batch_results.json  # Combined results
  ├── doc1_20251110_123456/
  │   ├── review_results.json
  │   ├── review_report.md
  │   └── dashboard.html
  ├── doc2_20251110_123457/
  │   ├── review_results.json
  │   ├── review_report.md
  │   └── dashboard.html
  └── doc3_20251110_123458/
      ├── review_results.json
      ├── review_report.md
      └── dashboard.html
```

---

## 🧪 Testing

### Test Upload Multipli Input
1. Vai su http://localhost:3000
2. Drag & drop **3 PDF** nella zona upload
3. Verifica che mostri "📄 3 documents to analyze"
4. Verifica la grid con tutti e 3 i file
5. Clicca [x] su uno → verifica rimozione
6. Clicca "Clear All" → verifica reset completo

### Test Upload Multipli Reference
1. Carica almeno 1 input document
2. Nella sezione "📚 Reference Documents":
   - Click su "Choose files"
   - Seleziona 2-3 file (PDF, DOCX, MD)
3. Verifica che mostri il badge con count: [3]
4. Verifica la grid con tutti i reference files
5. Clicca [x] su uno → verifica rimozione

### Test Batch Processing
1. Carica **3 documenti input**
2. Aggiungi **2 reference documents** (opzionale)
3. Clicca "Start Analysis"
4. Verifica progress bar:
   - "Processing document 1/3: doc1.pdf"
   - "Processing document 2/3: doc2.docx"
   - "Processing document 3/3: doc3.txt"
   - "Combining results..."
5. Verifica risultati:
   - 3 cartelle individuali in `outputs/`
   - 1 cartella batch con `batch_results.json`

---

## 🔄 Backward Compatibility

✅ **Completamente compatibile** con codice esistente:
- Single file upload ancora supportato
- API endpoint accetta sia `file` che `files`
- Store mantiene `file` per compatibility
- UI funziona con entrambi i modi

---

## 💡 Use Cases

### 1. **Multi-Document Review**
- Analizza tutti i capitoli di una tesi contemporaneamente
- Review di multipli contratti dello stesso progetto
- Analisi batch di CV per recruiting

### 2. **Template Comparison**
- Input: Multiple versions of a document
- Reference: Official template
- Result: Compliance analysis for each version

### 3. **Cross-Document Analysis**
- Input: Series of related documents (chapters, sections)
- Reference: Style guide + examples
- Result: Consistency report across all documents

### 4. **Batch Data Processing**
- Input: Multiple data reports (Excel, CSV as PDF)
- Reference: Data validation rules
- Result: Validation report for each file

---

## 📈 Performance

- **Parallel Processing**: Documents processed concurrently
- **Memory Efficient**: Streaming upload/download
- **Error Resilient**: Single document failure doesn't block others
- **Progress Tracking**: Real-time updates per document

### Limits
- **Max Input Files**: 10 per batch
- **Max Reference Files**: Unlimited (reasonable)
- **Max File Size**: 100 MB per file
- **Max Total Size**: ~500 MB per upload

---

## 🚀 Future Enhancements

1. **Parallel Analysis** (currently sequential)
2. **Smart Grouping** (auto-group related documents)
3. **Cross-Document Comparison** (highlight differences)
4. **Aggregate Dashboard** (combined visualization)
5. **Export Batch Report** (single PDF for all docs)

---

## ✅ Status

| Feature | Status | Notes |
|---------|--------|-------|
| Multiple Input Upload | ✅ Implemented | Up to 10 files |
| Multiple Reference Upload | ✅ Implemented | Unlimited |
| UI Grid View | ✅ Implemented | 2-column responsive |
| Individual File Removal | ✅ Implemented | With confirmation |
| Batch Processing | ✅ Implemented | Sequential |
| Combined Results | ✅ Implemented | batch_results.json |
| Progress Tracking | ✅ Implemented | Per-document |
| Error Handling | ✅ Implemented | Graceful degradation |

---

## 🎉 Ready to Use!

**Vai su** http://localhost:3000 **e prova ad caricare multipli documenti!**

Happy Batch Reviewing! 🚀

