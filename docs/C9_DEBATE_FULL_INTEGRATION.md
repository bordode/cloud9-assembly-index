# C9 Debate Ecosystem â Full Deployment Guide
## AutoBaby Integration + Daemon Mode

---

## 1. Deploy Everything (One Block)

Copy-paste this entire block into Termux:

```bash
# 1. Install screen (if missing)
pkg install screen -y 2>/dev/null || true

# 2. Download startup script
cat > ~/c9_debate_startup.sh << 'SHEOF'
#!/bin/bash
echo "[C9-DEBATE] Starting debate ecosystem..."

for s in c9_debate c9_interrupt c9_bridge; do
    screen -S "$s" -X quit 2>/dev/null
done
sleep 1

if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "[WARNING] Ollama not on 127.0.0.1:11434. Start it: ollama serve"
fi

if grep -q "localhost:8788" ~/c9_hypothesis_debate.py 2>/dev/null; then
    sed -i 's|localhost:8788|127.0.0.1:11434|g' ~/c9_hypothesis_debate.py
    sed -i 's|localhost:11434|127.0.0.1:11434|g' ~/c9_hypothesis_debate.py
    echo "[C9-DEBATE] Patched defaults"
fi

screen -dmS c9_interrupt bash -c 'python3 ~/c9_interrupt_controller.py --bus-file ~/c9_bus.jsonl'
screen -dmS c9_debate bash -c 'python3 ~/c9_hypothesis_debate.py --bus-file ~/c9_bus.jsonl --model phi3:mini --timeout 300'
screen -dmS c9_bridge bash -c 'python3 ~/c9_autobaby_debate_bridge.py --bus-file ~/c9_bus.jsonl --min-confidence 0.50'

sleep 1
echo "[C9-DEBATE] Screens started:"
screen -ls | grep c9_ || echo "  (none yet)"

python3 -c "
import json, datetime
entry = {
    'timestamp': datetime.datetime.now().isoformat(),
    'module': 'c9_debate_startup',
    'event': 'module_boot',
    'payload': {'status': 'screens_started', 'screens': ['c9_interrupt', 'c9_debate', 'c9_bridge']}
}
with open('/data/data/com.termux/files/home/c9_bus.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '
')
"
SHEOF
chmod +x ~/c9_debate_startup.sh

# 3. Download AutoBaby emitter helper
cat > ~/autobaby_bus_emitter.py << 'PYEOF'
import os, json
from datetime import datetime

BUS_FILE = os.path.expanduser("~/c9_bus.jsonl")

def emit_discovery(hypothesis: str, confidence: float, domain: str = "general", context: str = ""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "module": "autobaby",
        "event": "autobaby_discovery",
        "payload": {
            "hypothesis": hypothesis,
            "confidence": confidence,
            "domain": domain,
            "context": context,
            "source_module": "autobaby"
        }
    }
    with open(BUS_FILE, "a") as f:
        f.write(json.dumps(entry) + "
")
    print(f"[AUTOBABY] Emitted: {hypothesis[:60]}... (conf={confidence})")

def emit_discovery_from_text(text: str, confidence: float = 0.60, domain: str = "general"):
    hypothesis = text[:300]
    for line in text.split("
"):
        if line.lower().startswith(("hypothesis:", "finding:")):
            hypothesis = line.split(":", 1)[1].strip()
            break
    emit_discovery(hypothesis, confidence, domain, text[:500])
PYEOF
chmod +x ~/autobaby_bus_emitter.py

echo ""
echo "=== DEPLOYED ==="
echo "Startup script: ~/c9_debate_startup.sh"
echo "AutoBaby emitter: ~/autobaby_bus_emitter.py"
echo ""
echo "Next steps:"
echo "  1. Start Ollama: ollama serve (in another session)"
echo "  2. Run: bash ~/c9_debate_startup.sh"
echo "  3. Check: screen -ls"
```

---

## 2. Start the Ecosystem

### Step A: Ollama (dedicated session)
1. Swipe from left â **New Session**
2. Type: `ollama serve`
3. **Leave it open.** This is Ollama's home.

### Step B: Debate Ecosystem (main session)
```bash
bash ~/c9_debate_startup.sh
```

### Step C: Verify
```bash
screen -ls
```
Should show:
```
    c9_bridge	(Detached)
    c9_debate	(Detached)
    c9_interrupt	(Detached)
```

---

## 3. AutoBaby Integration

### Option A: Import the emitter (recommended)

In your AutoBaby v2 code, add:

```python
import sys
sys.path.insert(0, "/data/data/com.termux/files/home")
from autobaby_bus_emitter import emit_discovery

# When AutoBaby finds something
def on_discovery(hypothesis_text, confidence, domain="general", source=""):
    emit_discovery(
        hypothesis=hypothesis_text,
        confidence=confidence,
        domain=domain,
        context=source
    )
```

### Option B: Manual bus injection (for testing)

```bash
python3 -c "
import sys
sys.path.insert(0, '/data/data/com.termux/files/home')
from autobaby_bus_emitter import emit_discovery

emit_discovery(
    hypothesis='QPLS from inspiraling SMBH binaries encodes orbital dynamics in photometric lightcurves',
    confidence=0.82,
    domain='cosmology',
    context='arXiv:2506.16544'
)
"
```

---

## 4. Monitor Everything

| What | Command |
|---|---|
| List screens | `screen -ls` |
| Watch debate live | `screen -r c9_debate` (Ctrl+A then D to detach) |
| Watch bridge live | `screen -r c9_bridge` |
| Watch interrupt live | `screen -r c9_interrupt` |
| Check bus | `tail -20 ~/c9_bus.jsonl` |
| Check debate results | `ls -lt ~/.c9_debate_checkpoints/` |
| Check bridge state | `cat ~/.c9_debate_bridge_state.json` |

---

## 5. How the Pipeline Works (End-to-End)

```
âââââââââââââââ     ââââââââââââââââ     âââââââââââââââââââ
â   AutoBaby  ââââââºâ  C9 Bus      ââââââºâ Debate Bridge   â
â  (research) â     â  (jsonl)     â     â (quality gate)  â
âââââââââââââââ     ââââââââââââââââ     âââââââââââââââââââ
                                                  â
                                                  â¼
                                         âââââââââââââââââââ
                                         â c9_hypothesis   â
                                         â _debate.py      â
                                         â (4-agent review)â
                                         âââââââââââââââââââ
                                                  â
                                                  â¼
                                         âââââââââââââââââââ
                                         â  SYNTHESIZER    â
                                         â  JSON verdict   â
                                         â  A_c, Layer,    â
                                         â  Confidence     â
                                         âââââââââââââââââââ
                                                  â
                                                  â¼
                                         âââââââââââââââââââ
                                         â  C9 Bus         â
                                         â  collection_    â
                                         â  entry event    â
                                         âââââââââââââââââââ
                                                  â
                                                  â¼
                                         âââââââââââââââââââ
                                         â  Librarian      â
                                         â  (indexes)      â
                                         âââââââââââââââââââ
                                                  â
                                                  â¼
                                         âââââââââââââââââââ
                                         â  Weekly GitHub  â
                                         â  Upload         â
                                         âââââââââââââââââââ
```

**Flow:**
1. AutoBaby discovers hypothesis â writes `autobaby_discovery` to bus
2. Bridge sees it â checks confidence â¥ 0.50, not duplicate, not rate-limited
3. Bridge injects `debate_request` â debate module picks it up
4. Debate runs (ADVOCATE â SKEPTIC â EVIDENCE â SYNTHESIZER)
5. Debate emits `debate_complete` â bridge parses JSON
6. Bridge emits `collection_entry` â ready for Librarian/GitHub

---

## 6. Rate Limits & Safety

| Limit | Value | Purpose |
|---|---|---|
| Min confidence | 0.50 | Don't debate weak hypotheses |
| Rate limit | 10 min between debates | Prevent bus spam |
| Dedup | SHA256 hash of hypothesis | Never debate same thing twice |
| Max remembered | 500 hypotheses | Prevent state file bloat |
| Timeout per call | 300s (phi3:mini) | Don't hang forever |
| Interrupt | SIGINT = PAUSE, SIGTERM = ABORT | Graceful stops |

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `screen: command not found` | `pkg install screen -y` |
| Ollama not responding | Start `ollama serve` in dedicated session |
| Screens not showing | `screen -ls` â if empty, run startup script again |
| Debates timing out | Ollama overloaded; use `nemotron-lite` for speed or reduce `--timeout` |
| SKEPTIC refuses to argue | Model safety alignment; switch to `phi3:mini` |
| JSON garbled | SYNTHESIZER prompt issue; module auto-patched in v1.1 |

---

## 8. Files Reference

| File | Purpose |
|---|---|
| `~/c9_hypothesis_debate.py` | 4-agent debate engine |
| `~/c9_interrupt_controller.py` | Distributed signal layer |
| `~/c9_autobaby_debate_bridge.py` | AutoBaby â Debate pipeline |
| `~/autobaby_bus_emitter.py` | Drop-in helper for AutoBaby |
| `~/c9_debate_startup.sh` | One-command daemon startup |
| `~/.c9_debate_checkpoints/` | Debate transcripts + results |
| `~/.c9_debate_bridge_state.json` | Dedup + rate-limit state |
| `~/c9_bus.jsonl` | Shared event bus |

---

## 9. Add to c9_unified_launcher.py

If you want the launcher to manage these too, add to its `MODULES` list:

```python
    {
        "name": "c9_debate_startup",
        "script": "c9_debate_startup.sh",
        "args": [],
        "auto_restart": False,  # screen handles this internally
        "critical": False,
    },
```

Or keep them separate â the screen approach is more reliable than nohup in Termux.

---

**Status: READY FOR PRODUCTION**

The debate module is validated, the bridge is wired, AutoBaby can emit discoveries, and the pipeline produces scored, layered collection entries automatically.
