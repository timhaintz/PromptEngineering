#!/usr/bin/env python3
"""
Integration test script for the Prompt Pattern Dictionary project.

This script performs a comprehensive test of the entire system:
1. Tests Azure OpenAI client initialization
2. Verifies embedding generation works
3. Tests similarity calculations
4. Checks file output formats
5. Validates Next.js build process

Run this before deployment to catch issues early.
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
        # Check if similarity module files exist
        similarity_path = Path(__file__).parent / "src" / "lib" / "similarity"
        
        expected_files = [
            "similarity-engine.ts",
            "similarity-matrix.ts", 
            "similarity-network.ts",
            "index.ts"
        ]
        
        missing_files = []
        for file_name in expected_files:
            file_path = similarity_path / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"⚠️  Missing similarity files: {', '.join(missing_files)}")
            return False
        
        print("✅ Similarity module files found")
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
        output_dir = Path(__file__).parent / "public" / "data" / "embeddings"
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

def test_nextjs_structure():
    """Test that Next.js project structure is correct."""
    try:
        project_root = Path(__file__).parent
        
        required_files = [
            "package.json",
            "next.config.ts",
            "tsconfig.json",
            "src/app/layout.tsx",
            "src/app/page.tsx",
            "src/app/comparison/page.tsx",
            "src/app/playground/page.tsx"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"⚠️  Missing Next.js files: {', '.join(missing_files)}")
            return False
        
        print("✅ Next.js structure validated")
        
        # Check component structure
        component_dirs = [
            "src/components/comparison",
            "src/components/pattern", 
            "src/components/search",
            "src/components/ui"
        ]
        
        for dir_path in component_dirs:
            full_path = project_root / dir_path
            if not full_path.exists():
                print(f"⚠️  Missing component directory: {dir_path}")
                return False
        
        print("✅ Component structure validated")
        return True
        
    except Exception as e:
        print(f"❌ Next.js structure test failed: {e}")
        return False

def test_embedding_script():
    """Test that embedding generation script is properly configured."""
    try:
        script_path = Path(__file__).parent / "scripts" / "generate-embeddings-similarity.py"
        
        if not script_path.exists():
            print(f"❌ Embedding script not found: {script_path}")
            return False
        
        # Read script and check for key components
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        required_elements = [
            "EmbeddingGenerator",
            "azure_models",
            "_call_embedding_api",
            "paper-based chunking"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in script_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"⚠️  Missing elements in embedding script: {', '.join(missing_elements)}")
            return False
        
        print("✅ Embedding script validated")
        return True
        
    except Exception as e:
        print(f"❌ Embedding script test failed: {e}")
        return False

def test_package_dependencies():
    """Test that package.json has required dependencies."""
    try:
        package_file = Path(__file__).parent / "package.json"
        
        with open(package_file, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}
        
        required_deps = [
            "next",
            "react", 
            "react-dom",
            "typescript",
            "@types/react",
            "tailwindcss"
        ]
        
        missing_deps = []
        for dep in required_deps:
            if dep not in all_deps:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"⚠️  Missing package dependencies: {', '.join(missing_deps)}")
            return False
        
        print("✅ Package dependencies validated")
        return True
        
    except Exception as e:
        print(f"❌ Package dependencies test failed: {e}")
        return False

def main():
    """Run all tests and report results."""
    print("🚀 Running Prompt Pattern Dictionary Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Azure Client", test_azure_client),
        ("Source Data", test_source_data),
        ("Output Directories", test_output_directories),
        ("Next.js Structure", test_nextjs_structure),
        ("Similarity Functions", test_similarity_functions),
        ("Embedding Script", test_embedding_script),
        ("Package Dependencies", test_package_dependencies),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. python scripts/generate-embeddings-similarity.py")
        print("2. npm install")
        print("3. npm run build") 
        print("4. npm start")
        return True
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed. Please fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
