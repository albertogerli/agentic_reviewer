#!/usr/bin/env python3
"""
Test e debug per Gamma API integration
Verifica la configurazione e testa diverse richieste
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import Config
from gamma_integration import GammaPresentationGenerator, GammaConfig


def test_api_key():
    """Test 1: Verifica che l'API key sia configurata"""
    print("=" * 60)
    print("TEST 1: Verifica API Key")
    print("=" * 60)
    
    # Check environment
    env_key = os.getenv("GAMMA_API_KEY", "")
    print(f"GAMMA_API_KEY (env): {'✅ Presente' if env_key else '❌ Non trovata'}")
    
    # Check config.yaml
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        try:
            config = Config.from_yaml(str(config_path))
            config_key = config.gamma_api_key
            print(f"gamma_api_key (config.yaml): {'✅ Presente' if config_key else '❌ Non trovata'}")
        except Exception as e:
            print(f"⚠️ Errore lettura config.yaml: {e}")
            config_key = ""
    else:
        print("⚠️ config.yaml non trovato")
        config_key = ""
    
    # Final key
    final_key = env_key or config_key
    
    if not final_key:
        print("\n❌ ERRORE: Gamma API key non configurata!")
        print("\nCome configurare:")
        print("1. Vai su https://gamma.app/settings/api")
        print("2. Crea una nuova API key")
        print("3. Aggiungi al config.yaml: gamma_api_key: 'tua_key_qui'")
        print("   OPPURE")
        print("   export GAMMA_API_KEY='tua_key_qui'")
        return None
    
    print(f"\n✅ API Key configurata: {final_key[:10]}...{final_key[-4:]}")
    return final_key


def test_minimal_request(api_key: str):
    """Test 2: Request minima per verificare API"""
    print("\n" + "=" * 60)
    print("TEST 2: Request Minima")
    print("=" * 60)
    
    # Payload minimo assoluto
    minimal_payload = {
        "inputText": "# Test Slide\nThis is a test presentation."
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print("📤 Payload minimo:")
    print(json.dumps(minimal_payload, indent=2))
    
    try:
        response = requests.post(
            "https://public-api.gamma.app/v1.0/generations",
            headers=headers,
            json=minimal_payload,
            timeout=10
        )
        
        print(f"\n📥 Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Request minima funziona!")
            return True
        else:
            print(f"❌ Errore {response.status_code}")
            try:
                error_data = response.json()
                print(f"Dettagli errore: {json.dumps(error_data, indent=2)}")
            except:
                pass
            return False
            
    except Exception as e:
        print(f"❌ Eccezione: {e}")
        return False


def test_full_payload(api_key: str):
    """Test 3: Payload completo come nel codice"""
    print("\n" + "=" * 60)
    print("TEST 3: Payload Completo")
    print("=" * 60)
    
    full_payload = {
        "inputText": """# Test Presentation
AI-Powered Document Review
Comprehensive test presentation

---

# Executive Summary
This is a test of the Gamma API integration.
* Test bullet 1
* Test bullet 2

---

# Conclusion
Testing complete.""",
        "textMode": "preserve",
        "format": "presentation",
        "themeId": "Oasis",
        "numCards": 3,
        "cardSplit": "inputTextBreaks",
        "exportAs": "pdf",
        "textOptions": {
            "amount": "detailed",
            "language": "en"
        },
        "imageOptions": {
            "source": "aiGenerated",
            "model": "imagen-4-pro",
            "style": "professional, modern, clean, business"
        },
        "cardOptions": {
            "dimensions": "16x9",
            "headerFooter": {
                "topRight": {
                    "type": "text",
                    "value": "AI Document Review"
                },
                "bottomRight": {
                    "type": "cardNumber"
                },
                "hideFromFirstCard": True
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    
    print("📤 Payload completo (primi 500 char):")
    print(json.dumps(full_payload, indent=2)[:500])
    print("...")
    
    try:
        response = requests.post(
            "https://public-api.gamma.app/v1.0/generations",
            headers=headers,
            json=full_payload,
            timeout=10
        )
        
        print(f"\n📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request completa funziona!")
            print(f"Generation ID: {result.get('generationId')}")
            return result.get('generationId')
        else:
            print(f"❌ Errore {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to identify the problematic field
            print("\n🔍 Testing payload fields individually...")
            
            # Test without each optional section
            test_without = [
                ("imageOptions", ["imageOptions"]),
                ("cardOptions", ["cardOptions"]),
                ("textOptions", ["textOptions"]),
                ("themeId", ["themeId"]),
                ("exportAs", ["exportAs"]),
            ]
            
            for name, fields in test_without:
                test_payload = full_payload.copy()
                for field in fields:
                    if field in test_payload:
                        del test_payload[field]
                
                try:
                    test_resp = requests.post(
                        "https://public-api.gamma.app/v1.0/generations",
                        headers=headers,
                        json=test_payload,
                        timeout=10
                    )
                    print(f"  Without {name}: {test_resp.status_code}")
                except Exception as e:
                    print(f"  Without {name}: Exception - {e}")
            
            return None
            
    except Exception as e:
        print(f"❌ Eccezione: {e}")
        return None


def test_gamma_class(api_key: str):
    """Test 4: Test con la classe GammaPresentationGenerator"""
    print("\n" + "=" * 60)
    print("TEST 4: Classe GammaPresentationGenerator")
    print("=" * 60)
    
    sample_results = {
        "document_info": {
            "title": "Test Document",
            "type": "test"
        },
        "final_evaluation": "Test evaluation.",
        "structured_issues": [
            {
                "severity": "high",
                "title": "Test Issue",
                "description": "Test description",
                "location": "Test location",
                "suggestion": "Test suggestion"
            }
        ],
        "risk_heatmap": {
            "test_category": 50
        },
        "agent_reviews": {
            "test_agent": "Test review"
        }
    }
    
    try:
        generator = GammaPresentationGenerator(api_key)
        
        # Test formatting
        formatted = generator.format_review_for_gamma(sample_results)
        print("📄 Formatted text (primi 300 char):")
        print(formatted[:300])
        print("...")
        
        # Test creation with minimal config
        config = GammaConfig(
            api_key=api_key,
            theme_id=None,  # No theme
            num_cards=3,
            export_as="pdf"
        )
        
        print("\n🎨 Tentativo creazione presentazione...")
        result = generator.create_presentation(sample_results, config)
        
        print(f"✅ Successo! Generation ID: {result.get('generationId')}")
        return result.get('generationId')
        
    except Exception as e:
        print(f"❌ Errore nella classe: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests"""
    print("\n🧪 GAMMA API DEBUG TEST SUITE")
    print("=" * 60)
    
    # Test 1: API Key
    api_key = test_api_key()
    if not api_key:
        print("\n❌ Test interrotti: API key mancante")
        return 1
    
    # Test 2: Minimal request
    minimal_ok = test_minimal_request(api_key)
    
    # Test 3: Full payload
    generation_id = test_full_payload(api_key)
    
    # Test 4: Python class
    class_generation_id = test_gamma_class(api_key)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO TEST")
    print("=" * 60)
    print(f"API Key: {'✅' if api_key else '❌'}")
    print(f"Request Minima: {'✅' if minimal_ok else '❌'}")
    print(f"Request Completa: {'✅' if generation_id else '❌'}")
    print(f"Classe Python: {'✅' if class_generation_id else '❌'}")
    
    if class_generation_id:
        print("\n✅ TUTTI I TEST PASSATI!")
        print(f"Generation ID: {class_generation_id}")
        print("\nPuoi verificare lo stato con:")
        print(f"curl -H 'X-API-KEY: {api_key[:10]}...' \\")
        print(f"  https://public-api.gamma.app/v1.0/generations/{class_generation_id}")
        return 0
    else:
        print("\n⚠️ ALCUNI TEST FALLITI")
        return 1


if __name__ == "__main__":
    sys.exit(main())

