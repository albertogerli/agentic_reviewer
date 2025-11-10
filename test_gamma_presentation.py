#!/usr/bin/env python3
"""
Test script for Gamma presentation generation.
Tests the format_review_for_gamma function with various risk_heatmap formats.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from gamma_integration import GammaPresentationGenerator

def test_gamma_formatting():
    """Test the format_review_for_gamma function with edge cases."""
    
    print("🧪 Testing Gamma Presentation Formatting")
    print("=" * 60)
    
    # Create a test generator instance (no API key needed for formatting test)
    generator = GammaPresentationGenerator(api_key="test_key")
    
    # Test Case 1: risk_heatmap with numeric values (NORMAL)
    print("\n✅ Test 1: Numeric risk values")
    review_data_1 = {
        "document_info": {
            "title": "Test Document",
            "type": "business_proposal"
        },
        "final_evaluation": "Overall good document with minor issues.",
        "risk_heatmap": {
            "accuracy": 75.0,
            "completeness": 85.0,
            "clarity": 90.0,
            "consistency": 70.0
        },
        "structured_issues": [
            {
                "severity": "high",
                "title": "Test Issue",
                "description": "Test description",
                "location": "Page 1",
                "suggestion": "Test suggestion"
            }
        ],
        "agent_reviews": {
            "test_agent": "This is a test review with excellent points."
        }
    }
    
    try:
        content_1 = generator.format_review_for_gamma(review_data_1)
        print(f"✅ SUCCESS - Generated {len(content_1)} characters")
        print(f"   Preview: {content_1[:100]}...")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Test Case 2: risk_heatmap with dict values (BUG CASE)
    print("\n✅ Test 2: Dict risk values (previous bug)")
    review_data_2 = {
        "document_info": {
            "title": "Test Document 2",
            "type": "technical_report"
        },
        "final_evaluation": "Needs improvement.",
        "risk_heatmap": {
            "accuracy": {"score": 75.0, "confidence": 0.9},
            "completeness": {"score": 85.0, "confidence": 0.8},
            "clarity": 90.0,  # Mixed with numeric
            "consistency": {"score": 70.0}
        },
        "structured_issues": [],
        "agent_reviews": {}
    }
    
    try:
        content_2 = generator.format_review_for_gamma(review_data_2)
        print(f"✅ SUCCESS - Generated {len(content_2)} characters")
        print(f"   Preview: {content_2[:100]}...")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Test Case 3: risk_heatmap with invalid values
    print("\n✅ Test 3: Invalid risk values (edge case)")
    review_data_3 = {
        "document_info": {
            "title": "Test Document 3",
            "type": "legal_document"
        },
        "final_evaluation": "Complex case.",
        "risk_heatmap": {
            "accuracy": 75.0,
            "invalid_value": "not_a_number",
            "another_invalid": None,
            "empty_dict": {},
            "completeness": 85.0
        },
        "structured_issues": [],
        "agent_reviews": {}
    }
    
    try:
        content_3 = generator.format_review_for_gamma(review_data_3)
        print(f"✅ SUCCESS - Generated {len(content_3)} characters")
        print(f"   Handled invalid values gracefully")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Test Case 4: Empty risk_heatmap
    print("\n✅ Test 4: Empty risk heatmap")
    review_data_4 = {
        "document_info": {
            "title": "Test Document 4",
            "type": "other"
        },
        "final_evaluation": "Simple test.",
        "risk_heatmap": {},
        "structured_issues": [],
        "agent_reviews": {}
    }
    
    try:
        content_4 = generator.format_review_for_gamma(review_data_4)
        print(f"✅ SUCCESS - Generated {len(content_4)} characters")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_gamma_formatting()
    sys.exit(0 if success else 1)

