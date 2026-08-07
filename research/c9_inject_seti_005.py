#!/usr/bin/env python3
"""
C9-2026-SETI-005 Bus Injection Script
Injects the ALMA SETI entry into c9_bus.jsonl and updates the collection manifest.
"""

import json
import os
import sys
from datetime import datetime, timezone

# ââ CONFIG ââââââââââââââââââââââââââââââââââââââââââââââââ
BUS_PATH = os.path.expanduser("~/c9_bus.jsonl")
COLLECTION_PATH = os.path.expanduser("~/c9_collections.json")
ENTRY_FILE = os.path.expanduser("~/C9-2026-SETI-005_entry.json")

# ââ ENTRY DATA (embedded so no external file needed) ââââââ
ENTRY = {
    "entry_id": "C9-2026-SETI-005",
    "entry_title": "First SETI Survey Using ALMA: High-Frequency Technosignature Search at 90-93 GHz",
    "collection": "C9-COLLECTION-2026-0723-WEEKLYSCIENCE",
    "timestamp_created": "2026-07-24T01:18:10Z",
    "timestamp_updated": "2026-07-24T01:18:10Z",
    "version": "1.0.0",
    "layer": "LAYER 1",
    "audit_score": 0.799,
    "sandbox_passed": True,
    "sandbox_version": "2.0",
    "meta_pattern": "Structured Suppression of Dominant Mode",
    "source": {
        "primary": {
            "type": "peer_reviewed",
            "title": "Conducting high-frequency radio SETI searches using ALMA",
            "authors": ["Louisa A. Mason", "Michael A. Garrett", "Kelvin Wandia", "Andrew P. V. Siemion"],
            "journal": "MNRAS",
            "volume": "536",
            "issue": "3",
            "pages": "2127-2134",
            "year": 2025,
            "doi": "10.1093/mnras/stae2714",
            "arxiv": "2411.19827"
        },
        "secondary": {
            "type": "peer_reviewed",
            "title": "Simulating the stellar bycatch: constraining the prevalence of extraterrestrial transmitters within radio SETI surveys",
            "authors": ["Louisa A. Mason", "Michael A. Garrett", "Andrew P. V. Siemion"],
            "journal": "MNRAS",
            "volume": "545",
            "issue": "3",
            "year": 2026,
            "doi": "10.1093/mnras/staf2112",
            "arxiv": "2511.20231"
        },
        "tertiary": {
            "type": "press_release",
            "title": "Could alien signals be hiding on a different radio channel?",
            "publisher": "Royal Astronomical Society",
            "date": "2026-07-24",
            "event": "RAS National Astronomy Meeting 2026, Birmingham, UK"
        }
    },
    "technical_parameters": {
        "instrument": "ALMA",
        "band": "Band 3",
        "frequencies_ghz": [90.642, 93.151],
        "num_archival_observations": 4,
        "num_target_stars": 28,
        "num_bycatch_stars_bgm": 6100000,
        "num_bycatch_stars_gaia": 288000,
        "bycatch_multiplier": 21.18,
        "eirp_min_watts": 6.91e17,
        "galactic_model": "Besancon Galactic Model"
    },
    "cluster_mapping": [
        {"cluster": "C1", "relevance": 0.35},
        {"cluster": "C3", "relevance": 0.55},
        {"cluster": "C5", "relevance": 0.40},
        {"cluster": "C6", "relevance": 0.70}
    ],
    "cross_references": [
        {"entry_id": "C9-2026-QG-005", "strength": 0.35},
        {"entry_id": "C9-2026-COSMO-001", "strength": 0.45},
        {"entry_id": "C9-2026-LEGACY-001", "strength": 0.30}
    ],
    "sandbox_results": {
        "overall_score": 0.799,
        "layer": "LAYER 1",
        "passed": True
    },
    "c9_notes": {
        "bus_priority": 4,
        "discovery_pipeline_relevance": "High",
        "continuity": "User Dec 2023 3I/ATLAS 7/10 rating in tension with this null result"
    }
}

# ââ BUS INJECTION âââââââââââââââââââââââââââââââââââââââââ
def inject_bus():
    """Append entry event to c9_bus.jsonl"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "entry_injected",
        "module": "c9_librarian",
        "entry_id": ENTRY["entry_id"],
        "layer": ENTRY["layer"],
        "audit_score": ENTRY["audit_score"],
        "sandbox_passed": ENTRY["sandbox_passed"],
        "meta_pattern": ENTRY["meta_pattern"],
        "payload": ENTRY
    }

    with open(BUS_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")

    print(f"[BUS] Injected {ENTRY['entry_id']} â {BUS_PATH}")
    return True

# ââ COLLECTION UPDATE âââââââââââââââââââââââââââââââââââââ
def update_collection():
    """Add entry to weekly science collection manifest"""
    collection_id = ENTRY["collection"]

    if os.path.exists(COLLECTION_PATH):
        with open(COLLECTION_PATH, "r") as f:
            collections = json.load(f)
    else:
        collections = {}

    if collection_id not in collections:
        collections[collection_id] = {
            "created": datetime.now(timezone.utc).isoformat(),
            "entries": [],
            "metadata": {
                "type": "weekly_science",
                "week": "2026-W30",
                "compiler": "c9_librarian"
            }
        }

    # Add entry reference (avoid duplicating full payload)
    entry_ref = {
        "entry_id": ENTRY["entry_id"],
        "title": ENTRY["entry_title"],
        "layer": ENTRY["layer"],
        "audit_score": ENTRY["audit_score"],
        "sandbox_passed": ENTRY["sandbox_passed"],
        "added": datetime.now(timezone.utc).isoformat()
    }

    # Prevent duplicates
    existing_ids = [e["entry_id"] for e in collections[collection_id]["entries"]]
    if ENTRY["entry_id"] not in existing_ids:
        collections[collection_id]["entries"].append(entry_ref)
        collections[collection_id]["updated"] = datetime.now(timezone.utc).isoformat()

        with open(COLLECTION_PATH, "w") as f:
            json.dump(collections, f, indent=2)

        print(f"[COLLECTION] Added {ENTRY['entry_id']} â {collection_id}")
        print(f"[COLLECTION] Total entries in {collection_id}: {len(collections[collection_id]['entries'])}")
    else:
        print(f"[COLLECTION] {ENTRY['entry_id']} already in {collection_id}, skipping")

    return True

# ââ ENTRY FILE WRITE ââââââââââââââââââââââââââââââââââââââ
def write_entry_file():
    """Write standalone entry JSON to disk"""
    with open(ENTRY_FILE, "w") as f:
        json.dump(ENTRY, f, indent=2)
    print(f"[FILE] Wrote {ENTRY_FILE}")
    return True

# ââ MAIN ââââââââââââââââââââââââââââââââââââââââââââââââââ
def main():
    print("=" * 60)
    print("C9-2026-SETI-005 Injection")
    print("=" * 60)

    write_entry_file()
    inject_bus()
    update_collection()

    print("=" * 60)
    print("INJECTION COMPLETE")
    print(f"  Entry: {ENTRY['entry_id']}")
    print(f"  Layer: {ENTRY['layer']}")
    print(f"  Score: {ENTRY['audit_score']}")
    print(f"  Pattern: {ENTRY['meta_pattern']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
