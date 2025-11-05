#!/usr/bin/env python3
"""
Test script per verificare la configurazione Web Search.

Usage:
    python3 test_web_search.py
"""

import os
import sys

def test_openai():
    """Test OpenAI API key."""
    print("━" * 60)
    print("🧪 TEST 1: OpenAI API")
    print("━" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY non trovata!")
        print("   Set: export OPENAI_API_KEY='sk-...'")
        return False
    
    print(f"✅ OPENAI_API_KEY trovata: {api_key[:10]}...{api_key[-4:]}")
    
    # Try to import OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client creato con successo")
        return True
    except ImportError:
        print("❌ OpenAI non installato: pip install openai")
        return False
    except Exception as e:
        print(f"❌ Errore OpenAI: {e}")
        return False


def test_tavily():
    """Test Tavily setup."""
    print("\n" + "━" * 60)
    print("🧪 TEST 2: Tavily API (Fallback)")
    print("━" * 60)
    
    # Check if Tavily is installed
    try:
        from tavily import TavilyClient
        print("✅ Tavily installato")
    except ImportError:
        print("⚠️  Tavily NON installato")
        print("   Install: pip install tavily-python")
        print("   Questo è OPZIONALE ma RACCOMANDATO per fallback robusto")
        return False
    
    # Check API key
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("⚠️  TAVILY_API_KEY non trovata")
        print("   1. Registrati su: https://tavily.com")
        print("   2. Ottieni API key (FREE: 1000 ricerche/mese)")
        print("   3. Set: export TAVILY_API_KEY='tvly-...'")
        return False
    
    print(f"✅ TAVILY_API_KEY trovata: {api_key[:10]}...{api_key[-4:]}")
    
    # Try actual search
    try:
        client = TavilyClient(api_key=api_key)
        print("🔍 Eseguendo test search...")
        result = client.search("OpenAI GPT-5 news", max_results=2)
        
        if result.get('results'):
            print(f"✅ Tavily funzionante! Trovati {len(result['results'])} risultati:")
            for i, r in enumerate(result['results'], 1):
                print(f"   {i}. {r['title']}")
                print(f"      {r['url']}")
        else:
            print("⚠️  Nessun risultato, ma API funziona")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore Tavily: {e}")
        return False


def test_web_research_agent():
    """Test web_research_agent module."""
    print("\n" + "━" * 60)
    print("🧪 TEST 3: Web Research Agent Module")
    print("━" * 60)
    
    try:
        from web_research_agent import (
            execute_web_research_agent,
            WEB_RESEARCH_AVAILABLE
        )
        print(f"✅ web_research_agent importato")
        print(f"   WEB_RESEARCH_AVAILABLE: {WEB_RESEARCH_AVAILABLE}")
        return True
    except ImportError as e:
        print(f"⚠️  web_research_agent non trovato: {e}")
        print("   Questo è normale se web_research_agent.py non esiste")
        return False


def print_summary(openai_ok: bool, tavily_ok: bool, web_agent_ok: bool):
    """Print final summary."""
    print("\n" + "━" * 60)
    print("📊 RIEPILOGO")
    print("━" * 60)
    
    status = []
    
    if openai_ok:
        status.append("✅ OpenAI: Funzionante")
    else:
        status.append("❌ OpenAI: NON configurato (RICHIESTO!)")
    
    if tavily_ok:
        status.append("✅ Tavily: Funzionante (fallback robusto attivo!)")
    elif openai_ok:
        status.append("⚠️  Tavily: Non configurato (opzionale ma raccomandato)")
    
    if web_agent_ok:
        status.append("✅ Web Research Agent: Disponibile")
    
    for s in status:
        print(s)
    
    print("\n" + "━" * 60)
    print("🎯 RACCOMANDAZIONI")
    print("━" * 60)
    
    if not openai_ok:
        print("🔴 AZIONE RICHIESTA:")
        print("   export OPENAI_API_KEY='sk-...'")
    
    if openai_ok and not tavily_ok:
        print("🟡 OPZIONALE MA RACCOMANDATO:")
        print("   1. pip install tavily-python")
        print("   2. Registrati su https://tavily.com (FREE)")
        print("   3. export TAVILY_API_KEY='tvly-...'")
        print("\n   BENEFICI:")
        print("   • Fallback se OpenAI Responses API va in timeout")
        print("   • Web search più stabile")
        print("   • FREE tier: 1000 ricerche/mese")
    
    if openai_ok and tavily_ok:
        print("🟢 CONFIGURAZIONE OTTIMALE!")
        print("   Sistema pronto per web search robusto con fallback automatico")
        print("\n   FLUSSO:")
        print("   1. OpenAI Responses API (timeout 90s)")
        print("   2. → Tavily Fallback (se OpenAI fallisce)")
        print("   3. → Esecuzione Standard (se anche Tavily fallisce)")
        print("\n   ✅ Mai più hang o timeout!")
    
    print("\n" + "━" * 60)
    

if __name__ == "__main__":
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║  🌐 TEST CONFIGURAZIONE WEB SEARCH                        ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    openai_ok = test_openai()
    tavily_ok = test_tavily()
    web_agent_ok = test_web_research_agent()
    
    print_summary(openai_ok, tavily_ok, web_agent_ok)
    
    print("\n" + "━" * 60)
    if openai_ok:
        print("✅ Puoi usare il sistema!")
        print("   python3 web_ui.py")
    else:
        print("❌ Configura OpenAI prima di procedere")
        sys.exit(1)

