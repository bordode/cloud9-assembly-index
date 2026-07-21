#!/usr/bin/env python3
"""
c9_arxiv_harvester_v2.py â Fixed arXiv scraper with AND logic
Replaces c9_run_fixed.py. Properly constructs boolean queries.
"""
import os, json, urllib.request, re, time
from datetime import datetime
from pathlib import Path

OUT = Path.home() / "cloud9" / "orchestrator"
OUT.mkdir(parents=True, exist_ok=True)

# Each query is a list of terms â all must appear (AND logic)
QUERIES = [
    ["Walker", "Cronin", "assembly", "theory"],
    ["IllustrisTNG", "dark", "matter", "halo"],
    ["3I", "ATLAS", "interstellar"],
    ["quantum", "consciousness", "integrated", "information"],
    ["Fibonacci", "galactic", "halo"],
    ["neuromorphic", "spiking", "neural"],
    ["causal", "set", "quantum", "gravity"],
    ["topological", "data", "analysis", "physics"],
    ["entropic", "time", "cold", "atom"],
    ["Barontini", "entropy", "mini", "universe"],
    ["quantum", "Darwinism", "decoherence"],
    ["supermassive", "black", "hole", "binary"],
    ["origin", "life", "biosignature", "molecular"],
    ["memristor", "neuromorphic", "hardware"],
    ["loop", "quantum", "gravity", "spacetime"],
]

def build_query(terms):
    """Build arXiv AND query from term list."""
    return "+AND+".join(f"all:{t}" for t in terms)

def fetch_arxiv(terms, n=3):
    try:
        query = build_query(terms)
        url = f"https://export.arxiv.org/api/query?search_query={urllib.request.quote(query, safe='+:')}&max_results={n}&sortBy=submittedDate&sortOrder=descending"
        xml = urllib.request.urlopen(url, timeout=15).read().decode()
        papers = []
        for e in xml.split("<entry>")[1:]:
            def g(t):
                m = re.search(f"<{t}>(.*?)</{t}>", e, re.DOTALL)
                return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
            if g("title") and g("title") != "arXiv Query":
                papers.append({
                    "title": g("title"),
                    "abstract": g("summary")[:500],
                    "link": g("id"),
                    "date": g("published")[:10],
                    "query_terms": terms,
                })
        return papers
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

def score(t, a):
    x = (t + " " + a).lower()
    s = 0.15
    hits = []
    kw = {
        "assembly":0.15, "walker":0.10, "cronin":0.10, "complexity":0.10,
        "molecular":0.08, "biosignature":0.12, "origin of life":0.15,
        "dark matter":0.12, "halo":0.10, "illustristng":0.15, "tng":0.10,
        "interstellar":0.15, "comet":0.10, "oort":0.10, "extrasolar":0.10,
        "methane":0.08, "jwst":0.08, "quantum":0.08, "consciousness":0.12,
        "integrated":0.08, "iit":0.12, "neuromorphic":0.12, "spiking":0.10,
        "causal set":0.15, "loop quantum":0.12, "spacetime":0.08,
        "topological":0.10, "homology":0.10, "persistent":0.08, "tda":0.12,
        "entropic":0.12, "entropy":0.08, "cold atom":0.10, "barontini":0.12,
        "darwinism":0.12, "decoherence":0.10, "fibonacci":0.12,
        "15.4":0.15, "kpc":0.10, "memristor":0.12, "supermassive":0.10,
        "black hole binary":0.12, "gravitational wave":0.10, "lensing":0.10,
    }
    for k, v in kw.items():
        if k in x:
            s += v
            hits.append(k)
    if len(hits) >= 3: s += 0.05
    if len(hits) >= 5: s += 0.05
    if len(hits) >= 7: s += 0.05
    return min(round(s, 2), 1.0), hits

print(f"[{datetime.now().strftime('%H:%M:%S')}] C9 arXiv Harvester v2.0")
print(f"Output: {OUT}/harvest_v2.json\n")

all_papers = []
for terms in QUERIES:
    ps = fetch_arxiv(terms, 3)
    for p in ps:
        p["score"], p["hits"] = score(p["title"], p["abstract"])
    all_papers.extend(ps)
    print(f"  {' '.join(terms)[:45]:45s} â {len(ps)} papers")
    time.sleep(1.5)  # Be polite to arXiv

# Deduplicate by link
dedup = {}
for p in all_papers:
    dedup[p["link"]] = p
all_papers = list(dedup.values())
all_papers.sort(key=lambda x: x["score"], reverse=True)

print(f"\n{'='*60}")
print(f"Total unique papers: {len(all_papers)}")
print(f"{'='*60}")

for i, p in enumerate(all_papers[:20], 1):
    hits = ", ".join(p["hits"][:6]) if p["hits"] else "none"
    print(f"\n[{i:2d}] Score: {p['score']:.2f} | {p['date']}")
    print(f"      {p['title'][:70]}")
    print(f"      Hits: {hits}")

print(f"\n{'='*60}")
for thresh in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]:
    count = len([p for p in all_papers if p["score"] >= thresh])
    print(f"  Score â¥ {thresh:.1f}: {count} papers")

with open(OUT / "harvest_v2.json", "w") as f:
    json.dump(all_papers, f, indent=2)
print(f"\nSaved to {OUT}/harvest_v2.json")
