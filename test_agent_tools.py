#!/usr/bin/env python3
"""
Test script for Agent Tools with real Python execution.
Demonstrates how Data Validator can actually execute code to verify claims.
"""

import asyncio
import os
from openai import AsyncOpenAI
from agent_tools import (
    get_tool_registry,
    execute_agent_with_tools,
    create_data_validator_instructions_with_tools,
    SafePythonExecutor
)


async def test_safe_python_executor():
    """Test the safe Python executor."""
    print("\n" + "="*80)
    print("TEST 1: Safe Python Executor")
    print("="*80)
    
    executor = SafePythonExecutor()
    
    # Test 1: Simple calculation
    print("\n🧪 Test 1a: Simple calculation")
    code1 = """
initial = 1000000
final = 2500000
growth = ((final - initial) / initial) * 100
result = growth
"""
    result1 = executor.execute(code1)
    print(f"Code:\n{code1}")
    print(f"Result: {result1.output if result1.success else result1.error}")
    print(f"✅ Success" if result1.success else "❌ Failed")
    
    # Test 2: Data consistency check
    print("\n🧪 Test 1b: Data consistency")
    code2 = """
parts_sum = sum([Q1, Q2, Q3, Q4])
is_consistent = abs(parts_sum - Annual) < 0.01
result = {
    'parts_sum': parts_sum,
    'annual': Annual,
    'consistent': is_consistent,
    'difference': parts_sum - Annual
}
"""
    context = {"Q1": 1.2, "Q2": 1.5, "Q3": 1.8, "Q4": 2.1, "Annual": 6.6}
    result2 = executor.execute(code2, context=context)
    print(f"Context: {context}")
    print(f"Code:\n{code2}")
    print(f"Result: {result2.output if result2.success else result2.error}")
    print(f"✅ Success" if result2.success else "❌ Failed")
    
    # Test 3: Unsafe code (should be rejected)
    print("\n🧪 Test 1c: Unsafe code rejection")
    unsafe_code = "import os; os.system('ls')"
    result3 = executor.execute(unsafe_code)
    print(f"Code: {unsafe_code}")
    print(f"Result: {result3.error if not result3.success else 'Should have been blocked!'}")
    print(f"✅ Correctly blocked" if not result3.success else "❌ Should have been blocked!")


async def test_tool_registry():
    """Test the tool registry."""
    print("\n" + "="*80)
    print("TEST 2: Tool Registry")
    print("="*80)
    
    registry = get_tool_registry()
    
    # Test 1: List available tools
    print("\n🧪 Test 2a: Available tools")
    schemas = registry.get_tool_schemas()
    print(f"Registered tools: {len(schemas)}")
    for tool in schemas:
        print(f"  - {tool['function']['name']}: {tool['function']['description'][:60]}...")
    
    # Test 2: Execute validate_calculation tool
    print("\n🧪 Test 2b: Execute validate_calculation")
    result = registry.execute_tool(
        "validate_calculation",
        {
            "description": "Verify 150% growth from €1M to €2.5M",
            "code": "initial = 1000000; final = 2500000; growth = ((final - initial) / initial) * 100; result = growth"
        }
    )
    print(f"Result: {result.output if result.success else result.error}")
    print(f"✅ Success (growth = {result.output}%)" if result.success else "❌ Failed")
    
    # Test 3: Execute analyze_data_consistency tool
    print("\n🧪 Test 2c: Execute analyze_data_consistency")
    result = registry.execute_tool(
        "analyze_data_consistency",
        {
            "description": "Check if Q1-Q4 sum to Annual",
            "data": {"Q1": 1.2, "Q2": 1.5, "Q3": 1.8, "Q4": 2.1, "Annual": 6.6},
            "code": "parts = [Q1, Q2, Q3, Q4]; total = sum(parts); result = abs(total - Annual) < 0.01"
        }
    )
    print(f"Result: {result.output if result.success else result.error}")
    print(f"✅ Success (consistent = {result.output})" if result.success else "❌ Failed")
    
    # Test 4: Execute calculate_statistics tool
    print("\n🧪 Test 2d: Execute calculate_statistics")
    result = registry.execute_tool(
        "calculate_statistics",
        {
            "data": [12, 15, 18, 14, 16, 13],
            "operations": ["mean", "median", "min", "max"]
        }
    )
    print(f"Result: {result.output if result.success else result.error}")
    print(f"✅ Success" if result.success else "❌ Failed")


async def test_agent_with_tools():
    """Test agent execution with real tool calling."""
    print("\n" + "="*80)
    print("TEST 3: Agent with Tool Calling (REQUIRES OPENAI_API_KEY)")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  OPENAI_API_KEY not set, skipping agent test")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    # Document excerpt with numerical claims
    document_excerpt = """
# Business Plan - Q4 2024

## Financial Projections

Our revenue has shown exceptional growth:
- Q1 2024: €1,200,000
- Q2 2024: €1,500,000  
- Q3 2024: €1,800,000
- Q4 2024 (projected): €2,100,000

**Annual Total: €6,600,000**

This represents a 150% growth from our 2023 revenue of €1,000,000.

## Market Share

We currently hold 12% market share, which is calculated as:
Market Share = (Our Revenue / Total Market) × 100
Market Share = (€6.6M / €55M) × 100 = 12%

## Customer Metrics

- Average deal size: €500/month
- Customer lifetime (avg): 24 months
- LTV = €500 × 24 = €12,000
- CAC = €200
- LTV/CAC ratio = €12,000 / €200 = 60x

This 60x ratio shows excellent unit economics!
"""
    
    print(f"\n📄 Document excerpt ({len(document_excerpt)} chars)")
    print("-" * 80)
    print(document_excerpt[:500] + "..." if len(document_excerpt) > 500 else document_excerpt)
    print("-" * 80)
    
    # Create messages for data validator
    messages = [
        {
            "role": "system",
            "content": create_data_validator_instructions_with_tools()
        },
        {
            "role": "user",
            "content": f"""Please validate ALL numerical claims and calculations in this document.

Use your tools to verify:
1. Are the Q1-Q4 numbers correct and sum to the annual total?
2. Is the 150% growth calculation correct?
3. Is the market share calculation (12%) correct?
4. Is the LTV calculation (€12,000) correct?
5. Is the LTV/CAC ratio (60x) correct?

IMPORTANT: Actually CALL THE TOOLS to verify each claim!

DOCUMENT:
{document_excerpt}"""
        }
    ]
    
    print("\n🤖 Running Data Validator Agent with Tools...")
    print("   This will take 30-60 seconds as agent calls multiple tools...")
    
    try:
        # Note: For async, we'd need to adapt execute_agent_with_tools
        # For now, using sync version
        from openai import OpenAI
        sync_client = OpenAI(api_key=api_key)
        
        response = execute_agent_with_tools(
            client=sync_client,
            model="gpt-4o-mini",  # or gpt-4
            messages=messages,
            max_tool_iterations=10
        )
        
        print("\n" + "="*80)
        print("AGENT RESPONSE (with real Python execution!)")
        print("="*80)
        print(response)
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_incorrect_calculation():
    """Test agent detecting an incorrect calculation."""
    print("\n" + "="*80)
    print("TEST 4: Detect Incorrect Calculation")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  OPENAI_API_KEY not set, skipping test")
        return
    
    # Document with WRONG calculation
    doc_with_error = """
# Financial Report

Revenue increased from €1,000,000 in 2023 to €2,500,000 in 2024.

This represents a 150% growth rate.  [← WRONG! Should be 150%]
"""
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    messages = [
        {
            "role": "system",
            "content": create_data_validator_instructions_with_tools()
        },
        {
            "role": "user",
            "content": f"""Verify the growth rate calculation in this document.

Call validate_calculation to check if 150% is correct.

DOCUMENT:
{doc_with_error}"""
        }
    ]
    
    print("\n🤖 Testing error detection...")
    
    try:
        response = execute_agent_with_tools(
            client=client,
            model="gpt-4o-mini",
            messages=messages,
            max_tool_iterations=3
        )
        
        print("\n" + "="*80)
        print("AGENT RESPONSE (Should catch the error!)")
        print("="*80)
        print(response)
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run all tests."""
    print("\n🚀 AGENT TOOLS TESTING SUITE")
    print("="*80)
    
    # Test 1: Safe Python executor (no API needed)
    await test_safe_python_executor()
    
    # Test 2: Tool registry (no API needed)
    await test_tool_registry()
    
    # Test 3 & 4: Real agent with tools (requires API)
    await test_agent_with_tools()
    await test_incorrect_calculation()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

