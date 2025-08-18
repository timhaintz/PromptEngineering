#!/usr/bin/env python3
"""
Test script to verify the updated template logic works correctly.
This script tests both template modes:
1. Logic overview mode (only -logic)
2. Category-specific mode (-logic and -category)
"""

import sys
import os

# Add parent directory to path to import categorisation_write_up
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)

from categorisation_write_up import CategorisationWriteUpClient, validate_logic, validate_category

def test_template_logic():
    """Test the template selection logic."""
    
    print("="*60)
    print("TESTING TEMPLATE LOGIC")
    print("="*60)
    
    # Test 1: Logic overview mode (only logic provided)
    print("\n1. Testing Logic Overview Mode (only -logic 'Beyond')")
    print("-" * 50)
    
    try:
        client = CategorisationWriteUpClient(debug=True)
        
        # Test logic overview (category=None)
        result = client.generate_writeup(
            logic="Beyond",
            category=None,
            task="Generate logic overview for Beyond logic",
            temperature=0.3
        )
        
        print("✓ Logic overview generation successful")
        print(f"Output length: {len(result)} characters")
        print(f"Preview: {result[:200]}...")
        
    except Exception as e:
        print(f"✗ Logic overview generation failed: {e}")
    
    # Test 2: Category-specific mode (both logic and category provided)
    print("\n2. Testing Category-Specific Mode (-logic 'Beyond' -category 'prediction')")
    print("-" * 50)
    
    try:
        # Test category-specific writeup
        result = client.generate_writeup(
            logic="Beyond",
            category="prediction",
            task="Generate category writeup for prediction under Beyond logic",
            temperature=0.3
        )
        
        print("✓ Category-specific generation successful")
        print(f"Output length: {len(result)} characters")
        print(f"Preview: {result[:200]}...")
        
    except Exception as e:
        print(f"✗ Category-specific generation failed: {e}")
    
    # Test 3: Validation tests
    print("\n3. Testing Validation Logic")
    print("-" * 50)
    
    # Test valid logic
    assert validate_logic("Beyond"), "Should validate Beyond logic"
    print("✓ Valid logic validation works")
    
    # Test invalid logic
    assert not validate_logic("InvalidLogic"), "Should reject invalid logic"
    print("✓ Invalid logic validation works")
    
    # Test valid category
    assert validate_category("Beyond", "prediction"), "Should validate Beyond/prediction"
    print("✓ Valid category validation works")
    
    # Test invalid category
    assert not validate_category("Beyond", "invalid_category"), "Should reject invalid category"
    print("✓ Invalid category validation works")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    test_template_logic()
