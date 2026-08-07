#!/usr/bin/env python3
"""
c9_well_probe.py
Cloud-9 Tier 1 Probe for The Well (C9-2026-PHYS-001)
Pulls metadata from HuggingFace Hub API â zero disk, zero download.
"""
import urllib.request, json, os
from datetime import datetime

BUS = os.path.expanduser("~/c9_bus.jsonl")
HF_API = "https://huggingface.co/api/datasets"

def bus(event, payload):
    entry = {
        "t": datetime.now().isoformat(),
        "module": "well_probe",
        "event": event,
        "payload": payload
    }
    with open(BUS, "a") as f:
        print(json.dumps(entry), file=f)

def probe_dataset(repo_id):
    url = f"{HF_API}/{repo_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        tags = data.get("tags", [])
        downloads = data.get("downloads", 0)
        card = data.get("cardData", {})

        # Extract shape info from card if available
        shape = "unknown"
        if isinstance(card, dict):
            desc = card.get("pretty_name", "") or str(card)[:200]
            # Heuristic: look for shape patterns in description
            import re
            m = re.search(r'(\d+\s*x\s*\d+\s*x\s*\d+)', desc, re.I)
            if m:
                shape = m.group(1).replace(" ", "")

        complexity_proxy = len(tags) + (downloads / 100000.0)

        bus("well_snapshot", {
            "entry_id": "C9-2026-PHYS-001",
            "dataset": repo_id.split("/")[-1],
            "fields": tags,
            "shape": shape,
            "complexity_proxy": round(complexity_proxy, 4),
            "tier": 1,
            "downloads": downloads
        })

        print("[well] %s | complexity=%.2f | downloads=%d | shape=%s" % (
            repo_id, complexity_proxy, downloads, shape
        ))
        return True

    except urllib.error.HTTPError as e:
        bus("well_error", {"dataset": repo_id, "code": e.code})
        print("[well] ERR %s: HTTP %d" % (repo_id, e.code))
        return False
    except Exception as e:
        bus("well_error", {"dataset": repo_id, "error": str(e)})
        print("[well] ERR %s: %s" % (repo_id, e))
        return False

# âââ Main ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
print("[well] BOOT")
bus("module_boot", {"entry_id": "C9-2026-PHYS-001", "tier": 1})

datasets = [
    "polymathic-ai/MHD_64",
    "polymathic-ai/planetswe",
    "polymathic-ai/supernova_explosion_64",
    "polymathic-ai/post_neutron_star_merger",
    "polymathic-ai/active_matter",
    "polymathic-ai/acoustic_scattering",
    "polymathic-ai/RBC_2D",
    "polymathic-ai/RBC_3D"
]

success = 0
for ds in datasets:
    if probe_dataset(ds):
        success += 1

print("[well] DONE | %d/%d probed" % (success, len(datasets)))
bus("module_shutdown", {"probed": success, "total": len(datasets)})
