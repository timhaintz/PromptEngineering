#!/usr/bin/env python3
"""
Analyze semantic similarity between patterns and categories using embeddings.
This script compares pattern embeddings against category embeddings to suggest
optimal categorization based on semantic similarity.
"""

import json
import logging
import sys
import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SemanticSimilarityAnalyzer:
    """Analyze semantic similarity between patterns and categories."""
    
    def __init__(self, similarity_threshold: float = 0.6):
        """Initialize the similarity analyzer."""
        self.similarity_threshold = similarity_threshold
        self.category_embeddings = None
        self.pattern_embeddings = {}
        self.patterns_data = None
        
    def _validate_data_loaded(self) -> bool:
        """Validate that all required data is loaded."""
        if not self.category_embeddings:
            logger.error("Category embeddings not loaded")
            return False
        
        if 'categories' not in self.category_embeddings:
            logger.error("Category embeddings missing 'categories' section")
            return False
            
        if not self.pattern_embeddings:
            logger.error("Pattern embeddings not loaded")
            return False
            
        if not self.patterns_data:
            logger.error("Pattern data not loaded")
            return False
            
        return True
    
    def _get_category_embeddings(self) -> Dict[str, Any]:
        """Get category embeddings with type safety."""
        if not self.category_embeddings:
            raise RuntimeError("Category embeddings not loaded")
        return self.category_embeddings
    
    def _get_patterns_data(self) -> Dict[str, Any]:
        """Get patterns data with type safety."""
        if not self.patterns_data:
            raise RuntimeError("Patterns data not loaded")
        return self.patterns_data
        
    def load_category_embeddings(self, category_embeddings_file: str) -> bool:
        """Load category embeddings."""
        try:
            logger.info(f"Loading category embeddings from: {category_embeddings_file}")
            
            with open(category_embeddings_file, 'r', encoding='utf-8') as f:
                self.category_embeddings = json.load(f)
            
            if not self.category_embeddings or 'categories' not in self.category_embeddings:
                logger.error("Invalid category embeddings format - missing 'categories' section")
                return False
            
            category_count = len(self.category_embeddings['categories'])
            logger.info(f"Loaded embeddings for {category_count} categories")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading category embeddings: {e}")
            return False
    
    def load_pattern_embeddings(self, embeddings_dir: str) -> bool:
        """Load all pattern embeddings from paper files."""
        try:
            logger.info(f"Loading pattern embeddings from: {embeddings_dir}")
            
            embeddings_path = Path(embeddings_dir)
            if not embeddings_path.exists():
                logger.error(f"Embeddings directory does not exist: {embeddings_dir}")
                return False
            
            pattern_count = 0
            
            # Load all paper embedding files
            for paper_file in embeddings_path.glob("paper-*.json"):
                try:
                    with open(paper_file, 'r', encoding='utf-8') as f:
                        paper_data = json.load(f)
                    
                    # Extract pattern embeddings
                    if 'patterns' in paper_data:
                        for pattern_id, pattern_info in paper_data['patterns'].items():
                            if 'embedding' in pattern_info:
                                self.pattern_embeddings[pattern_id] = {
                                    'embedding': pattern_info['embedding'],
                                    'paper_file': paper_file.name
                                }
                                pattern_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error loading {paper_file}: {e}")
                    continue
            
            logger.info(f"Loaded embeddings for {pattern_count} patterns from {len(list(embeddings_path.glob('paper-*.json')))} papers")
            return True
            
        except Exception as e:
            logger.error(f"Error loading pattern embeddings: {e}")
            return False
    
    def load_patterns_data(self, patterns_file: str) -> bool:
        """Load pattern metadata."""
        try:
            logger.info(f"Loading pattern data from: {patterns_file}")
            
            with open(patterns_file, 'r', encoding='utf-8') as f:
                patterns_list = json.load(f)
            
            # Convert to dict for easier lookup
            self.patterns_data = {pattern['id']: pattern for pattern in patterns_list}
            
            logger.info(f"Loaded metadata for {len(self.patterns_data)} patterns")
            return True
            
        except Exception as e:
            logger.error(f"Error loading patterns data: {e}")
            return False
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def analyze_pattern_similarity(self, pattern_id: str) -> List[Tuple[str, float, str]]:
        """Analyze similarity of a single pattern against all categories."""
        if pattern_id not in self.pattern_embeddings:
            return []
        
        if not self.category_embeddings or 'categories' not in self.category_embeddings:
            logger.error("Category embeddings not properly loaded")
            return []
        
        pattern_embedding = self.pattern_embeddings[pattern_id]['embedding']
        similarities = []
        
        for category_slug, category_data in self.category_embeddings['categories'].items():
            category_embedding = category_data['embedding']
            similarity = self.cosine_similarity(pattern_embedding, category_embedding)
            similarities.append((category_slug, similarity, category_data['name']))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities
    
    def analyze_all_patterns(self) -> Dict[str, Any]:
        """Analyze similarity for all patterns."""
        logger.info("Starting semantic similarity analysis...")
        
        # Validate all data is loaded
        if not self._validate_data_loaded():
            raise RuntimeError("Required data not loaded properly")
        
        analysis_results = {
            "metadata": {
                "generatedAt": datetime.now().isoformat(),
                "totalPatterns": len(self.pattern_embeddings),
                "totalCategories": len(self._get_category_embeddings()['categories']),
                "similarityThreshold": self.similarity_threshold,
                "analysis": {}
            },
            "patterns": {},
            "categoryStats": {},
            "recommendations": {
                "recategorize": [],
                "lowConfidence": [],
                "multiCategory": []
            }
        }
        
        processed = 0
        correct_categorizations = 0
        needs_recategorization = 0
        low_confidence_patterns = 0
        
        for pattern_id in self.pattern_embeddings:
            if pattern_id not in self.patterns_data:
                logger.warning(f"Pattern {pattern_id} not found in patterns data")
                continue
            
            pattern_data = self._get_patterns_data()[pattern_id]
            current_category = pattern_data.get('category', 'Unknown')
            
            # Analyze similarity
            similarities = self.analyze_pattern_similarity(pattern_id)
            
            if not similarities:
                continue
            
            # Get best match
            best_match_slug, best_similarity, best_match_name = similarities[0]
            
            # Convert current category name to slug for comparison
            current_category_slug = self._category_name_to_slug(current_category)
            
            # Store analysis results
            analysis_results["patterns"][pattern_id] = {
                "patternName": pattern_data.get('patternName', ''),
                "currentCategory": current_category,
                "currentCategorySlug": current_category_slug,
                "bestMatch": {
                    "category": best_match_name,
                    "slug": best_match_slug,
                    "similarity": best_similarity
                },
                "allSimilarities": [
                    {
                        "category": name,
                        "slug": slug,
                        "similarity": sim
                    }
                    for slug, sim, name in similarities[:5]  # Top 5 matches
                ],
                "isCorrectlyClassified": best_match_slug == current_category_slug,
                "confidenceLevel": "high" if best_similarity >= 0.7 else "medium" if best_similarity >= 0.5 else "low"
            }
            
            # Track statistics
            if best_match_slug == current_category_slug:
                correct_categorizations += 1
            else:
                needs_recategorization += 1
                if best_similarity >= self.similarity_threshold:
                    analysis_results["recommendations"]["recategorize"].append({
                        "patternId": pattern_id,
                        "patternName": pattern_data.get('patternName', ''),
                        "currentCategory": current_category,
                        "suggestedCategory": best_match_name,
                        "similarity": best_similarity
                    })
            
            if best_similarity < self.similarity_threshold:
                low_confidence_patterns += 1
                analysis_results["recommendations"]["lowConfidence"].append({
                    "patternId": pattern_id,
                    "patternName": pattern_data.get('patternName', ''),
                    "currentCategory": current_category,
                    "bestSimilarity": best_similarity
                })
            
            # Check for multi-category patterns (multiple high similarities)
            high_similarities = [s for _, s, _ in similarities if s >= 0.6]
            if len(high_similarities) > 1:
                analysis_results["recommendations"]["multiCategory"].append({
                    "patternId": pattern_id,
                    "patternName": pattern_data.get('patternName', ''),
                    "highSimilarities": [
                        {"category": name, "similarity": sim}
                        for slug, sim, name in similarities if sim >= 0.6
                    ]
                })
            
            processed += 1
            if processed % 100 == 0:
                logger.info(f"Processed {processed}/{len(self.pattern_embeddings)} patterns")
        
        # Calculate category statistics
        for category_slug, category_data in self._get_category_embeddings()['categories'].items():
            category_patterns = [
                p for p in analysis_results["patterns"].values()
                if p["bestMatch"]["slug"] == category_slug
            ]
            
            analysis_results["categoryStats"][category_slug] = {
                "name": category_data['name'],
                "totalRecommended": len(category_patterns),
                "averageSimilarity": np.mean([p["bestMatch"]["similarity"] for p in category_patterns]) if category_patterns else 0,
                "highConfidenceCount": len([p for p in category_patterns if p["confidenceLevel"] == "high"])
            }
        
        # Update analysis metadata
        analysis_results["metadata"]["analysis"] = {
            "patternsProcessed": processed,
            "correctlyClassified": correct_categorizations,
            "needsRecategorization": needs_recategorization,
            "lowConfidencePatterns": low_confidence_patterns,
            "accuracyRate": correct_categorizations / processed if processed > 0 else 0
        }
        
        logger.info(f"Analysis completed:")
        logger.info(f"  Patterns processed: {processed}")
        logger.info(f"  Correctly classified: {correct_categorizations} ({correct_categorizations/processed*100:.1f}%)")
        logger.info(f"  Needs recategorization: {needs_recategorization}")
        logger.info(f"  Low confidence: {low_confidence_patterns}")
        
        return analysis_results
    
    def _category_name_to_slug(self, category_name: str) -> str:
        """Convert category name to slug for comparison."""
        # Simple conversion - could be enhanced
        return category_name.lower().replace(' ', '-').replace('_', '-')
    
    def save_analysis(self, analysis: Dict[str, Any], output_file: str) -> bool:
        """Save analysis results to file."""
        try:
            logger.info(f"Saving analysis results to: {output_file}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Analysis results saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis: {e}")
            return False

def main():
    """Main execution function."""
    # File paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    category_embeddings_file = project_root / "public" / "data" / "category-embeddings.json"
    embeddings_dir = project_root / "public" / "data" / "embeddings"
    patterns_file = project_root / "public" / "data" / "patterns.json"
    output_file = project_root / "public" / "data" / "similarity-analysis.json"
    
    logger.info("🔍 Starting semantic similarity analysis...")
    
    # Initialize analyzer
    analyzer = SemanticSimilarityAnalyzer(similarity_threshold=0.6)
    
    # Load data
    if not analyzer.load_category_embeddings(str(category_embeddings_file)):
        logger.error("❌ Failed to load category embeddings")
        sys.exit(1)
    
    if not analyzer.load_pattern_embeddings(str(embeddings_dir)):
        logger.error("❌ Failed to load pattern embeddings")
        sys.exit(1)
    
    if not analyzer.load_patterns_data(str(patterns_file)):
        logger.error("❌ Failed to load patterns data")
        sys.exit(1)
    
    try:
        # Perform analysis
        analysis = analyzer.analyze_all_patterns()
        
        # Save analysis
        if analyzer.save_analysis(analysis, str(output_file)):
            logger.info("✅ Semantic similarity analysis completed successfully!")
            print(f"📁 Analysis saved to: {output_file}")
            print(f"📊 Processed {analysis['metadata']['analysis']['patternsProcessed']} patterns")
            print(f"🎯 Accuracy: {analysis['metadata']['analysis']['accuracyRate']*100:.1f}%")
            print(f"🔄 Recategorization suggestions: {len(analysis['recommendations']['recategorize'])}")
            print(f"⚠️  Low confidence patterns: {len(analysis['recommendations']['lowConfidence'])}")
        else:
            logger.error("❌ Failed to save analysis")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
