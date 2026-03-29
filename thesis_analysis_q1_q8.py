"""Thesis analysis script for Q1 (polysemy) and Q8 (score distribution)."""
import json
import statistics

with open('analysis_results/semantic_similarity_analysis_20250730_104123.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Q1: Multi-category patterns (similarity >= 0.6 in multiple categories)
multi_cat_06 = []
for p in data['detailed_results']['patterns']:
    high_cats = [(cat, score) for cat, score in p['top_categories'] if score >= 0.6]
    if len(high_cats) > 1:
        multi_cat_06.append(p)

print(f"=== Q1: Patterns with similarity >= 0.6 in MULTIPLE categories: {len(multi_cat_06)} ===")
for m in multi_cat_06[:10]:
    print(f"  {m['pattern_id']} {m['pattern_name']}: {m['top_categories']}")

# With lower threshold >= 0.3 (since the embedding space is sparse)
multi_cat_03 = []
for p in data['detailed_results']['patterns']:
    high_cats = [(cat, score) for cat, score in p['top_categories'] if score >= 0.3]
    if len(high_cats) > 1:
        multi_cat_03.append({
            'id': p['pattern_id'],
            'name': p['pattern_name'],
            'cats': high_cats,
            'count': len(high_cats)
        })

multi_cat_03.sort(key=lambda x: x['count'], reverse=True)
print(f"\n=== Patterns with similarity >= 0.3 in multiple categories (polysemous): {len(multi_cat_03)} ===")
print(f"=== Top 15 most polysemous: ===")
for m in multi_cat_03[:15]:
    cats_str = ", ".join([f"{c[0]}={c[1]:.4f}" for c in m['cats']])
    print(f"  {m['id']} {m['name']} ({m['count']} cats): {cats_str}")

# With threshold >= 0.25
multi_cat_025 = []
for p in data['detailed_results']['patterns']:
    high_cats = [(cat, score) for cat, score in p['top_categories'] if score >= 0.25]
    if len(high_cats) > 1:
        multi_cat_025.append({
            'id': p['pattern_id'],
            'name': p['pattern_name'],
            'cats': high_cats,
            'count': len(high_cats)
        })

multi_cat_025.sort(key=lambda x: x['count'], reverse=True)
print(f"\n=== Patterns with similarity >= 0.25 in multiple categories: {len(multi_cat_025)} ===")
print(f"=== Top 10 most polysemous: ===")
for m in multi_cat_025[:10]:
    cats_str = ", ".join([f"{c[0]}={c[1]:.4f}" for c in m['cats']])
    print(f"  {m['id']} {m['name']} ({m['count']} cats): {cats_str}")

# Q8: Full distribution
all_confidences = [p['confidence'] for p in data['detailed_results']['patterns']]
print(f"\n=== Q8: Similarity Score Distribution ({len(all_confidences)} patterns) ===")
print(f"Mean: {statistics.mean(all_confidences):.4f}")
print(f"Median: {statistics.median(all_confidences):.4f}")
print(f"Stdev: {statistics.stdev(all_confidences):.4f}")
print(f"Min: {min(all_confidences):.4f}")
print(f"Max: {max(all_confidences):.4f}")

high = len([c for c in all_confidences if c >= 0.7])
medium = len([c for c in all_confidences if 0.5 <= c < 0.7])
low = len([c for c in all_confidences if c < 0.5])
print(f"High (>=0.7): {high} ({high/len(all_confidences)*100:.1f}%)")
print(f"Medium (0.5-0.69): {medium} ({medium/len(all_confidences)*100:.1f}%)")
print(f"Low (<0.5): {low} ({low/len(all_confidences)*100:.1f}%)")

# Finer histogram
buckets = {}
for c in all_confidences:
    bucket = round(c * 10) / 10  # Round to nearest 0.1
    buckets[bucket] = buckets.get(bucket, 0) + 1
print("\nHistogram (0.1 bins):")
for b in sorted(buckets.keys()):
    bar = "#" * (buckets[b] // 5)
    print(f"  {b:.1f}: {buckets[b]:4d} ({buckets[b]/len(all_confidences)*100:5.1f}%) {bar}")

# Also check examples
all_ex_conf = [e['confidence'] for e in data['detailed_results']['examples']]
print(f"\n=== Example-Level Distribution ({len(all_ex_conf)} examples) ===")
print(f"Mean: {statistics.mean(all_ex_conf):.4f}")
print(f"Median: {statistics.median(all_ex_conf):.4f}")
print(f"Min: {min(all_ex_conf):.4f}")
print(f"Max: {max(all_ex_conf):.4f}")
