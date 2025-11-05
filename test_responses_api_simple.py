#!/usr/bin/env python3
"""
Test semplice per Responses API con gpt-5.
Basato sull'esempio fornito dall'utente.
"""

from openai import OpenAI
import os
import sys

# Verifica API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY not set")
    sys.exit(1)

print("╔═══════════════════════════════════════════════════════════╗")
print("║  🧪 TEST RESPONSES API CON GPT-5                         ║")
print("╚═══════════════════════════════════════════════════════════╝\n")

client = OpenAI(api_key=api_key)

SYSTEM = (
    "Sei un analista. Quando usi il web search, cita sempre le fonti "
    "in fondo alla risposta."
)

# Test con gpt-5
print("━" * 60)
print("TEST 1: Web Search con gpt-5")
print("━" * 60)

try:
    print("🔍 Cercando: 'Ultime novità LED Europa 2025'...")
    
    # Chiamata con gpt-5 (come nel sistema)
    resp = client.responses.create(
        model="gpt-5",  # USA GPT-5!
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Trova le ultime novità sul mercato LED in Europa nel 2025 "
                            "e sintetizza in 5 bullet con fonti."
                        ),
                    }
                ],
            },
        ],
        tools=[{"type": "web_search"}],
    )
    
    print(f"✅ Risposta ricevuta! ID: {resp.id}")
    
    # Estrai messaggio
    msg = next((o for o in resp.output if getattr(o, "type", None) == "message"), None)
    
    if not msg:
        print("⚠️ Nessun messaggio nella risposta!")
        print(f"Output: {resp.output}")
        sys.exit(1)
    
    # Estrai testo e citazioni
    text = ""
    urls = []
    if msg and msg.content:
        block = msg.content[0]
        text = getattr(block, "text", "") or getattr(block, "value", "")
        ann = getattr(block, "annotations", []) or []
        urls = [a.url for a in ann if getattr(a, "type", "") == "url_citation"]
    
    print("\n📝 RISPOSTA:\n")
    print(text)
    
    if urls:
        print(f"\n📚 FONTI ({len(urls)}):")
        for i, u in enumerate(urls, 1):
            print(f"  {i}. {u}")
    else:
        print("\n⚠️ Nessuna fonte trovata")
    
    print("\n" + "━" * 60)
    print("✅ TEST COMPLETATO CON SUCCESSO!")
    print("━" * 60)
    
except Exception as e:
    import traceback
    print(f"\n❌ ERRORE: {e}\n")
    print("TRACEBACK:")
    print(traceback.format_exc())
    print("\n" + "━" * 60)
    print("⚠️ POSSIBILI CAUSE:")
    print("━" * 60)
    print("1. gpt-5 potrebbe non supportare Responses API")
    print("2. Responses API potrebbe essere in beta/non disponibile")
    print("3. Account potrebbe non avere accesso")
    print("\n💡 SOLUZIONE:")
    print("   Sistema userà Tavily come fallback automatico")
    print("   pip install tavily-python")
    print("   export TAVILY_API_KEY='tvly-...'")
    sys.exit(1)


# Test con gpt-5-mini
print("\n" + "━" * 60)
print("TEST 2: Web Search con gpt-5-mini")
print("━" * 60)

try:
    print("🔍 Cercando con gpt-5-mini...")
    
    resp = client.responses.create(
        model="gpt-5-mini",
        input="Qual è la temperatura media globale nel 2024? Cita fonti.",
        tools=[{"type": "web_search"}],
    )
    
    msg = next((o for o in resp.output if getattr(o, "type", None) == "message"), None)
    if msg and msg.content:
        text = msg.content[0].text
        print(f"✅ Risposta ricevuta ({len(text)} chars)")
        print(text[:200] + "..." if len(text) > 200 else text)
    
except Exception as e:
    print(f"⚠️ gpt-5-mini fallito: {e}")


print("\n" + "━" * 60)
print("🎯 CONCLUSIONE")
print("━" * 60)
print("Se vedi errori sopra:")
print("  → Responses API potrebbe non supportare gpt-5")
print("  → Sistema userà automaticamente Tavily fallback")
print("  → Web search funzionerà comunque!")
print("\nSe funziona:")
print("  → ✅ Perfetto! gpt-5 supporta Responses API")
print("  → Web search nativo funzionante")
print("━" * 60)

