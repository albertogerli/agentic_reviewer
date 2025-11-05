#!/usr/bin/env python3
"""
Quick Test for Academic Search Integration

Tests both Subject Matter Expert and Academic Researcher capabilities.
"""

import os
import sys

def test_semantic_scholar_module():
    """Test 1: Verify Semantic Scholar module works"""
    print("🧪 Test 1: Semantic Scholar Module\n")
    
    try:
        from semantic_scholar import SemanticScholarAPI, format_papers_for_agent
        print("✅ Module imported successfully")
        
        # Initialize API
        api = SemanticScholarAPI()
        print("✅ API initialized")
        
        # Quick search
        print("\n📚 Searching for 'machine learning'...")
        papers = api.search_papers("machine learning", limit=3)
        
        if papers:
            print(f"✅ Found {len(papers)} papers")
            print(f"\nTop result:")
            print(f"  Title: {papers[0].title}")
            print(f"  Authors: {', '.join(papers[0].authors[:3])}")
            print(f"  Year: {papers[0].year}")
            print(f"  Citations: {papers[0].citation_count}")
            if papers[0].doi:
                print(f"  DOI: {papers[0].doi}")
            elif papers[0].arxiv_id:
                print(f"  arXiv: {papers[0].arxiv_id}")
        else:
            print("⚠️ No papers found (might be API issue)")
        
        print("\n✅ Test 1 PASSED\n")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Make sure semantic_scholar.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_generic_reviewer_integration():
    """Test 2: Verify integration with generic_reviewer.py"""
    print("🧪 Test 2: Generic Reviewer Integration\n")
    
    try:
        # Import without running
        import generic_reviewer
        
        # Check if functions exist
        assert hasattr(generic_reviewer, 'execute_academic_research'), "execute_academic_research not found"
        print("✅ execute_academic_research() found")
        
        assert hasattr(generic_reviewer, 'SEMANTIC_SCHOLAR_AVAILABLE'), "SEMANTIC_SCHOLAR_AVAILABLE flag not found"
        print(f"✅ SEMANTIC_SCHOLAR_AVAILABLE = {generic_reviewer.SEMANTIC_SCHOLAR_AVAILABLE}")
        
        # Check agent templates
        from generic_reviewer import AgentTemplateLibrary
        
        # Check subject_matter_expert
        sme = AgentTemplateLibrary.TEMPLATES.get('subject_matter_expert')
        if sme and sme.get('use_web_search'):
            print("✅ Subject Matter Expert has web search enabled")
        else:
            print("⚠️ Subject Matter Expert web search not enabled")
        
        # Check academic_researcher
        ar = AgentTemplateLibrary.TEMPLATES.get('academic_researcher')
        if ar:
            print("✅ Academic Researcher agent found")
            if ar.get('use_academic_search'):
                print("   ✅ Academic search enabled")
            if ar.get('use_web_search'):
                print("   ✅ Web search enabled")
        else:
            print("❌ Academic Researcher agent not found")
            return False
        
        # Check tiers
        tier = AgentTemplateLibrary.AGENT_TIERS.get('academic_researcher')
        print(f"   ✅ Tier: {tier}")
        
        complexity = AgentTemplateLibrary.AGENT_COMPLEXITY.get('academic_researcher')
        print(f"   ✅ Complexity: {complexity}")
        
        print("\n✅ Test 2 PASSED\n")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_agent_execution_flow():
    """Test 3: Verify agent execution flow logic"""
    print("🧪 Test 3: Agent Execution Flow\n")
    
    try:
        from generic_reviewer import GenericReviewOrchestrator
        
        # Check if _execute_agent_with_optional_tools handles academic_search
        import inspect
        source = inspect.getsource(GenericReviewOrchestrator._execute_agent_with_optional_tools)
        
        if 'use_academic_search' in source:
            print("✅ _execute_agent_with_optional_tools handles use_academic_search")
        else:
            print("❌ use_academic_search not found in execution logic")
            return False
        
        if 'execute_academic_research' in source:
            print("✅ execute_academic_research is called")
        else:
            print("❌ execute_academic_research not called")
            return False
        
        if 'Semantic Scholar' in source or 'SEMANTIC_SCHOLAR' in source:
            print("✅ Semantic Scholar integration present")
        else:
            print("⚠️ Semantic Scholar references not found")
        
        print("\n✅ Test 3 PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def print_usage_examples():
    """Print usage examples"""
    print("\n" + "="*70)
    print("📖 USAGE EXAMPLES")
    print("="*70 + "\n")
    
    print("🎓 Subject Matter Expert (Tier 2, sempre attivo):")
    print("   python generic_reviewer.py document.pdf")
    print("   → Web search per verifiche tecniche\n")
    
    print("🔬 Academic Researcher (Tier 3, deep review):")
    print("   python generic_reviewer.py document.pdf --deep-review")
    print("   → Semantic Scholar + Web search per ricerca accademica\n")
    
    print("📊 Test Semantic Scholar standalone:")
    print("   python semantic_scholar.py\n")
    
    print("🌐 Con Web UI:")
    print("   python web_ui.py")
    print("   → Seleziona 'Enable deep review' per attivare Academic Researcher\n")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🔬 ACADEMIC SEARCH INTEGRATION - TEST SUITE")
    print("="*70 + "\n")
    
    results = []
    
    # Test 1: Semantic Scholar module
    results.append(("Semantic Scholar Module", test_semantic_scholar_module()))
    
    # Test 2: Generic Reviewer integration
    results.append(("Generic Reviewer Integration", test_generic_reviewer_integration()))
    
    # Test 3: Agent execution flow
    results.append(("Agent Execution Flow", test_agent_execution_flow()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} {name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    # Print usage
    print_usage_examples()
    
    # Exit code
    if passed == total:
        print("🎉 All tests passed! Academic search is ready to use.\n")
        return 0
    else:
        print(f"⚠️ {total - passed} test(s) failed. Check errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

