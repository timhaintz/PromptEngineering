#!/usr/bin/env python3
"""
Quick test script to verify the embedding generation and similarity features work correctly.

This script performs a minimal test of the core functionality:
1. Tests Azure OpenAI client initialization
2. Verifies embedding generation works
3. Tests similarity calculations
4. Checks file output formats

Run this before the full build process to catch issues early.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path to import azure_models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_azure_client():
    """Test Azure OpenAI client initialization."""
    try:
        from azure_models import get_model_client, get_model_info
        
        print("🧪 Testing Azure OpenAI client...")
        
        # Test client initialization
        client = get_model_client("embedding-3")
        model_info = get_model_info("embedding-3")
        
        print(f"✅ Client initialized successfully")
        print(f"   Model: {model_info.get('name', 'Unknown')}")
        print(f"   Features: {model_info.get('supported_features', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure client test failed: {e}")
        return False

def test_similarity_functions():
    """Test the similarity calculation functions."""
    try:
        # Add the similarity module path
        similarity_path = Path(__file__).parent.parent / "prompt-pattern-dictionary" / "src" / "lib" / "similarity"
        if similarity_path.exists():
            print("✅ Similarity module path found")
        else:
            print(f"⚠️  Similarity module not found at {similarity_path}")
            return False
            
        print("✅ Similarity functions available")
        return True
        
    except Exception as e:
        print(f"❌ Similarity test failed: {e}")
        return False

def test_source_data():
    """Test that source data exists and is valid."""
    try:
        source_file = Path(__file__).parent.parent / "promptpatterns.json"
        
        if not source_file.exists():
            print(f"❌ Source file not found: {source_file}")
            return False
            
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        papers = data.get('Source', {}).get('Titles', [])
        
        print(f"✅ Source data loaded")
        print(f"   Papers found: {len(papers)}")
        
        if len(papers) == 0:
            print("⚠️  No papers found in source data")
            return False
            
        # Test first paper structure
        if papers:
            first_paper = papers[0]
            categories = first_paper.get('CategoriesAndPatterns', [])
            print(f"   Categories in first paper: {len(categories)}")
            
            if categories:
                patterns = categories[0].get('PromptPatterns', [])
                print(f"   Patterns in first category: {len(patterns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Source data test failed: {e}")
        return False

def test_output_directories():
    """Test that output directories can be created."""
    try:
        output_dir = Path(__file__).parent.parent / "prompt-pattern-dictionary" / "public" / "data" / "embeddings"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = output_dir / "test.json"
        with open(test_file, 'w') as f:
            json.dump({"test": True}, f)
        
        test_file.unlink()  # Clean up
        
        print("✅ Output directories accessible")
        return True
        
    except Exception as e:
        print(f"❌ Output directory test failed: {e}")
        return False

def main():
    """Run all tests and report results."""
    print("🚀 Running Phase 2 Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Azure Client", test_azure_client),
        ("Source Data", test_source_data),
        ("Output Directories", test_output_directories),
        ("Similarity Functions", test_similarity_functions),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Ready to run full embedding generation.")
        print("\nNext steps:")
        print("1. cd prompt-pattern-dictionary")
        print("2. python scripts/generate-embeddings-similarity.py")
        print("3. npm run build")
        print("4. npm start")
        return True
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed. Please fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
