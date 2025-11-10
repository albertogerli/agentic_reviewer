#!/usr/bin/env python3
"""
Test End-to-End per Gamma integration
Simula esattamente il flow del backend quando clicchi "Create Presentation"
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from main import Config
from gamma_integration import create_presentation_from_review


def load_latest_review():
    """Carica l'ultimo review disponibile"""
    outputs_dir = Path("outputs")
    
    if not outputs_dir.exists():
        print("❌ Directory outputs/ non trovata")
        return None, None
    
    # Find latest review directory
    review_dirs = sorted(
        [d for d in outputs_dir.iterdir() if d.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not review_dirs:
        print("❌ Nessuna review trovata in outputs/")
        return None, None
    
    latest_dir = review_dirs[0]
    results_file = latest_dir / "review_results.json"
    
    if not results_file.exists():
        print(f"❌ review_results.json non trovato in {latest_dir}")
        return None, None
    
    print(f"📂 Caricato: {latest_dir.name}")
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return results, latest_dir


def main():
    print("🎨 TEST END-TO-END GAMMA PRESENTATION")
    print("=" * 60)
    
    # 1. Load config
    print("\n1️⃣ Caricamento configurazione...")
    config_path = Path("config.yaml")
    if config_path.exists():
        config = Config.from_yaml(str(config_path))
        gamma_key = config.gamma_api_key
    else:
        gamma_key = os.getenv("GAMMA_API_KEY", "")
    
    if not gamma_key:
        print("❌ Gamma API key non configurata!")
        return 1
    
    print(f"✅ API Key: {gamma_key[:10]}...{gamma_key[-4:]}")
    
    # 2. Load latest review
    print("\n2️⃣ Caricamento ultima review...")
    results, output_dir = load_latest_review()
    
    if not results:
        print("❌ Nessuna review da testare")
        print("\nCrea una review prima:")
        print("  1. Vai su http://localhost:3000")
        print("  2. Carica un documento")
        print("  3. Esegui l'analisi")
        print("  4. Riprova questo test")
        return 1
    
    print(f"✅ Review caricata:")
    print(f"   - Documento: {results.get('document_info', {}).get('title', 'N/A')}")
    print(f"   - Tipo: {results.get('document_info', {}).get('type', 'N/A')}")
    print(f"   - Issues: {len(results.get('structured_issues', []))}")
    print(f"   - Agenti: {len(results.get('agent_reviews', {}))}")
    
    # 3. Create presentation
    print("\n3️⃣ Creazione presentazione...")
    print("   (questo può richiedere 10-30 secondi)")
    
    try:
        start_time = time.time()
        
        presentation_info = create_presentation_from_review(
            review_results=results,
            gamma_api_key=gamma_key,
            output_dir=str(output_dir),
            theme_id=None,  # Let Gamma choose
            export_format="pdf"
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ SUCCESSO! ({elapsed:.1f}s)")
        print(f"   - Generation ID: {presentation_info['generation_id']}")
        print(f"   - Gamma URL: {presentation_info['gamma_url']}")
        print(f"   - Export URL: {presentation_info['export_url']}")
        print(f"   - File locale: {presentation_info['local_path']}")
        
        # Verify file
        if presentation_info['local_path']:
            local_file = Path(presentation_info['local_path'])
            if local_file.exists():
                file_size = local_file.stat().st_size / 1024  # KB
                print(f"   - Dimensione: {file_size:.1f} KB")
                print(f"\n📄 PDF salvato in: {local_file}")
            else:
                print(f"\n⚠️ File non trovato: {local_file}")
        
        print("\n🌐 Apri la presentazione:")
        print(f"   {presentation_info['gamma_url']}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRORE durante creazione:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

