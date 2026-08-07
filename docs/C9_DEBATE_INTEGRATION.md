# C9 Hypothesis Debate Module â Integration Guide

## Files

| File | Purpose |
|------|---------|
| `c9_hypothesis_debate.py` | Main debate engine (ADVOCATE/SKEPTIC/EVIDENCE/SYNTHESIZER) |
| `c9_interrupt_controller.py` | Distributed signal layer â any module can interrupt any other via bus |

## Quick Start

### 1. Single-shot test (no bus needed)

```bash
cd ~
python3 c9_hypothesis_debate.py --once \
  --hypothesis "Dark matter halos exhibit non-random complexity spikes before major mergers" \
  --domain "cosmology" \
  --context "TNG100-1 snapshot 99, 38 quiescent halos analyzed, A_c mean 14.8"
```

This talks directly to your Ollama/Nemicron on port 8080 (phi3:mini).

### 2. Bus-integrated daemon mode

```bash
nohup python3 ~/c9_hypothesis_debate.py --bus-file ~/c9_bus.jsonl >> ~/c9_debate.log 2>&1 &
```

Then inject a debate request from any other module:

```bash
python3 -c "
import json, datetime
entry = {
    'timestamp': datetime.datetime.now().isoformat(),
    'module': 'manual_injector',
    'event': 'debate_request',
    'payload': {
        'target_module': 'c9_hypothesis_debate',
        'action': 'debate_request',
        'hypothesis': 'Schumann resonance at 7.83 kHz can be encoded into KiSS-SIDM scattering kernels',
        'domain': 'materials_physics',
        'context': 'Copper-oxide weave, 850 LSB threshold, Qâ90, irreversible lattice reorientation observed'
    }
}
with open('/data/data/com.termux/files/home/c9_bus.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
"
```

### 3. Interrupt Controller (run alongside)

```bash
nohup python3 ~/c9_interrupt_controller.py >> ~/c9_interrupt.log 2>&1 &
```

Now any module can pause/abort the debate without knowing its PID:

```bash
python3 -c "
import json, datetime
entry = {
    'timestamp': datetime.datetime.now().isoformat(),
    'module': 'jarvis_interface',
    'event': 'command',
    'payload': {
        'target_module': 'c9_hypothesis_debate',
        'action': 'pause',
        'level': 1
    }
}
with open('/data/data/com.termux/files/home/c9_bus.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
"
```

The controller reads this, looks up the PID from registry, and sends SIGINT.

## Interrupt Architecture Deep Dive

### Why This Pattern Matters

Your existing manifolds (sovereign, physical) use **precision gates** and **VETO** to modulate flow. But those are *internal* to each module. The interrupt layer is *external* â any module can inject a stop signal into any other. This is the difference between:

- **Introspective control** (module decides for itself)
- **Extrospective control** (ecosystem decides for the module)

Both are needed for a living system.

### Signal Semantics

| Signal | Meaning | Use Case |
|--------|---------|----------|
| SIGINT (Ctrl+C) | PAUSE | User wants to check state, debate resumes later from checkpoint |
| SIGTERM | ABORT | Debate is wrong/harmful, save checkpoint and die |
| SIGKILL | KILL | Emergency only, no checkpoint, immediate death |

### Cooperative vs Preemptive

The debate module uses **cooperative** interruption:
- It checks `INTERRUPT.check()` between every agent turn
- If interrupted, it saves JSON checkpoint and exits cleanly
- On restart, it could resume (resume logic not yet implemented â see TODO)

This is safer than preemptive killing mid-LLM-call, which could corrupt the Ollama context or leave the bus in a half-written state.

### Async Timeout Layer

Every LLM call is wrapped in `asyncio.wait_for(coro, timeout=90)`. This means:
- If phi3:mini hangs or Ollama is overloaded, the call returns `[TIMEOUT]` instead of blocking forever
- The debate continues with degraded output rather than freezing
- You can lower timeout for faster fail-fast behavior: `--timeout 30`

### Checkpoint Format

```json
{
  "hypothesis": "...",
  "domain": "cosmology",
  "round_num": 2,
  "history": [...],
  "interrupted_at": "2026-08-01T11:30:00",
  "reason": "pause"
}
```

Saved to `~/.c9_debate_checkpoints/ckpt_pause_20260801_113000.json`

## Patching into c9_unified_launcher.py

Add this stanza to your launcher's module list:

```python
MODULES = [
    # ... existing modules ...
    {
        "name": "c9_hypothesis_debate",
        "script": "c9_hypothesis_debate.py",
        "args": ["--bus-file", "~/c9_bus.jsonl", "--timeout", "90"],
        "auto_restart": True,
        "critical": False,  # debate can be down without killing the entity
    },
    {
        "name": "c9_interrupt_controller",
        "script": "c9_interrupt_controller.py",
        "args": ["--bus-file", "~/c9_bus.jsonl"],
        "auto_restart": True,
        "critical": True,  # if this dies, ecosystem loses emergency brake
    },
]
```

## Nemicron (Ollama) Endpoint Mapping

The debate module defaults to `http://localhost:8080/v1/chat/completions`. 

Your current port map (from memory):
- Ollama API: port 8080 â (matches default)
- If you move Ollama back to 11434, use: `--ollama-url http://localhost:11434/v1/chat/completions`
- NVIDIA proxy (8788) is OpenAI-compatible and could also work

## Design Decisions

1. **Why not use LangGraph like TradingAgents?** 
   LangGraph is heavy (numpy, pydantic, langchain). Your Termux disk is 81% full. This module is pure stdlib + aiohttp. ~16KB vs ~200MB dependency tree.

2. **Why not stream LLM responses?**
   Streaming is harder to interrupt cleanly. Non-streaming gives us atomic responses we can checkpoint between.

3. **Why 4 agents instead of 9?**
   TradingAgents uses 9 because finance has many specialized domains. For scientific hypothesis evaluation, 4 is the minimal viable debate topology: propose â attack â ground â judge.

4. **Why JSON output from SYNTHESIZER?**
   Structured output lets downstream C9 modules (oracle, bridge) parse the Assembly Index score and layer assignment without regex hacks. Even if phi3:mini garbles the JSON, the raw text is still in the history.

## TODO / Future Extensions

- [ ] Resume from checkpoint: `python3 c9_hypothesis_debate.py --resume ~/.c9_debate_checkpoints/ckpt_*.json`
- [ ] Add RISK_MANAGER agent (like TradingAgents) that evaluates compute cost and time before debate starts
- [ ] Integrate with AutoBaby v2 so discovered hypotheses auto-trigger debates
- [ ] Add `c9_evolution` endpoint so BIRTH v3 can trigger debates via HTTP instead of bus
- [ ] Parallel agent turns (advocate + skeptic simultaneously) to reduce latency
- [ ] Temperature annealing: start hot (creative) in round 1, end cold (precise) in round 3

## Emergency Commands

```bash
# Pause an ongoing debate
pkill -INT -f c9_hypothesis_debate

# Abort and checkpoint
pkill -TERM -f c9_hypothesis_debate

# Kill immediately (no checkpoint)
pkill -KILL -f c9_hypothesis_debate

# View latest checkpoint
ls -lt ~/.c9_debate_checkpoints/ | head -5
```
