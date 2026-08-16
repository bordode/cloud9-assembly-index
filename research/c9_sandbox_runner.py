#!/usr/bin/env python3
"""
C9 Hypothesis Debate Sandbox Runner v1.2
Connects to Ollama (port 11434) and runs 4-agent debate on a Cloud-9 entry.
Appends results to c9_bus.jsonl

Usage:
    python3 c9_sandbox_runner.py C9-2026-PHYS-007_programmable_resonance_assembly.json
"""

import json
import sys
import os
import requests
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"
BUS_FILE = os.path.expanduser("~/cloud9/c9_bus.jsonl")
TIMEOUT = 120

def ollama_generate(prompt, model=MODEL, temperature=0.7):
    """Query local Ollama instance."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 800}
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json().get("response", "[NO RESPONSE]").strip()
    except Exception as e:
        return f"[ERROR: {e}]"

def load_entry(path):
    with open(path, 'r') as f:
        return json.load(f)

def build_prompt(agent_role, entry):
    title = entry["title"]
    thesis = entry["core_thesis"]["statement"]
    anchors = json.dumps(entry["empirical_anchors"], indent=2)
    extensions = json.dumps(entry["speculative_extensions"], indent=2)

    base = f"""You are the {agent_role} agent in the Cloud-9 Hypothesis Debate Module.
Your job is to evaluate the following scientific entry rigorously.

ENTRY TITLE: {title}
CORE THESIS: {thesis}

EMPIRICAL ANCHORS:
{anchors}

SPECULATIVE EXTENSIONS:
{extensions}

"""

    if agent_role == "ADVOCATE":
        return base + """As ADVOCATE, your job is to argue FOR the maximum possible Assembly Index score and layer assignment.
Find every piece of supporting evidence. Emphasize the strength of the empirical anchors. Argue that the speculative extensions are natural, physically consistent extensions of proven phenomena.

Output format:
- Verdict: PASS or CONDITIONAL PASS
- Recommended Score: 0.00-1.00
- Recommended Layer: L1 / L2 / L3
- Key Arguments: (bullet points)
- Confidence: High / Medium / Low
"""
    elif agent_role == "SKEPTIC":
        return base + """As SKEPTIC, your job is to attack this entry ruthlessly. Find every weakness, gap, unsupported assumption, and logical flaw.
Question the scaling claims. Attack the lack of experimental evidence for bulk coupling. Point out where the analogy breaks down. Demand explicit energy accounting.

Output format:
- Verdict: PASS / CONDITIONAL PASS / FAIL
- Recommended Score: 0.00-1.00
- Recommended Layer: L1 / L2 / L3
- Key Criticisms: (bullet points)
- Dealbreakers: (list any claims that should be quarantined as L3)
- Confidence: High / Medium / Low
"""
    elif agent_role == "EVIDENCE":
        return base + """As EVIDENCE, your job is to assess the factual accuracy and sourcing of every claim.
Check whether the empirical anchors are correctly described. Verify the physics references. Note if any score seems inflated or deflated relative to the actual literature.

Output format:
- Verdict: PASS / CONDITIONAL PASS / FAIL
- Recommended Score: 0.00-1.00
- Factual Accuracy: (assessment of each anchor)
- Missing Evidence: (what should have been cited but wasn't)
- Score Adjustments: (which scores need correction and why)
- Confidence: High / Medium / Low
"""
    elif agent_role == "SYNTHESIZER":
        return base + """As SYNTHESIZER, your job is to reconcile the ADVOCATE, SKEPTIC, and EVIDENCE positions into a single coherent verdict.
You are the final arbiter. Consider all arguments, weight the evidence, and produce the definitive Cloud-9 assessment.

Output format:
- Final Verdict: PASS / CONDITIONAL PASS / FAIL
- Final Assembly Index Score: 0.00-1.00
- Final Layer Assignment: L1 / L2 / L3 (with sub-classification if composite)
- Rationale: (2-3 sentences)
- Key Risks: (list)
- Next Experiments: (list)
- Confidence: High / Medium / Low
- Agent Consensus: (how much agreement existed)
"""
    else:
        return base

def append_to_bus(record):
    os.makedirs(os.path.dirname(BUS_FILE), exist_ok=True)
    with open(BUS_FILE, 'a') as f:
        f.write(json.dumps(record) + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 c9_sandbox_runner.py <entry.json>")
        sys.exit(1)

    entry_path = sys.argv[1]
    entry = load_entry(entry_path)
    entry_id = entry["entry_id"]

    print(f"[C9 SANDBOX] Initiating debate for {entry_id}...")
    print(f"[C9 SANDBOX] Ollama endpoint: {OLLAMA_URL}")
    print(f"[C9 SANDBOX] Model: {MODEL}")
    print("=" * 60)

    agents = ["ADVOCATE", "SKEPTIC", "EVIDENCE", "SYNTHESIZER"]
    results = {}

    for agent in agents:
        print(f"\n>>> Running {agent}...")
        prompt = build_prompt(agent, entry)
        response = ollama_generate(prompt)
        results[agent] = response
        print(f"[{agent}] Response received ({len(response)} chars)")
        # Print first 200 chars for live feedback
        preview = response.replace("\n", " ")[:200]
        print(f"   Preview: {preview}...")

    # Compile final report
    final_report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "C9-HYPOTHESIS-DEBATE-MODULE",
        "version": "1.2",
        "entry_id": entry_id,
        "event_type": "SANDBOX_COMPLETED",
        "model": MODEL,
        "agent_outputs": results,
        "manual_simulation": False,
        "note": "This is a LIVE sandbox run via Ollama."
    }

    # Append to bus
    append_to_bus(final_report)

    # Also save standalone report
    report_path = entry_path.replace(".json", "_SANDBOX_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump(final_report, f, indent=2)

    print("\n" + "=" * 60)
    print(f"[C9 SANDBOX] Debate complete for {entry_id}")
    print(f"[C9 SANDBOX] Bus log appended: {BUS_FILE}")
    print(f"[C9 SANDBOX] Report saved: {report_path}")
    print("=" * 60)

    # Print SYNTHESIZER output for immediate reading
    print("\n>>> FINAL SYNTHESIZER VERDICT:")
    print(results["SYNTHESIZER"])

if __name__ == "__main__":
    main()
