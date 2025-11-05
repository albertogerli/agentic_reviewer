# 🔧 Guida Integrazione v3.0

## 🎯 Come Integrare le Nuove Funzionalità

Questa guida spiega come **integrare** le funzionalità v3.0 nel sistema esistente.

---

## 📦 Passo 1: Installazione Dipendenze

```bash
# Vai nella directory del progetto
cd /path/to/project

# Installa dipendenze opzionali
pip install -r requirements_optional.txt

# O installale individualmente
pip install tqdm tabulate pandas openpyxl python-docx
```

### Verifica Installazione

```bash
python3 -c "import tqdm; import tabulate; print('✅ All dependencies installed!')"
```

---

## 🔗 Passo 2: Integrazione nel Codice

### Opzione A: Integrazione Automatica (Consigliata)

Le funzionalità sono **già pronte** nei file creati:

```
document_tracker.py      # Database & persistence ✅
progress_notifier.py     # Progress & notifications ✅
review_history.py        # History CLI ✅
```

**Basta importarle** nel `generic_reviewer.py`:

```python
# All'inizio di generic_reviewer.py, dopo gli altri import:

# Try to import advanced features (optional)
try:
    from document_tracker import DocumentTracker, DocumentVersion
    from progress_notifier import ReviewProgressOrchestrator, SystemNotifier
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    ADVANCED_FEATURES_AVAILABLE = False
    logger.warning("Advanced features not available. Install: pip install tqdm tabulate")
```

### Opzione B: Integrazione Manuale

Se preferisci integrare manualmente, segui questi step:

#### Step 1: Inizializza Tracker nel `main()`

```python
def main():
    # ... existing code ...
    
    # Initialize document tracker
    if ADVANCED_FEATURES_AVAILABLE:
        tracker = DocumentTracker()
        doc_hash = tracker.compute_document_hash(document_text)
        
        # Check for existing history
        history = tracker.get_document_history(doc_hash)
        if history:
            logger.info(f"📚 Found {len(history)} previous versions of this document")
    else:
        tracker = None
        doc_hash = None
```

#### Step 2: Inizializza Progress nel Review

```python
async def execute_iterative_review(...):
    # ... existing code ...
    
    # Initialize progress tracking
    if ADVANCED_FEATURES_AVAILABLE:
        progress = ReviewProgressOrchestrator(
            document_title=title,
            mode="iterative",
            max_iterations=max_iterations,
            enable_notifications=True
        )
        progress.start()
    else:
        progress = None
    
    # ... rest of code ...
```

#### Step 3: Aggiorna Progress Durante Review

```python
# Durante le varie fasi:

if progress:
    progress.start_phase("Document Classification")

# ... do classification ...

if progress:
    progress.update(5, "Classification complete")
    progress.complete_phase()

# Per ogni iterazione:
for iteration in range(1, max_iterations + 1):
    if progress:
        progress.start_phase(f"Iteration {iteration}: Review")
    
    # ... do review ...
    
    if progress:
        progress.update(steps, f"Reviewing with {len(agents)} agents")
    
    # ... do improvement ...
    
    if progress:
        progress.complete_phase()
        progress.notify_iteration_complete(iteration, current_score)
```

#### Step 4: Salva Checkpoint

```python
# Dopo ogni iterazione:
if tracker and iteration < max_iterations:
    checkpoint_id = f"checkpoint_{doc_hash}_{iteration}"
    state_data = {
        "document_text": current_document,
        "reviews": reviews,
        "scores": scores_history,
        "improvements": improvements_applied
    }
    
    tracker.save_checkpoint(
        checkpoint_id=checkpoint_id,
        document_hash=doc_hash,
        document_title=title,
        current_iteration=iteration,
        current_phase="Review Complete",
        state_data=state_data
    )
    
    if progress:
        progress.notify_checkpoint(iteration)
```

#### Step 5: Salva Version Finale

```python
# Alla fine della review:
if tracker:
    version = DocumentVersion(
        version_id=f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        document_hash=doc_hash,
        document_title=title,
        project_name=args.project if hasattr(args, 'project') else None,
        review_date=datetime.now().isoformat(),
        score=final_score,
        iteration_number=total_iterations,
        file_path=args.document_path,
        output_directory=config.output_dir,
        review_mode="iterative" if args.iterative else "standard",
        language=output_language,
        improvements_applied=len(all_improvements),
        critical_issues=critical_count,
        moderate_issues=moderate_count,
        minor_issues=minor_count,
        agent_count=agent_count,
        metadata=json.dumps({"target_score": args.target_score})
    )
    
    tracker.save_version(version)
    logger.info(f"✅ Version saved to database: {version.version_id}")

if progress:
    progress.complete(final_score)
```

#### Step 6: Gestione Errori

```python
try:
    # ... review process ...
except KeyboardInterrupt:
    logger.info("🛑 Review interrupted by user")
    
    # Save checkpoint
    if tracker:
        # ... save checkpoint code ...
    
    if progress:
        progress.notify_checkpoint(current_iteration)
        progress.close()
    
    return 1

except Exception as e:
    logger.error(f"❌ Error: {e}")
    
    if progress:
        progress.notify_error(str(e))
        progress.close()
    
    return 1
```

---

## 🎮 Passo 3: Aggiungi Argomenti CLI

Aggiungi al parser argparse:

```python
# In main()
parser = argparse.ArgumentParser(...)

# Existing arguments...

# New arguments for v3.0
parser.add_argument("--project", 
                   help="Project name for grouping related reviews")

parser.add_argument("--resume", 
                   help="Resume from checkpoint ID")

parser.add_argument("--no-notifications", 
                   action="store_true",
                   help="Disable system notifications")

parser.add_argument("--no-progress", 
                   action="store_true",
                   help="Disable progress bars")
```

---

## 🧪 Passo 4: Testing

### Test 1: Progress Bar

```bash
python3 generic_reviewer.py test_doc.pdf --iterative

# Dovresti vedere:
Overall Progress |████░░░░░░░░░░░░░░░░| 20%
  └─ Iteration 1: Review |██████░░░░| 60%
```

### Test 2: Notifiche

```bash
python3 generic_reviewer.py test_doc.pdf --iterative

# Lancia e vai su altro
# Dovresti ricevere notifica quando finisce
```

### Test 3: Checkpoint

```bash
# Start review
python3 generic_reviewer.py test_doc.pdf \
    --iterative \
    --max-iterations 5

# Dopo 1-2 iterazioni, premi Ctrl+C

# Dovrebbe salvare checkpoint
💾 Checkpoint saved: checkpoint_abc123

# Resume
python3 generic_reviewer.py --resume checkpoint_abc123

# Dovrebbe continuare da dove interrotto
```

### Test 4: Database

```bash
# Dopo alcune review
python3 review_history.py recent

# Dovresti vedere la lista
```

### Test 5: Project Tracking

```bash
# Prima review
python3 generic_reviewer.py doc_v1.pdf --project "Test Project"

# Seconda review
python3 generic_reviewer.py doc_v2.pdf --project "Test Project"

# Vedi storia
python3 review_history.py project "Test Project"

# Dovresti vedere entrambe le versioni
```

---

## 🎯 Passo 5: Verifica Completa

Script di test automatico:

```bash
#!/bin/bash
# test_v3_features.sh

echo "🧪 Testing v3.0 Features..."
echo ""

# Test 1: Dependencies
echo "1️⃣ Testing dependencies..."
python3 -c "import tqdm, tabulate; print('✅ Dependencies OK')" || exit 1
echo ""

# Test 2: Database init
echo "2️⃣ Testing database..."
python3 -c "from document_tracker import DocumentTracker; t=DocumentTracker('test.db'); print('✅ Database OK')"
rm test.db
echo ""

# Test 3: Progress (dry run)
echo "3️⃣ Testing progress..."
python3 -c "from progress_notifier import ProgressTracker; p=ProgressTracker(10); p.start(); p.update(5); p.complete(); print('✅ Progress OK')"
echo ""

# Test 4: CLI tool
echo "4️⃣ Testing history CLI..."
python3 review_history.py --help > /dev/null && echo "✅ History CLI OK" || exit 1
echo ""

echo "🎉 All tests passed!"
```

Esegui:

```bash
chmod +x test_v3_features.sh
./test_v3_features.sh
```

---

## 📊 Esempio Completo di Integrazione

```python
#!/usr/bin/env python3
"""
Example integration of v3.0 features into generic_reviewer.py
"""

import asyncio
from datetime import datetime
import json

# Try import advanced features
try:
    from document_tracker import DocumentTracker, DocumentVersion
    from progress_notifier import ReviewProgressOrchestrator
    ADVANCED_FEATURES = True
except:
    ADVANCED_FEATURES = False

async def review_with_v3_features(document_path, args):
    """Example review function with all v3.0 features."""
    
    # Read document
    with open(document_path) as f:
        document_text = f.read()
    
    # Initialize v3 components
    tracker = None
    progress = None
    doc_hash = None
    
    if ADVANCED_FEATURES:
        # Database
        tracker = DocumentTracker()
        doc_hash = tracker.compute_document_hash(document_text)
        
        # Check history
        history = tracker.get_document_history(doc_hash)
        if history:
            print(f"📚 Found {len(history)} previous versions")
            print(f"   Last score: {history[0].score:.1f}/100")
        
        # Progress tracking
        progress = ReviewProgressOrchestrator(
            document_title=args.title,
            mode="iterative",
            max_iterations=args.max_iterations,
            enable_notifications=not args.no_notifications
        )
        progress.start()
    
    try:
        # Phase 1: Classification
        if progress:
            progress.start_phase("Document Classification")
        
        # ... do classification ...
        await asyncio.sleep(2)  # Simulated work
        
        if progress:
            progress.update(10, "Classification complete")
            progress.complete_phase()
        
        # Phase 2: Iterative review
        scores = []
        
        for iteration in range(1, args.max_iterations + 1):
            # Review phase
            if progress:
                progress.start_phase(f"Iteration {iteration}: Review")
            
            # ... do review ...
            await asyncio.sleep(3)  # Simulated work
            score = 60 + iteration * 8  # Simulated score improvement
            scores.append(score)
            
            if progress:
                progress.update(15, f"Review complete - Score: {score}/100")
                progress.complete_phase()
            
            # Improvement phase
            if iteration < args.max_iterations:
                if progress:
                    progress.start_phase(f"Iteration {iteration}: Improve")
                
                # ... do improvement ...
                await asyncio.sleep(2)  # Simulated work
                
                if progress:
                    progress.update(15, "Improvements applied")
                    progress.complete_phase()
                    progress.notify_iteration_complete(iteration, score)
                
                # Save checkpoint
                if tracker:
                    checkpoint_id = f"checkpoint_{doc_hash}_{iteration}"
                    tracker.save_checkpoint(
                        checkpoint_id=checkpoint_id,
                        document_hash=doc_hash,
                        document_title=args.title,
                        current_iteration=iteration,
                        current_phase="Improvement Complete",
                        state_data={"scores": scores}
                    )
                    print(f"💾 Checkpoint saved: {checkpoint_id}")
        
        # Final score
        final_score = scores[-1]
        
        # Save to database
        if tracker:
            version = DocumentVersion(
                version_id=f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                document_hash=doc_hash,
                document_title=args.title,
                project_name=args.project,
                review_date=datetime.now().isoformat(),
                score=final_score,
                iteration_number=args.max_iterations,
                file_path=document_path,
                output_directory="./output",
                review_mode="iterative",
                language="English",
                improvements_applied=args.max_iterations - 1,
                critical_issues=0,
                moderate_issues=2,
                minor_issues=5,
                agent_count=6,
                metadata=json.dumps({"target": args.target_score})
            )
            tracker.save_version(version)
            print(f"✅ Version saved: {version.version_id}")
        
        # Complete
        if progress:
            progress.complete(final_score)
        
        print(f"\n🎉 Review complete! Final score: {final_score}/100")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted - saving checkpoint...")
        if progress:
            progress.notify_checkpoint(iteration)
        raise
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if progress:
            progress.notify_error(str(e))
        raise


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("document")
    parser.add_argument("--title", default="Test Document")
    parser.add_argument("--project", default="Test Project")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--target-score", type=float, default=85.0)
    parser.add_argument("--no-notifications", action="store_true")
    
    args = parser.parse_args()
    
    asyncio.run(review_with_v3_features(args.document, args))
```

---

## 🚀 Quick Start (Dopo Integrazione)

```bash
# Test completo
python3 generic_reviewer.py documento.pdf \
    --iterative \
    --interactive \
    --project "My Important Project" \
    --max-iterations 5 \
    --target-score 90

# Vedrai:
✅ Progress bar real-time
✅ Notifiche a ogni milestone
✅ Checkpoint automatici
✅ Database tracking
✅ Storia progetto

# Dopo, vedi storia:
python3 review_history.py project "My Important Project"

# O recent reviews:
python3 review_history.py recent

# O statistiche:
python3 review_history.py stats
```

---

## ⚠️ Troubleshooting

### Problema: Import Error

```python
ImportError: No module named 'tqdm'
```

**Soluzione:**
```bash
pip install tqdm tabulate
```

### Problema: Database Locked

```
sqlite3.OperationalError: database is locked
```

**Soluzione:**
```bash
# Chiudi altre istanze
pkill -f generic_reviewer.py

# O usa database diverso
python3 generic_reviewer.py --db-path another.db
```

### Problema: Notifiche Non Funzionano (Linux)

```bash
# Installa notify-send
sudo apt-get install libnotify-bin
```

### Problema: Progress Bar Distorta

```bash
# Usa terminale più largo o disabilita
python3 generic_reviewer.py --no-progress
```

---

## 📚 Riferimenti

- `document_tracker.py` - Database API
- `progress_notifier.py` - Progress & notifications API
- `review_history.py` - CLI tool
- `FUNZIONALITA_AVANZATE.md` - User documentation
- `requirements_optional.txt` - Dependencies

---

## ✅ Checklist Integrazione

- [ ] Dipendenze installate (`pip install -r requirements_optional.txt`)
- [ ] Import aggiunti in `generic_reviewer.py`
- [ ] Tracker inizializzato nel `main()`
- [ ] Progress orchestrator creato per review
- [ ] Progress aggiornato durante fasi
- [ ] Checkpoint salvati dopo iterazioni
- [ ] Version salvata a fine review
- [ ] Gestione errori e interruzioni
- [ ] Argomenti CLI aggiunti
- [ ] Test eseguiti e passati

---

**Integrazione completa! Sistema ora con tracking e resilienza! 🚀**

