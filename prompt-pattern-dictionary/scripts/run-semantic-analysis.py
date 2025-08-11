#!/usr/bin/env python3
"""
Comprehensive semantic analysis pipeline.
This script runs the complete pipeline for semantic categorization analysis:
1. Generates category embeddings
2. Analyzes pattern-category similarities 
3. Provides recommendations for recategorization

Usage:
    python run-semantic-analysis.py [--force]
    
Options:
    --force    Force regeneration of all files even if they exist
"""

import subprocess
import sys
import argparse
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists and log the result."""
    if file_path.exists():
        logger.info(f"✅ {description} already exists: {file_path}")
        return True
    else:
        logger.info(f"📝 {description} needs to be generated: {file_path}")
        return False

def run_script(script_path: Path, description: str) -> bool:
    """Run a Python script and return success status."""
    try:
        logger.info(f"🚀 Starting: {description}")
        logger.info(f"📜 Running script: {script_path}")
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=script_path.parent
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"❌ {description} failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error output: {result.stderr}")
            if result.stdout:
                logger.info(f"Standard output: {result.stdout}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running {description}: {e}")
        return False

def main():
    """Run the complete semantic analysis pipeline."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run semantic analysis pipeline')
    parser.add_argument('--force', action='store_true', 
                       help='Force regeneration of all files even if they exist')
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Check for existing files
    category_embeddings_file = project_root / "public" / "data" / "category-embeddings.json"
    similarity_analysis_file = project_root / "public" / "data" / "similarity-analysis.json"
    
    logger.info("🎯 Starting Semantic Analysis Pipeline")
    logger.info("=" * 60)
    
    # Check existing files
    logger.info("\n📋 Checking existing files:")
    category_embeddings_exist = check_file_exists(category_embeddings_file, "Category embeddings")
    similarity_analysis_exist = check_file_exists(similarity_analysis_file, "Similarity analysis")
    
    # Define scripts to run conditionally
    scripts = []
    
    if args.force or not category_embeddings_exist:
        scripts.append({
            "path": script_dir / "generate-category-embeddings.py",
            "description": "Category Embedding Generation"
        })
        if args.force and category_embeddings_exist:
            logger.info("🔄 Force mode: Regenerating category embeddings")
    else:
        logger.info("⏭️  Skipping category embedding generation (already exists)")
    
    if args.force or not similarity_analysis_exist:
        scripts.append({
            "path": script_dir / "analyze-semantic-similarity.py", 
            "description": "Semantic Similarity Analysis"
        })
        if args.force and similarity_analysis_exist:
            logger.info("🔄 Force mode: Regenerating similarity analysis")
    else:
        logger.info("⏭️  Skipping similarity analysis (already exists)")
    
    if not scripts:
        logger.info("\n🎉 All analysis files already exist!")
        logger.info("📊 Results available in:")
        logger.info(f"   - {category_embeddings_file}")
        logger.info(f"   - {similarity_analysis_file}")
        
        print("\n🎯 Files are up to date!")
        print("💡 To regenerate, use --force flag or delete the existing files.")
        
        # Show quick summary of existing results
        try:
            with open(similarity_analysis_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            metadata = analysis.get('metadata', {}).get('analysis', {})
            print(f"\n📈 Current Analysis Summary:")
            print(f"   Patterns processed: {metadata.get('patternsProcessed', 0)}")
            print(f"   Accuracy rate: {metadata.get('accuracyRate', 0)*100:.1f}%")
            print(f"   Recategorization suggestions: {len(analysis.get('recommendations', {}).get('recategorize', []))}")
            print(f"   Low confidence patterns: {len(analysis.get('recommendations', {}).get('lowConfidence', []))}")
            
        except Exception as e:
            logger.warning(f"Could not read existing analysis summary: {e}")
        
        return
    
    success_count = 0
    
    for i, script_info in enumerate(scripts, 1):
        logger.info(f"\n📍 Step {i}/{len(scripts)}: {script_info['description']}")
        logger.info("-" * 40)
        
        if run_script(script_info["path"], script_info["description"]):
            success_count += 1
        else:
            logger.error(f"❌ Pipeline failed at step {i}")
            break
    
    # Final results
    logger.info("\n" + "=" * 60)
    if success_count == len(scripts):
        logger.info("🎉 Semantic Analysis Pipeline completed successfully!")
        logger.info("📊 Results available in:")
        logger.info("   - public/data/category-embeddings.json")
        logger.info("   - public/data/similarity-analysis.json")
        
        print("\n🎯 Next Steps:")
        print("1. Review similarity-analysis.json for recategorization suggestions")
        print("2. Check patterns with low confidence scores")
        print("3. Consider updating category definitions based on patterns")
        print("4. Implement similarity-based search in the web app")
        
    else:
        logger.error(f"❌ Pipeline completed with errors ({success_count}/{len(scripts)} steps successful)")
        sys.exit(1)

if __name__ == "__main__":
    main()
