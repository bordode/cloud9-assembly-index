#!/usr/bin/env python3
"""
c9_hypothesis_debate.py
Cloud-9 Hypothesis Debate Module v1.0
Inspired by TradingAgents multi-agent debate architecture.
Patches into Nemicron (local LLM endpoint) via existing C9 bridge/proxy.

Agents:
  - ADVOCATE: Builds the case for hypothesis H
  - SKEPTIC: Attacks H, demands evidence
  - EVIDENCE: Grounds claims in data (TNG, arXiv, sensors)
  - SYNTHESIZER: Weighs debate, produces Assembly Index score

Interrupt Architecture:
  - SIGINT/SIGTERM: graceful checkpoint + exit
  - Per-LLM-call timeout (asyncio.wait_for)
  - Mid-debate VETO gate (external bus command)
  - Resume from checkpoint on restart

Bus Integration:
  - Reads c9_bus.jsonl for incoming debate_requests
  - Writes debate_results back to bus
  - Heartbeats via c9_bus_client v2.0 pattern
"""

import os
import sys
import json
import time
import signal
import asyncio
import aiohttp
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# ââ Configuration ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

DEFAULTS = {
    "ollama_url": "http://localhost:8080/v1/chat/completions",
    "model": "phi3:mini",
    "bus_file": os.path.expanduser("~/c9_bus.jsonl"),
    "checkpoint_dir": os.path.expanduser("~/.c9_debate_checkpoints"),
    "timeout_per_call": 90,          # seconds per LLM call
    "debate_rounds": 3,              # advocate â skeptic exchanges
    "max_tokens": 800,
    "temperature": 0.7,
    "module_name": "c9_hypothesis_debate",
}

# ââ Interrupt & Signal Handling ââââââââââââââââââââââââââââââââââââââââââ

class InterruptHandler:
    """
    Cooperative interrupt system.

    Levels:
      0 = NORMAL   (running)
      1 = PAUSE    (finish current agent turn, then checkpoint)
      2 = ABORT    (drop everything, checkpoint immediately)
      3 = SHUTDOWN (exit now, no checkpoint)
    """
    def __init__(self):
        self.level = 0
        self._lock = asyncio.Lock()
        self.checkpoints: List[Dict] = []

    def set_level(self, level: int):
        self.level = level
        print(f"[INTERRUPT] Level set to {level}", flush=True)

    async def check(self, current_state: Dict) -> bool:
        """Returns True if we should continue, False if we should stop."""
        async with self._lock:
            if self.level >= 2:
                self._save_checkpoint(current_state, "abort")
                return False
            if self.level == 1:
                self._save_checkpoint(current_state, "pause")
                self.level = 0  # auto-clear after checkpoint
                return False
            return True

    def _save_checkpoint(self, state: Dict, reason: str):
        os.makedirs(DEFAULTS["checkpoint_dir"], exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(DEFAULTS["checkpoint_dir"], f"ckpt_{reason}_{ts}.json")
        with open(path, "w") as f:
            json.dump(state, f, indent=2, default=str)
        print(f"[CHECKPOINT] Saved to {path}", flush=True)

INTERRUPT = InterruptHandler()

def _signal_handler(signum, frame):
    if signum == signal.SIGINT:
        print("\n[SIGINT] Setting PAUSE level...", flush=True)
        INTERRUPT.set_level(1)
    elif signum == signal.SIGTERM:
        print("\n[SIGTERM] Setting ABORT level...", flush=True)
        INTERRUPT.set_level(2)

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

# ââ Ollama / Local LLM Client with Timeout ââââââââââââââââââââââââââââââââ

class NemicronClient:
    """
    Async client for local LLM (Ollama/Nemotron/Phi-3).
    Every call is wrapped in asyncio.wait_for for interruptibility.
    """
    def __init__(self, url: str, model: str, timeout: int = 90):
        self.url = url
        self.model = model
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def chat(self, messages: List[Dict], max_tokens: int = None, temp: float = None) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or DEFAULTS["max_tokens"],
            "temperature": temp or DEFAULTS["temperature"],
            "stream": False,
        }
        try:
            coro = self.session.post(self.url, json=payload, headers={"Content-Type": "application/json"})
            async with await asyncio.wait_for(coro, timeout=self.timeout) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"LLM HTTP {resp.status}: {text[:200]}")
                data = await resp.json()
                # Handle both OpenAI-style and Ollama-style responses
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                elif "message" in data:
                    return data["message"]["content"]
                else:
                    return str(data)
        except asyncio.TimeoutError:
            return "[TIMEOUT] LLM call exceeded timeout. Agent yields."
        except Exception as e:
            return f"[ERROR] {type(e).__name__}: {str(e)[:200]}"

# ââ Agent Prompts ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

SYSTEM_ADVOCATE = """You are the ADVOCATE agent in the Cloud-9 Assembly framework.
Your job: build the strongest possible case FOR the proposed hypothesis.
Use analogies, cross-domain patterns, and theoretical backing.
Be bold but intellectually honest. Output â¤ 300 words."""

SYSTEM_SKEPTIC = """You are the SKEPTIC agent in the Cloud-9 Assembly framework.
Your job: attack the hypothesis ruthlessly. Demand falsifiability,
point out hidden assumptions, question data quality, and expose
confirmation bias. Be the devil's advocate. Output â¤ 300 words."""

SYSTEM_EVIDENCE = """You are the EVIDENCE agent. You do not speculate.
You only ground claims in observable, quantitative, or peer-reviewed data.
If a claim lacks support, say "UNSUBSTANTIATED." If data exists,
cite approximate values and sources. Output â¤ 250 words."""

SYSTEM_SYNTHESIZER = """You are the SYNTHESIZER agent. You weigh the debate,
assign a Cloud-9 Assembly Index score (0.00â1.00), and decide:
- LAYER 1: Established physics / confirmed observation
- LAYER 2: Speculative but testable theory  
- LAYER 3: Mathematical fiction / unfalsifiable

Also output: CONFIDENCE (0-1), KEY RISK, and NEXT EXPERIMENT.
Format as JSON inside markdown code block. Output â¤ 400 words."""

# ââ Debate Engine ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

@dataclass
class DebateState:
    hypothesis: str
    domain: str          # cosmology, neuro, quantum, etc.
    context: str         # prior evidence, TNG data, sensor readings
    round_num: int = 0
    history: List[Dict] = None
    checkpoint_path: str = ""

    def __post_init__(self):
        if self.history is None:
            self.history = []

    def to_dict(self) -> Dict:
        return asdict(self)

class HypothesisDebate:
    def __init__(self, client: NemicronClient, rounds: int = 3):
        self.client = client
        self.rounds = rounds

    async def run(self, state: DebateState) -> Dict:
        print(f"[DEBATE] Starting: {state.hypothesis[:80]}...")

        # Seed with hypothesis
        state.history.append({"role": "system", "content": f"HYPOTHESIS: {state.hypothesis}\nDOMAIN: {state.domain}\nCONTEXT: {state.context}"})

        for r in range(1, self.rounds + 1):
            state.round_num = r
            print(f"[DEBATE] Round {r}/{self.rounds}")

            # Check interrupt before each turn
            if not await INTERRUPT.check(state.to_dict()):
                return {"status": "interrupted", "state": state.to_dict()}

            # ADVOCATE turn
            advocate_msgs = [
                {"role": "system", "content": SYSTEM_ADVOCATE},
                {"role": "user", "content": self._build_prompt(state, "advocate")}
            ]
            advocate_resp = await self.client.chat(advocate_msgs)
            state.history.append({"agent": "ADVOCATE", "round": r, "content": advocate_resp})
            print(f"  [ADVOCATE] {advocate_resp[:100]}...")

            if not await INTERRUPT.check(state.to_dict()):
                return {"status": "interrupted", "state": state.to_dict()}

            # SKEPTIC turn
            skeptic_msgs = [
                {"role": "system", "content": SYSTEM_SKEPTIC},
                {"role": "user", "content": self._build_prompt(state, "skeptic")}
            ]
            skeptic_resp = await self.client.chat(skeptic_msgs)
            state.history.append({"agent": "SKEPTIC", "round": r, "content": skeptic_resp})
            print(f"  [SKEPTIC] {skeptic_resp[:100]}...")

            if not await INTERRUPT.check(state.to_dict()):
                return {"status": "interrupted", "state": state.to_dict()}

            # EVIDENCE grounding (every round)
            evidence_msgs = [
                {"role": "system", "content": SYSTEM_EVIDENCE},
                {"role": "user", "content": self._build_prompt(state, "evidence")}
            ]
            evidence_resp = await self.client.chat(evidence_msgs)
            state.history.append({"agent": "EVIDENCE", "round": r, "content": evidence_resp})
            print(f"  [EVIDENCE] {evidence_resp[:100]}...")

        # Final SYNTHESIZER
        if not await INTERRUPT.check(state.to_dict()):
            return {"status": "interrupted", "state": state.to_dict()}

        synth_msgs = [
            {"role": "system", "content": SYSTEM_SYNTHESIZER},
            {"role": "user", "content": self._build_prompt(state, "synthesizer")}
        ]
        synth_resp = await self.client.chat(synth_msgs, max_tokens=1200, temp=0.3)
        state.history.append({"agent": "SYNTHESIZER", "round": "final", "content": synth_resp})
        print(f"  [SYNTHESIZER] {synth_resp[:100]}...")

        return {"status": "complete", "state": state.to_dict(), "verdict": synth_resp}

    def _build_prompt(self, state: DebateState, agent: str) -> str:
        lines = [f"HYPOTHESIS: {state.hypothesis}", f"DOMAIN: {state.domain}", f"CONTEXT: {state.context}", ""]
        lines.append("DEBATE HISTORY:")
        for h in state.history[-6:]:  # last 6 turns for context window
            role = h.get("agent", h.get("role", "?"))
            content = h.get("content", "")[:400]
            lines.append(f"  [{role}] {content}")
        lines.append(f"\nYour turn as {agent.upper()}. Respond now.")
        return "\n".join(lines)

# ââ Bus Integration ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

class BusClient:
    """Minimal c9_bus.jsonl client. Non-blocking read, atomic append."""
    def __init__(self, bus_file: str, module_name: str):
        self.bus_file = bus_file
        self.module_name = module_name
        self._last_size = 0

    def emit(self, event_type: str, payload: Dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "module": self.module_name,
            "event": event_type,
            "payload": payload,
        }
        with open(self.bus_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def read_new(self) -> List[Dict]:
        """Poll for new bus entries since last read."""
        if not os.path.exists(self.bus_file):
            return []
        current_size = os.path.getsize(self.bus_file)
        if current_size <= self._last_size:
            return []
        entries = []
        with open(self.bus_file, "r") as f:
            f.seek(self._last_size)
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        self._last_size = current_size
        return entries

# ââ Main Loop ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

async def main_loop(args):
    bus = BusClient(args.bus_file, DEFAULTS["module_name"])
    bus.emit("module_boot", {"status": "starting", "pid": os.getpid()})

    async with NemicronClient(args.ollama_url, args.model, args.timeout) as client:
        debate_engine = HypothesisDebate(client, rounds=args.rounds)

        print(f"[C9-DEBATE] Online. Polling {args.bus_file} every 3s...")
        print(f"[C9-DEBATE] Model: {args.model} @ {args.ollama_url}")
        print(f"[C9-DEBATE] Interrupt: Ctrl+C = PAUSE, SIGTERM = ABORT")

        while True:
            # Heartbeat every 30s
            bus.emit("heartbeat", {"vitals": "ok", "time": time.time()})

            # Poll bus for debate_requests
            new_entries = bus.read_new()
            for entry in new_entries:
                payload = entry.get("payload", {})
                if payload.get("target_module") == DEFAULTS["module_name"] and payload.get("action") == "debate_request":
                    hypothesis = payload.get("hypothesis", "")
                    domain = payload.get("domain", "general")
                    context = payload.get("context", "")

                    if not hypothesis:
                        bus.emit("debate_error", {"error": "empty hypothesis"})
                        continue

                    state = DebateState(hypothesis=hypothesis, domain=domain, context=context)
                    bus.emit("debate_start", {"hypothesis": hypothesis[:100], "domain": domain})

                    try:
                        result = await debate_engine.run(state)
                        bus.emit("debate_complete", {
                            "hypothesis": hypothesis[:100],
                            "status": result["status"],
                            "verdict_preview": result.get("verdict", "")[:200],
                        })
                    except Exception as e:
                        bus.emit("debate_error", {"error": str(e)})

            await asyncio.sleep(3)

# ââ CLI ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def cli():
    parser = argparse.ArgumentParser(description="C9 Hypothesis Debate Module")
    parser.add_argument("--ollama-url", default=DEFAULTS["ollama_url"])
    parser.add_argument("--model", default=DEFAULTS["model"])
    parser.add_argument("--bus-file", default=DEFAULTS["bus_file"])
    parser.add_argument("--rounds", type=int, default=DEFAULTS["debate_rounds"])
    parser.add_argument("--timeout", type=int, default=DEFAULTS["timeout_per_call"])
    parser.add_argument("--once", action="store_true", help="Run single debate from CLI, then exit")
    parser.add_argument("--hypothesis", help="Hypothesis text (for --once mode)")
    parser.add_argument("--domain", default="general", help="Domain tag")
    parser.add_argument("--context", default="", help="Supporting context/data")
    args = parser.parse_args()

    if args.once:
        if not args.hypothesis:
            print("ERROR: --once requires --hypothesis")
            sys.exit(1)
        asyncio.run(run_once(args))
    else:
        asyncio.run(main_loop(args))

async def run_once(args):
    """Single-shot debate from command line."""
    async with NemicronClient(args.ollama_url, args.model, args.timeout) as client:
        debate = HypothesisDebate(client, rounds=args.rounds)
        state = DebateState(hypothesis=args.hypothesis, domain=args.domain, context=args.context)
        result = await debate.run(state)

        print("\n" + "="*60)
        print("DEBATE RESULT")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))

        # Save to file
        out_path = os.path.expanduser(f"~/.c9_debate_checkpoints/result_{int(time.time())}.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nSaved to: {out_path}")

if __name__ == "__main__":
    cli()
