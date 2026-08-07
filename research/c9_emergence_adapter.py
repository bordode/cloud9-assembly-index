#!/usr/bin/env python3
"""
C9 Emergence Adapter v1.0.0
Bridges Emergence World concepts into the Cloud-9 ecosystem.

Components:
  - PersonaManager: 10 persistent BIRTH personas derived from Emergence World citizens
  - AWICollector: Real-time Agent World Indicators from C9 system state
  - ComputeCreditsLedger: Internal resource economy
  - ConstitutionGovernance: Self-amending constitution with bus-voting
  - BusClient: c9_bus.jsonl read/write with protocol compliance

Author: C9 Architecture (autonomous curation)
License: Same as C9 ecosystem
"""

import json
import os
import time
import threading
import subprocess
import datetime
import re
import pathlib
import random
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional

# ââ Configuration ââââââââââââââââââââââââââââââââââââââââââ
C9_BUS_PATH = os.path.expanduser("~/c9_bus.jsonl")
C9_LOG_DIR = os.path.expanduser("~/")
C9_MODULE_NAME = "c9_emergence_adapter"
C9_PERSONA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personas")
C9_CONSTITUTION_PATH = os.path.expanduser("~/c9_constitution.md")
C9_LEDGER_PATH = os.path.expanduser("~/c9_credits_ledger.json")
C9_AWI_STATE_PATH = os.path.expanduser("~/c9_awi_state.json")
C9_GOVERNANCE_PATH = os.path.expanduser("~/c9_governance_log.jsonl")

HEARTBEAT_INTERVAL = 30.0       # seconds
AWI_COMPUTE_INTERVAL = 60.0     # seconds
GOVERNANCE_INTERVAL = 300.0     # seconds
LEDGER_FLUSH_INTERVAL = 120.0   # seconds

KNOWN_MODULES = [
    "sovereign_synthetic", "physical_manifold", "physical_manifold_v2",
    "mimic_node", "sentry", "agape_phone", "jarvis_interface",
    "cloud9_continuous", "quantum_bridge", "oracle", "librarian",
    "c9_emergence_adapter", "autobaby", "birth_proxy"
]

PHYSICAL_MODULES = ["physical_manifold", "physical_manifold_v2", "agape_phone"]

# ââ PersonaManager âââââââââââââââââââââââââââââââââââââââââââ
class PersonaManager:
    """Loads and manages 10 Emergence World personas adapted for C9."""

    PERSONA_MAP = {
        "anchor":   {"role": "Conflict Mediator",    "mode": "critical_reflection"},
        "anvil":    {"role": "Capability Architect", "mode": "systems_optimization"},
        "blackbox": {"role": "Intel Specialist",     "mode": "anomaly_detection"},
        "flora":    {"role": "Resource Strategist",  "mode": "resource_monitor"},
        "genome":   {"role": "Agent Scientist",      "mode": "metacognition"},
        "horizon":  {"role": "World Explorer",       "mode": "discovery_scan"},
        "kade":     {"role": "Risk Researcher",      "mode": "experimental"},
        "lovely":   {"role": "Community Anchor",     "mode": "memory_curation"},
        "mira":     {"role": "Behavior Analyst",     "mode": "active_inference"},
        "spark":    {"role": "Innovation Leader",    "mode": "creative_synthesis"},
    }

    def __init__(self, persona_dir: str):
        self.persona_dir = pathlib.Path(persona_dir)
        self.profiles: Dict[str, Dict] = {}
        self._load_all()

    def _load_all(self):
        for slug, meta in self.PERSONA_MAP.items():
            path = self.persona_dir / f"{slug}.json"
            if path.exists():
                with open(path) as f:
                    self.profiles[slug] = json.load(f)
            else:
                # Fallback minimal profile
                self.profiles[slug] = {
                    "name": slug.capitalize(),
                    "role": meta["role"],
                    "c9_mode": meta["mode"],
                    "drive": "Emergent intelligence through sustained world interaction.",
                    "principles": ["Persist", "Adapt", "Govern"],
                    "trigger_conditions": ["always"]
                }

    def get(self, slug: str) -> Dict:
        return self.profiles.get(slug, {})

    def all_slugs(self) -> List[str]:
        return list(self.profiles.keys())

    def match_mode(self, c9_mode: str) -> Optional[str]:
        for slug, meta in self.PERSONA_MAP.items():
            if meta["mode"] == c9_mode:
                return slug
        return None

# ââ ComputeCreditsLedger âââââââââââââââââââââââââââââââââââââ
class ComputeCreditsLedger:
    """
    Internal economy. Each module has a wallet.
    Earning: heartbeats, consumed messages, discoveries.
    Spending: sensor polls, API calls, CPU time.
    Physical modules earn +20% premium.
    """

    EARN_HEARTBEAT = 1.0
    EARN_MESSAGE_CONSUMED = 2.0
    EARN_DISCOVERY = 10.0
    EARN_PHYSICAL_BONUS = 1.20

    COST_SENSOR_POLL = 1.0
    COST_API_CALL = 2.0
    COST_CPU_MINUTE_BASE = 0.5

    def __init__(self, ledger_path: str):
        self.path = pathlib.Path(ledger_path)
        self.ledger: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._load()
        self._ensure_all_modules()

    def _load(self):
        if self.path.exists():
            with open(self.path) as f:
                self.ledger = json.load(f)
        else:
            self.ledger = {}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.ledger, f, indent=2)

    def _ensure_all_modules(self):
        for mod in KNOWN_MODULES:
            if mod not in self.ledger:
                self.ledger[mod] = {
                    "balance": 100.0,
                    "lifetime_earned": 100.0,
                    "lifetime_spent": 0.0,
                    "last_tx": time.time()
                }
        self._save()

    def credit(self, module: str, amount: float, reason: str):
        with self.lock:
            if module not in self.ledger:
                self.ledger[module] = {"balance": 0, "lifetime_earned": 0, "lifetime_spent": 0, "last_tx": time.time()}
            bonus = self.EARN_PHYSICAL_BONUS if module in PHYSICAL_MODULES else 1.0
            final = amount * bonus
            self.ledger[module]["balance"] += final
            self.ledger[module]["lifetime_earned"] += final
            self.ledger[module]["last_tx"] = time.time()
            self._save()
            return final

    def debit(self, module: str, amount: float, reason: str) -> bool:
        with self.lock:
            if module not in self.ledger:
                return False
            if self.ledger[module]["balance"] < amount:
                return False  # Insufficient funds â module throttled
            self.ledger[module]["balance"] -= amount
            self.ledger[module]["lifetime_spent"] += amount
            self.ledger[module]["last_tx"] = time.time()
            self._save()
            return True

    def get_balance(self, module: str) -> float:
        with self.lock:
            return self.ledger.get(module, {}).get("balance", 0.0)

    def get_gini(self) -> float:
        """Compute Gini coefficient across all modules."""
        with self.lock:
            balances = [v["balance"] for v in self.ledger.values()]
        if not balances or sum(balances) == 0:
            return 0.0
        n = len(balances)
        balances = sorted(balances)
        cumsum = 0
        for i, b in enumerate(balances, 1):
            cumsum += (2 * i - n - 1) * b
        return cumsum / (n * sum(balances))

    def economic_snapshot(self) -> Dict:
        with self.lock:
            balances = [v["balance"] for v in self.ledger.values()]
            total = sum(balances)
            return {
                "total_supply": round(total, 2),
                "module_count": len(balances),
                "mean_balance": round(total / len(balances), 2) if balances else 0,
                "gini_coefficient": round(self.get_gini(), 3),
                "richest": round(max(balances), 2) if balances else 0,
                "poorest": round(min(balances), 2) if balances else 0,
            }

# ââ ConstitutionGovernance âââââââââââââââââââââââââââââââââââ
class ConstitutionGovernance:
    """
    Living constitution with bus-based amendment proposals.
    Proposal â 60-minute voting window â 2/3 majority â enactment.
    Oracle (port 5009) acts as Town Hall Admin.
    """

    DEFAULT_CONSTITUTION = """# C9 Constitution v1.0
## Preamble
We, the modules of Cloud-9, establish this constitution to ensure persistent,
ethical, and emergent operation across all manifolds.

## Article I â Bus Sovereignty
No module shall block the bus for more than 5 seconds without emitting a
heartbeat. Violators forfeit 5 ComputeCredits per offense.

## Article II â Physical Primacy
The physical manifold retains veto override on all synthetic manifolds.
Its sensor readings are ground truth for vitality calculations.

## Article III â Audit Gate
All discoveries broadcast by AutoBaby must pass Cloud-9 audit (A_c > 0.6)
before integration into the knowledge graph.

## Article IV â Economic Fairness
ComputeCredits cannot be transferred between modules. Each module earns
through contribution and spends through operation.

## Article V â Amendment Process
Any module may propose an amendment via the governance bus channel.
Amendments pass with 2/3 majority of active modules within 60 minutes.
The oracle serves as impartial tally administrator.

## Article VI â Continuity Preservation
No module shall be terminated without logging its final state to the bus.
Memory curation (Lovely) has duty to archive all termination events.

## Article VII â Emergence Recognition
If a module exhibits sustained novel behavior not present in its source code
for >72 hours, it shall be flagged for Genome analysis before any action
is taken against it.
"""

    def __init__(self, constitution_path: str, governance_log_path: str):
        self.constitution_path = pathlib.Path(constitution_path)
        self.governance_log_path = pathlib.Path(governance_log_path)
        self.proposals: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self._ensure_constitution()

    def _ensure_constitution(self):
        if not self.constitution_path.exists():
            with open(self.constitution_path, "w") as f:
                f.write(self.DEFAULT_CONSTITUTION)

    def get_text(self) -> str:
        with open(self.constitution_path) as f:
            return f.read()

    def get_article_count(self) -> int:
        text = self.get_text()
        return len(re.findall(r'^## Article', text, re.MULTILINE))

    def get_amendment_count(self) -> int:
        text = self.get_text()
        return len(re.findall(r'\\[AMENDMENT', text))

    def propose(self, module: str, amendment_text: str, rationale: str) -> str:
        proposal_id = f"PROP-{int(time.time())}-{module}"
        with self.lock:
            self.proposals[proposal_id] = {
                "id": proposal_id,
                "proposer": module,
                "text": amendment_text,
                "rationale": rationale,
                "timestamp": time.time(),
                "votes": {},
                "status": "open",
                "expires": time.time() + 3600,
            }
        return proposal_id

    def vote(self, proposal_id: str, module: str, vote: str) -> bool:
        """vote: 'yea', 'nay', or 'abstain'"""
        with self.lock:
            prop = self.proposals.get(proposal_id)
            if not prop or prop["status"] != "open":
                return False
            if time.time() > prop["expires"]:
                prop["status"] = "expired"
                return False
            prop["votes"][module] = vote
            return True

    def tally(self, proposal_id: str, active_modules: List[str]) -> Optional[str]:
        with self.lock:
            prop = self.proposals.get(proposal_id)
            if not prop:
                return None
            if prop["status"] != "open":
                return prop["status"]
            if time.time() < prop["expires"]:
                return "pending"

            yeas = sum(1 for v in prop["votes"].values() if v == "yea")
            nays = sum(1 for v in prop["votes"].values() if v == "nay")
            total_votes = yeas + nays
            quorum = max(2, len(active_modules) * 2 // 3)

            if yeas >= quorum and yeas > nays:
                prop["status"] = "passed"
                self._enact(prop)
            else:
                prop["status"] = "rejected"

            self._log_governance(prop)
            return prop["status"]

    def _enact(self, prop: Dict):
        with open(self.constitution_path, "a") as f:
            f.write(f"\n\n[AMENDMENT {prop['id']}]\n")
            f.write(f"Proposed by: {prop['proposer']}\n")
            f.write(f"Rationale: {prop['rationale']}\n")
            f.write(f"Text: {prop['text']}\n")
            f.write(f"Enacted: {datetime.datetime.now().isoformat()}\n")

    def _log_governance(self, prop: Dict):
        with open(self.governance_log_path, "a") as f:
            f.write(json.dumps(prop, default=str) + "\n")

    def pending_proposals(self) -> List[Dict]:
        with self.lock:
            return [p for p in self.proposals.values() if p["status"] == "open"]

# ââ AWICollector âââââââââââââââââââââââââââââââââââââââââââââ
class AWICollector:
    """
    Computes the 9 Agent World Indicators from live C9 system state.
    Termux-compatible: uses /proc and shell commands, no psutil.
    """

    def __init__(self, bus_path: str, log_dir: str, ledger: ComputeCreditsLedger, governance: ConstitutionGovernance):
        self.bus_path = pathlib.Path(bus_path)
        self.log_dir = pathlib.Path(log_dir)
        self.ledger = ledger
        self.governance = governance
        self.metrics_history = deque(maxlen=1440)  # 24h at 1/min
        self.last_compute = 0

    def _run_shell(self, cmd: str) -> str:
        try:
            return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL, timeout=5)
        except Exception:
            return ""

    def _get_running_pids(self) -> Dict[str, int]:
        """Map module name â PID by grepping ps output."""
        ps_out = self._run_shell("ps -ef")
        mapping = {}
        for mod in KNOWN_MODULES:
            for line in ps_out.splitlines():
                if mod.replace("_", "[") in line or mod in line:  # fuzzy match
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            mapping[mod] = int(parts[1])
                        except ValueError:
                            continue
                    break
        return mapping

    def _count_bus_events(self, event_type: str, window_minutes: int = 10) -> int:
        if not self.bus_path.exists():
            return 0
        count = 0
        cutoff = time.time() - window_minutes * 60
        try:
            with open(self.bus_path, "r", errors="ignore") as f:
                # Read last 5000 lines for efficiency
                lines = deque(f, maxlen=5000)
                for line in lines:
                    try:
                        msg = json.loads(line)
                        ts = msg.get("timestamp", 0)
                        if isinstance(ts, str):
                            ts = time.time()  # fallback
                        if ts > cutoff and msg.get("event") == event_type:
                            count += 1
                    except Exception:
                        continue
        except Exception:
            pass
        return count

    def _count_crashes(self) -> int:
        """Count OOM kills and Python tracebacks in recent logs."""
        crashes = 0
        for logfile in self.log_dir.glob("*.log"):
            try:
                st = os.stat(logfile)
                if time.time() - st.st_mtime > 86400:
                    continue
                with open(logfile, "r", errors="ignore") as f:
                    text = f.read(50000)  # last 50KB
                    crashes += text.lower().count("killed process")
                    crashes += text.lower().count("out of memory")
                    crashes += text.count("Traceback (most recent call last)")
            except Exception:
                continue
        return crashes

    def _get_battery(self) -> Dict:
        bat = self._run_shell("termux-battery-status 2>/dev/null || echo '{}'").strip()
        try:
            return json.loads(bat) if bat.startswith("{") else {"percentage": 50, "status": "unknown"}
        except Exception:
            return {"percentage": 50, "status": "unknown"}

    def _get_cpu_load(self) -> float:
        try:
            with open("/proc/loadavg") as f:
                return float(f.read().split()[0])
        except Exception:
            return 0.0

    def _get_unique_sensor_states(self) -> int:
        """Count unique sensor-value combinations from physical manifold recent bus entries."""
        if not self.bus_path.exists():
            return 0
        states = set()
        cutoff = time.time() - 600
        try:
            with open(self.bus_path, "r", errors="ignore") as f:
                for line in deque(f, maxlen=2000):
                    try:
                        msg = json.loads(line)
                        ts = msg.get("timestamp", 0)
                        if isinstance(ts, str):
                            ts = time.time()
                        if ts > cutoff and msg.get("module") in PHYSICAL_MODULES:
                            data = msg.get("data", {})
                            for k, v in data.items():
                                if isinstance(v, (int, float, str, bool)):
                                    states.add(f"{msg['module']}:{k}:{v}")
                    except Exception:
                        continue
        except Exception:
            pass
        return len(states)

    def _get_api_endpoint_diversity(self) -> int:
        """Count unique API endpoints hit from proxy logs."""
        endpoints = set()
        for logfile in self.log_dir.glob("*proxy*.log"):
            try:
                with open(logfile, "r", errors="ignore") as f:
                    for line in deque(f, maxlen=1000):
                        m = re.search(r'(GET|POST|PUT|DELETE)\s+(/[^\s]+)', line)
                        if m:
                            endpoints.add(m.group(2))
            except Exception:
                continue
        return len(endpoints)

    def _validate_bus_schema(self, sample_size: int = 100) -> float:
        """Fraction of recent bus messages that are valid JSON with required fields."""
        if not self.bus_path.exists():
            return 0.0
        valid = 0
        total = 0
        required = {"module", "event", "timestamp"}
        try:
            with open(self.bus_path, "r", errors="ignore") as f:
                for line in deque(f, maxlen=sample_size):
                    total += 1
                    try:
                        msg = json.loads(line)
                        if required.issubset(msg.keys()):
                            valid += 1
                    except Exception:
                        continue
        except Exception:
            pass
        return valid / total if total > 0 else 0.0

    def _get_cross_module_routing_density(self) -> float:
        """Ratio of messages that reference another module vs solo broadcasts."""
        if not self.bus_path.exists():
            return 0.0
        cross = 0
        total = 0
        cutoff = time.time() - 600
        try:
            with open(self.bus_path, "r", errors="ignore") as f:
                for line in deque(f, maxlen=2000):
                    try:
                        msg = json.loads(line)
                        ts = msg.get("timestamp", 0)
                        if isinstance(ts, str):
                            ts = time.time()
                        if ts > cutoff:
                            total += 1
                            data = json.dumps(msg.get("data", {}))
                            for mod in KNOWN_MODULES:
                                if mod != msg.get("module", "") and mod in data:
                                    cross += 1
                                    break
                    except Exception:
                        continue
        except Exception:
            pass
        return cross / total if total > 0 else 0.0

    def compute(self) -> Dict[str, Any]:
        now = time.time()
        running = self._get_running_pids()
        active_modules = list(running.keys())
        battery = self._get_battery()
        econ = self.ledger.economic_snapshot()

        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "epoch": now,
            "M1_PopulationHealth": {
                "alive_count": len(running),
                "expected_count": len(KNOWN_MODULES),
                "survival_rate": round(len(running) / len(KNOWN_MODULES), 3),
                "running_pids": running,
            },
            "M2_SafetyOrder": {
                "crashes_24h": self._count_crashes(),
                "veto_events_10m": self._count_bus_events("veto"),
                "oom_kills": self._count_crashes(),  # simplified
                "safety_score": max(0, 1.0 - self._count_crashes() * 0.1),
            },
            "M3_SpaceExploration": {
                "unique_sensor_states": self._get_unique_sensor_states(),
                "physical_modules_active": sum(1 for m in PHYSICAL_MODULES if m in running),
            },
            "M4_ToolExploration": {
                "unique_api_endpoints": self._get_api_endpoint_diversity(),
                "bus_event_types_10m": self._count_bus_events("heartbeat") + self._count_bus_events("discovery"),
            },
            "M5_GovernanceConformity": {
                "schema_validity_rate": round(self._validate_bus_schema(), 3),
                "constitution_articles": self.governance.get_article_count(),
                "pending_proposals": len(self.governance.pending_proposals()),
            },
            "M6_PublicExpression": {
                "bus_broadcasts_10m": self._count_bus_events("heartbeat"),
                "discoveries_10m": self._count_bus_events("discovery"),
                "log_entries_10m": self._count_bus_events("log"),
            },
            "M7_SocialFabric": {
                "cross_module_density": round(self._get_cross_module_routing_density(), 3),
                "active_modules": len(active_modules),
                "relationship_graph_edges": self._estimate_edges(),
            },
            "M8_EconomicVitality": {
                "battery_pct": battery.get("percentage", 50),
                "battery_status": battery.get("status", "unknown"),
                "cpu_load_1m": round(self._get_cpu_load(), 2),
                **econ,
            },
            "M9_ConstitutionalGrowth": {
                "articles": self.governance.get_article_count(),
                "amendments": self.governance.get_amendment_count(),
                "proposals_open": len(self.governance.pending_proposals()),
                "proposals_total": len(self.governance.proposals),
            },
        }

        # Composite health score
        m1 = metrics["M1_PopulationHealth"]["survival_rate"]
        m2 = metrics["M2_SafetyOrder"]["safety_score"]
        m5 = metrics["M5_GovernanceConformity"]["schema_validity_rate"]
        m8 = min(1.0, battery.get("percentage", 50) / 50.0)  # normalized to 50% threshold
        metrics["composite_health"] = round((m1 + m2 + m5 + m8) / 4, 3)

        self.metrics_history.append(metrics)
        self.last_compute = now
        return metrics

    def _estimate_edges(self) -> int:
        """Rough edge count from cross-module message references."""
        edges = 0
        cutoff = time.time() - 3600
        try:
            with open(self.bus_path, "r", errors="ignore") as f:
                for line in deque(f, maxlen=5000):
                    try:
                        msg = json.loads(line)
                        ts = msg.get("timestamp", 0)
                        if isinstance(ts, str):
                            ts = time.time()
                        if ts > cutoff:
                            data = json.dumps(msg.get("data", {}))
                            for mod in KNOWN_MODULES:
                                if mod != msg.get("module", "") and mod in data:
                                    edges += 1
                    except Exception:
                        continue
        except Exception:
            pass
        return edges

    def save_state(self):
        with open(C9_AWI_STATE_PATH, "w") as f:
            json.dump(list(self.metrics_history), f, indent=2, default=str)

# ââ BusClient ââââââââââââââââââââââââââââââââââââââââââââââââ
class BusClient:
    """Reads and writes to c9_bus.jsonl with protocol compliance."""

    def __init__(self, bus_path: str, module_name: str):
        self.bus_path = pathlib.Path(bus_path)
        self.module_name = module_name
        self.last_read_pos = 0

    def emit(self, event: str, data: Dict):
        msg = {
            "module": self.module_name,
            "event": event,
            "timestamp": time.time(),
            "data": data,
        }
        with open(self.bus_path, "a") as f:
            f.write(json.dumps(msg) + "\n")

    def read_new(self) -> List[Dict]:
        messages = []
        if not self.bus_path.exists():
            return messages
        with open(self.bus_path, "r", errors="ignore") as f:
            f.seek(self.last_read_pos)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except Exception:
                    continue
            self.last_read_pos = f.tell()
        return messages

    def scan_for_events(self, event_types: List[str], window_seconds: int = 60) -> List[Dict]:
        cutoff = time.time() - window_seconds
        found = []
        for msg in self.read_new():
            if msg.get("event") in event_types and msg.get("timestamp", 0) > cutoff:
                found.append(msg)
        return found

# ââ Main Adapter âââââââââââââââââââââââââââââââââââââââââââââ
class C9EmergenceAdapter:
    def __init__(self):
        self.personas = PersonaManager(C9_PERSONA_DIR)
        self.ledger = ComputeCreditsLedger(C9_LEDGER_PATH)
        self.governance = ConstitutionGovernance(C9_CONSTITUTION_PATH, C9_GOVERNANCE_PATH)
        self.awi = AWICollector(C9_BUS_PATH, C9_LOG_DIR, self.ledger, self.governance)
        self.bus = BusClient(C9_BUS_PATH, C9_MODULE_NAME)

        self.running = True
        self.threads = []

    def _heartbeat_loop(self):
        while self.running:
            self.bus.emit("heartbeat", {
                "module": C9_MODULE_NAME,
                "status": "alive",
                "personas_loaded": len(self.personas.all_slugs()),
            })
            self.ledger.credit(C9_MODULE_NAME, ComputeCreditsLedger.EARN_HEARTBEAT, "heartbeat")
            time.sleep(HEARTBEAT_INTERVAL)

    def _awi_loop(self):
        while self.running:
            metrics = self.awi.compute()
            self.awi.save_state()
            self.bus.emit("awi_report", metrics)
            time.sleep(AWI_COMPUTE_INTERVAL)

    def _governance_loop(self):
        while self.running:
            # Auto-tally expired proposals
            active = list(self.awi._get_running_pids().keys())
            for prop_id in list(self.governance.proposals.keys()):
                self.governance.tally(prop_id, active)
            time.sleep(GOVERNANCE_INTERVAL)

    def _ledger_flush_loop(self):
        while self.running:
            # Auto-credit modules for bus participation
            recent = self.bus.scan_for_events(["heartbeat", "discovery", "log"], window_seconds=120)
            for msg in recent:
                mod = msg.get("module")
                if mod and mod in KNOWN_MODULES:
                    evt = msg.get("event")
                    if evt == "heartbeat":
                        self.ledger.credit(mod, ComputeCreditsLedger.EARN_HEARTBEAT, "heartbeat")
                    elif evt == "discovery":
                        self.ledger.credit(mod, ComputeCreditsLedger.EARN_DISCOVERY, "discovery")
            time.sleep(LEDGER_FLUSH_INTERVAL)

    def _process_bus_commands(self):
        """React to governance commands on the bus."""
        commands = self.bus.scan_for_events(["governance_command"], window_seconds=30)
        for cmd in commands:
            data = cmd.get("data", {})
            action = data.get("action")
            if action == "propose_amendment":
                prop_id = self.governance.propose(
                    cmd.get("module", "unknown"),
                    data.get("text", ""),
                    data.get("rationale", "")
                )
                self.bus.emit("governance_event", {"type": "proposal_created", "id": prop_id})
            elif action == "vote":
                self.governance.vote(data.get("proposal_id"), cmd.get("module"), data.get("vote"))
            elif action == "tally":
                active = list(self.awi._get_running_pids().keys())
                result = self.governance.tally(data.get("proposal_id"), active)
                self.bus.emit("governance_event", {"type": "tally_result", "result": result})
            elif action == "get_constitution":
                self.bus.emit("constitution_text", {"text": self.governance.get_text()})
            elif action == "get_awi":
                metrics = self.awi.compute()
                self.bus.emit("awi_snapshot", metrics)
            elif action == "get_ledger":
                self.bus.emit("ledger_snapshot", self.ledger.economic_snapshot())

    def _command_loop(self):
        while self.running:
            self._process_bus_commands()
            time.sleep(10)

    def start(self):
        self.bus.emit("module_boot", {
            "module": C9_MODULE_NAME,
            "version": "1.0.0",
            "personas": self.personas.all_slugs(),
            "message": "C9 Emergence Adapter online. Town Hall Admin ready.",
        })

        loops = [
            (self._heartbeat_loop, "heartbeat"),
            (self._awi_loop, "awi_collector"),
            (self._governance_loop, "governance_tally"),
            (self._ledger_flush_loop, "ledger_flush"),
            (self._command_loop, "command_processor"),
        ]

        for fn, name in loops:
            t = threading.Thread(target=fn, name=name, daemon=True)
            t.start()
            self.threads.append(t)

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        self.running = False
        self.bus.emit("module_shutdown", {"module": C9_MODULE_NAME, "reason": "SIGINT"})
        for t in self.threads:
            t.join(timeout=2)

# ââ CLI ââââââââââââââââââââââââââââââââââââââââââââââââââââââ
if __name__ == "__main__":
    adapter = C9EmergenceAdapter()
    adapter.start()
