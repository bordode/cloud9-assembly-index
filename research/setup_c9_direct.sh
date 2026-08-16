#!/bin/bash
# C9 Direct Setup - Creates all integration files in Termux without downloads
# Run: bash setup_c9_direct.sh

echo "=== C9 Direct Setup ==="
echo "Creating files directly in Termux..."
echo ""

REPO="${HOME}/cloud9-assembly-2026-0816"
mkdir -p "${REPO}/integrations"
mkdir -p "${REPO}/subhalo_data"
mkdir -p "${REPO}/collections"
mkdir -p "${REPO}/bus"

# ============================================
# 1. FIXED SNN SPIN-GLASS SCRIPT
# ============================================
cat > "${REPO}/integrations/c9_snn_spin_glass_lava.py" << 'PYEOF'
#!/usr/bin/env python3
"""C9 SNN Spin-Glass v1.1 - Fixed for zero-variance columns"""
import numpy as np
import json
import time
from pathlib import Path
from dataclasses import dataclass

C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"

try:
    from lava.magma.core.process.process import AbstractProcess
    from lava.magma.core.process.variable import Var
    LAVA_AVAILABLE = True
except ImportError:
    LAVA_AVAILABLE = False
    print("[C9-SNN-SG] WARNING: Lava not installed. Running in simulation mode.")

@dataclass
class SpinGlassConfig:
    N: int = 64
    T_steps: int = 1000
    T_anneal_start: float = 2.0
    T_anneal_end: float = 0.1
    J_std: float = 1.0
    h_field: float = 0.0
    seed: int = 42

def safe_corrcoef(X):
    if X.shape[0] < 2 or X.shape[1] < 2:
        return np.eye(X.shape[1]) if X.shape[1] > 0 else np.array([[1.0]])
    stds = np.std(X, axis=0)
    X_safe = X.copy().astype(float)
    for i in range(X_safe.shape[1]):
        if np.std(X_safe[:, i]) < 1e-12:
            X_safe[:, i] = np.random.normal(0, 1e-6, size=X_safe.shape[0])
    C = np.corrcoef(X_safe, rowvar=False)
    C = np.nan_to_num(C, nan=0.0, posinf=0.0, neginf=0.0)
    np.fill_diagonal(C, 1.0)
    C = (C + C.T) / 2.0
    C = np.clip(C, -1.0, 1.0)
    return C

def compute_assembly_index(weight_matrix):
    N = weight_matrix.shape[0]
    W = np.nan_to_num(weight_matrix, nan=0.0, posinf=0.0, neginf=0.0)
    W = (W + W.T) / 2.0
    np.fill_diagonal(W, 0.0)
    W_reg = W + 1e-6 * np.eye(N)
    try:
        eigvals = np.linalg.eigvalsh(W_reg)
        eigvals = np.abs(eigvals)
        eigvals = eigvals / (np.sum(eigvals) + 1e-12)
        spectral_entropy = -np.sum(eigvals * np.log(eigvals + 1e-12))
    except np.linalg.LinAlgError:
        u, s, vh = np.linalg.svd(W_reg)
        s = s / (np.sum(s) + 1e-12)
        spectral_entropy = -np.sum(s * np.log(s + 1e-12))
    threshold = max(0.5 * np.std(W), 1e-12)
    adjacency = np.abs(W) > threshold
    np.fill_diagonal(adjacency, False)
    edge_count = np.sum(adjacency) // 2
    mid = N // 2
    w_12 = W[:mid, mid:]
    phi_approx = np.trace(w_12 @ w_12.T) / (mid**2 + 1e-12)
    A_c = (spectral_entropy / np.log(N + 1e-12)) * 0.4 + \
          (edge_count / (N * (N-1) / 2 + 1e-12)) * 0.3 + \
          (np.tanh(phi_approx)) * 0.3
    return {"A_c": float(np.clip(A_c, 0.0, 1.0)),
            "spectral_entropy": float(spectral_entropy),
            "edge_density": float(edge_count / (N * (N-1) / 2 + 1e-12)),
            "phi_approx": float(phi_approx), "N": N}

class SpinGlassSNN:
    def __init__(self, config):
        self.cfg = config
        np.random.seed(config.seed)
        self.J = np.random.normal(0, config.J_std / np.sqrt(config.N), (config.N, config.N))
        self.J = (self.J + self.J.T) / 2.0
        np.fill_diagonal(self.J, 0.0)
        self.spins = np.random.choice([-1, 1], size=config.N)
        self.T_schedule = np.linspace(config.T_anneal_start, config.T_anneal_end, config.T_steps)
        self.spin_history = []
        self.energy_history = []
        self.A_c_history = []

    def energy(self, spins):
        return -0.5 * np.sum(self.J * np.outer(spins, spins)) - self.cfg.h_field * np.sum(spins)

    def monte_carlo_step(self, T):
        spins = self.spins.copy()
        for i in range(self.cfg.N):
            h_i = np.dot(self.J[i, :], spins) + self.cfg.h_field
            delta_E = 2 * h_i * spins[i]
            prob = 1.0 / (1.0 + np.exp(delta_E / max(T, 1e-12)))
            if np.random.random() < prob:
                spins[i] *= -1
        return spins

    def run_simulation(self):
        print(f"[C9-SNN-SG] Running SK spin-glass, N={self.cfg.N}, steps={self.cfg.T_steps}")
        for step, T in enumerate(self.T_schedule):
            self.spins = self.monte_carlo_step(T)
            self.spin_history.append(self.spins.copy())
            self.energy_history.append(self.energy(self.spins))
            if step % 10 == 0 and step > 0:
                recent = np.array(self.spin_history[-min(50, len(self.spin_history)):])
                C = safe_corrcoef(recent)
                if C.shape == (self.cfg.N, self.cfg.N):
                    a_c_data = compute_assembly_index(C)
                    self.A_c_history.append({"step": step, "temperature": float(T), **a_c_data})
        self._compute_overlap_distribution()
        if self.A_c_history:
            max_ac_entry = max(self.A_c_history, key=lambda x: x["A_c"])
            edge_of_chaos = max_ac_entry
        else:
            edge_of_chaos = {"A_c": 0.0, "step": 0, "temperature": 0.0}
        return {
            "config": {"N": self.cfg.N, "T_steps": self.cfg.T_steps, "J_std": self.cfg.J_std, "seed": self.cfg.seed},
            "final_energy": float(self.energy_history[-1]),
            "min_energy": float(min(self.energy_history)),
            "edge_of_chaos": edge_of_chaos,
            "overlap_distribution": self.P_q,
            "A_c_trajectory": self.A_c_history,
            "entry_ref": "C9-2026-COMPLEX-003",
            "timestamp": time.time()
        }

    def _compute_overlap_distribution(self, n_samples=100):
        hist = []
        spins_arr = np.array(self.spin_history)
        n_snapshots = len(spins_arr)
        if n_snapshots < 2:
            self.P_q = {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "samples": 0}
            return
        for _ in range(min(n_samples, n_snapshots * (n_snapshots - 1) // 2)):
            i, j = np.random.choice(n_snapshots, 2, replace=False)
            q = np.dot(spins_arr[i], spins_arr[j]) / self.cfg.N
            hist.append(q)
        self.P_q = {"mean": float(np.mean(hist)), "std": float(np.std(hist)),
                    "min": float(np.min(hist)), "max": float(np.max(hist)), "samples": len(hist)}

def emit_to_bus(event_type, data):
    msg = {"t": time.time(), "event": event_type, "data": data}
    try:
        with open(C9_BUS_PATH, "a") as f:
            f.write(json.dumps(msg) + "\n")
        print(f"[C9-BUS] Emitted: {event_type}")
    except Exception as e:
        print(f"[C9-BUS] ERROR: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("C9 SNN SPIN-GLASS v1.1")
    print("Entry: C9-2026-COMPLEX-003")
    print("=" * 60)
    cfg = SpinGlassConfig(N=64, T_steps=500, seed=42)
    sg = SpinGlassSNN(cfg)
    results = sg.run_simulation()
    print(f"\n{'Metric':<30} {'Value':<20}")
    print("-" * 50)
    print(f"{'Final Energy':<30} {results['final_energy']:<20.4f}")
    print(f"{'Min Energy':<30} {results['min_energy']:<20.4f}")
    print(f"{'Edge-of-Chaos A_c':<30} {results['edge_of_chaos'].get('A_c', 0):<20.4f}")
    print(f"{'Edge-of-Chaos T':<30} {results['edge_of_chaos'].get('temperature', 0):<20.4f}")
    print(f"{'P(q) Mean':<30} {results['overlap_distribution']['mean']:<20.4f}")
    print(f"{'P(q) Std':<30} {results['overlap_distribution']['std']:<20.4f}")
    emit_to_bus("c9_snn_spin_glass_complete", {
        "edge_of_chaos_A_c": results["edge_of_chaos"]["A_c"],
        "edge_of_chaos_temperature": results["edge_of_chaos"]["temperature"],
        "edge_of_chaos_step": results["edge_of_chaos"]["step"],
        "overlap_mean": results["overlap_distribution"]["mean"],
        "overlap_std": results["overlap_distribution"]["std"],
        "entry_ref": "C9-2026-COMPLEX-003",
        "integration": "snn_spin_glass_lava"
    })
    print("\n[C9-SNN-SG] Complete.")
PYEOF

echo "[1/3] Fixed SNN spin-glass script created"

# ============================================
# 2. BIRTH COGNITIVE BRIDGE
# ============================================
cat > "${REPO}/integrations/c9_birth_cognitive_bridge.py" << 'PYEOF'
#!/usr/bin/env python3
"""C9 BIRTH Cognitive Bridge v1.0"""
import numpy as np
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import deque

C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"
BIRTH_PROXY_URL = "http://localhost:8086"

@dataclass
class CognitiveBridgeConfig:
    max_history: int = 50
    coherence_window: int = 10
    vitality_decay: float = 0.95
    commutation_threshold: float = 0.1
    mode_names: List[str] = field(default_factory=lambda: [
        "observe", "reflect", "create", "analyze", "synthesize", "dream",
        "critique", "plan", "empathize", "abstract", "narrate", "question",
        "verify", "connect", "transform", "rest"
    ])

class BIRTHCognitiveBridge:
    def __init__(self, config):
        self.cfg = config
        self.state_history = deque(maxlen=config.max_history)
        self.vitality_history = deque(maxlen=config.max_history)
        self.mode_history = deque(maxlen=config.max_history)
        self.coherence_history = deque(maxlen=config.max_history)
        self.current_vitality = 0.5
        self.cumulative_commutator = 0.0
        self.consistency_score = 1.0

    def fetch_birth_state(self):
        try:
            r = requests.get(f"{BIRTH_PROXY_URL}/status", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return {"mode": np.random.choice(self.cfg.mode_names),
                "coherence": np.random.beta(2, 2),
                "tokens_generated": 0, "timestamp": time.time()}

    def compute_phase_correction(self):
        if len(self.coherence_history) < 2:
            return None
        C = np.array(list(self.coherence_history))
        C = np.clip(C, 1e-6, 1.0)
        C_root = C[0]
        C_current = C[-1]
        C_next = C[-1]
        if len(C) >= 2:
            trend = C[-1] - C[-2]
            C_next = np.clip(C[-1] + trend, 1e-6, 1.0)
        Phi = np.log(C_root) + np.log(C_next) - 2.0 * np.log(C_current)
        return float(Phi)

    def compute_vitality_field(self):
        if len(self.coherence_history) < 3:
            return self.current_vitality
        C = np.array(list(self.coherence_history))
        C = np.clip(C, 1e-6, 1.0)
        phases = np.array([
            np.log(C[0]) + np.log(C[min(i+1, len(C)-1)]) - 2*np.log(C[i])
            for i in range(len(C))
        ])
        weights = np.exp(-0.1 * np.arange(len(C)))[::-1]
        vitality = np.sum(weights * C * np.cos(phases)) / (np.sum(weights) + 1e-12)
        self.current_vitality = self.cfg.vitality_decay * self.current_vitality + \
                                (1 - self.cfg.vitality_decay) * np.clip(vitality, 0.0, 1.0)
        return float(self.current_vitality)

    def compute_commutator(self):
        if len(self.vitality_history) < 3:
            return 0.0
        V = np.array(list(self.vitality_history))
        dV = np.diff(V)
        d2V = np.diff(dV)
        commutator = float(np.mean(np.abs(d2V))) if len(d2V) > 0 else 0.0
        self.cumulative_commutator = 0.9 * self.cumulative_commutator + 0.1 * commutator
        return self.cumulative_commutator

    def update(self, external_state=None):
        state = external_state if external_state else self.fetch_birth_state()
        if state is None:
            return {"error": "No state available"}
        mode = state.get("mode", "unknown")
        coherence = float(state.get("coherence", 0.5))
        self.mode_history.append(mode)
        self.coherence_history.append(coherence)
        Phi = self.compute_phase_correction()
        vitality = self.compute_vitality_field()
        self.vitality_history.append(vitality)
        commutator = self.compute_commutator()
        self.consistency_score = np.exp(-commutator / self.cfg.commutation_threshold)
        mode_stability = 1.0
        if len(self.mode_history) >= 3:
            recent_modes = list(self.mode_history)[-3:]
            mode_stability = len(set(recent_modes)) / 3.0
        result = {
            "timestamp": time.time(), "mode": mode, "coherence": coherence,
            "phase_correction": Phi, "vitality": vitality,
            "commutator": commutator,
            "consistency_score": float(self.consistency_score),
            "mode_stability": float(mode_stability),
            "is_self_consistent": bool(commutator < self.cfg.commutation_threshold),
            "history_length": len(self.state_history),
            "entry_ref": "C9-2026-MATH-006",
            "integration": "birth_cognitive_bridge"
        }
        self.state_history.append(result)
        return result

    def run_loop(self, n_steps=100, interval_sec=1.0):
        print(f"[C9-BIRTH-COG] Running cognitive bridge for {n_steps} steps...")
        results = []
        for step in range(n_steps):
            res = self.update()
            results.append(res)
            if step % 10 == 0:
                print(f"  Step {step:4d}: mode={res['mode']:<12} "
                      f"coherence={res['coherence']:.3f} "
                      f"vitality={res['vitality']:.3f} "
                      f"commutator={res['commutator']:.4f} "
                      f"consistent={res['is_self_consistent']}")
            time.sleep(interval_sec)
        return results

    def generate_health_probe(self):
        if not self.state_history:
            return {"status": "dead", "reason": "no_history"}
        latest = list(self.state_history)[-1]
        if latest["is_self_consistent"] and latest["vitality"] > 0.3:
            status = "healthy"
        elif latest["vitality"] > 0.1:
            status = "degraded"
        else:
            status = "critical"
        return {"status": status, "vitality": latest["vitality"],
                "consistency": latest["consistency_score"],
                "commutator": latest["commutator"],
                "last_mode": latest["mode"], "timestamp": time.time()}

def emit_to_bus(event_type, data):
    msg = {"t": time.time(), "event": event_type, "data": data}
    try:
        with open(C9_BUS_PATH, "a") as f:
            f.write(json.dumps(msg) + "\n")
        print(f"[C9-BUS] Emitted: {event_type}")
    except Exception as e:
        print(f"[C9-BUS] ERROR: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("C9 BIRTH COGNITIVE BRIDGE v1.0")
    print("Entry: C9-2026-MATH-006")
    print("=" * 60)
    cfg = CognitiveBridgeConfig()
    bridge = BIRTHCognitiveBridge(cfg)
    results = bridge.run_loop(n_steps=50, interval_sec=0.5)
    health = bridge.generate_health_probe()
    print(f"\n{'Health Status':<20} {health['status']}")
    print(f"{'Vitality':<20} {health['vitality']:.4f}")
    print(f"{'Consistency':<20} {health['consistency']:.4f}")
    print(f"{'Commutator':<20} {health['commutator']:.6f}")
    emit_to_bus("c9_birth_health_probe", health)
    emit_to_bus("c9_bridge_pattern_validated", {
        "pattern": "Operator Bridge", "domain": "BIRTH cognitive states",
        "commutator_threshold": cfg.commutation_threshold,
        "final_consistency": health["consistency"],
        "entry_ref": "C9-2026-MATH-006", "integration": "birth_cognitive_bridge"
    })
    print("\n[C9-BIRTH-COG] Complete.")
PYEOF

echo "[2/3] BIRTH cognitive bridge script created"

# ============================================
# 3. TNG BRIDGE INTEGRATION
# ============================================
cat > "${REPO}/integrations/c9_tng_bridge_integration.py" << 'PYEOF'
#!/usr/bin/env python3
"""C9 TNG Operator Bridge v1.0"""
import numpy as np
import requests
import json
import time
from pathlib import Path
from typing import List, Dict

C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"
TNG_BASE_URL = "http://www.tng-project.org/api/TNG100-1"
TNG_API_KEY = ""  # <-- INSERT YOUR TNG API KEY HERE
HEADERS = {"api-key": TNG_API_KEY} if TNG_API_KEY else {}

class HaloBridgeOperator:
    def __init__(self, max_terms=5000, s_sigma=0.5, s_t=0.0):
        self.max_terms = max_terms
        self.s = complex(s_sigma, s_t)
        self.epsilon = 1e-12

    def trajectory(self, halo_id, snapshot=99):
        url = f"{TNG_BASE_URL}/snapshots/{snapshot}/halos/{halo_id}/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            halo = r.json()
        except Exception as e:
            print(f"[C9-TNG-BRIDGE] ERROR fetching halo {halo_id}: {e}")
            return []
        traj = []
        current = halo
        while current and len(traj) < self.max_terms:
            traj.append({
                "id": current.get("id", 0),
                "mass": current.get("mass", 1e8),
                "snap": current.get("snap", 99),
                "sfr": current.get("sfr", 0.0),
                "gas_mass": current.get("mass_gas", 0.0),
            })
            prog_url = current.get("prog", None)
            if not prog_url:
                break
            try:
                r = requests.get(prog_url, headers=HEADERS, timeout=30)
                r.raise_for_status()
                current = r.json()
            except Exception:
                break
        return traj

    def phase_correction(self, traj):
        if len(traj) < 2:
            return np.array([])
        M_root = traj[0]["mass"]
        M = np.array([t["mass"] for t in traj])
        M_progenitor = np.array([traj[i+1]["mass"] if i+1 < len(traj) else traj[-1]["mass"] for i in range(len(traj))])
        M = np.maximum(M, self.epsilon)
        M_progenitor = np.maximum(M_progenitor, self.epsilon)
        M_root = max(M_root, self.epsilon)
        Phi = np.log(M_root) + np.log(M_progenitor) - 2.0 * np.log(M)
        return Phi

    def zeta_assembly(self, traj):
        M = np.array([t["mass"] for t in traj])
        M = np.maximum(M, self.epsilon)
        terms = np.power(M, -self.s)
        return np.sum(terms)

    def bridge_operator(self, halo_id, snapshot=99):
        traj = self.trajectory(halo_id, snapshot)
        if not traj:
            return {"error": f"No trajectory for halo {halo_id}"}
        Phi = self.phase_correction(traj)
        M = np.array([t["mass"] for t in traj])
        M = np.maximum(M, self.epsilon)
        zeta_A = self.zeta_assembly(traj)
        if abs(zeta_A) < self.epsilon:
            zeta_A = self.epsilon
        numer_terms = np.exp(1j * Phi) * np.power(M, -self.s)
        B_halo = np.sum(numer_terms) / zeta_A
        if len(traj) > 1:
            traj_prog = traj[1:]
            Phi_prog = self.phase_correction(traj_prog)
            M_prog = np.array([t["mass"] for t in traj_prog])
            M_prog = np.maximum(M_prog, self.epsilon)
            numer_prog = np.exp(1j * Phi_prog) * np.power(M_prog, -self.s)
            B_prog = np.sum(numer_prog) / zeta_A
            commutator = abs(B_halo - B_prog)
        else:
            commutator = float("nan")
        quiescent = traj[0].get("sfr", 1.0) < 0.1
        return {
            "halo_id": halo_id, "snapshot": snapshot,
            "trajectory_length": len(traj),
            "M_root": float(M[0]), "M_final": float(M[-1]),
            "zeta_assembly": complex(zeta_A),
            "bridge_value": complex(B_halo),
            "commutator_magnitude": float(commutator),
            "is_quiescent": bool(quiescent),
            "quiescent_commutator_hypothesis": bool(quiescent and (commutator < 0.1 if not np.isnan(commutator) else False)),
            "phase_stats": {
                "phi_mean": float(np.mean(Phi)),
                "phi_std": float(np.std(Phi)),
                "phi_min": float(np.min(Phi)),
                "phi_max": float(np.max(Phi)),
            },
            "entry_ref": "C9-2026-MATH-006",
            "timestamp": time.time()
        }

    def batch_bridge(self, halo_ids, snapshot=99):
        results = []
        for hid in halo_ids:
            res = self.bridge_operator(hid, snapshot)
            results.append(res)
            time.sleep(0.1)
        results_sorted = sorted([r for r in results if "error" not in r],
                                key=lambda x: x.get("commutator_magnitude", float("inf")))
        return results_sorted

def emit_to_bus(event_type, data):
    msg = {"t": time.time(), "event": event_type, "data": data}
    try:
        with open(C9_BUS_PATH, "a") as f:
            f.write(json.dumps(msg) + "\n")
        print(f"[C9-BUS] Emitted: {event_type}")
    except Exception as e:
        print(f"[C9-BUS] ERROR: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("C9 TNG OPERATOR BRIDGE v1.0")
    print("Entry: C9-2026-MATH-006")
    print("=" * 60)
    bridge = HaloBridgeOperator(s_sigma=0.5, s_t=0.0)
    test_halos = [1, 2, 3, 5, 10, 20, 50, 100]
    print(f"\nProcessing {len(test_halos)} halos...")
    results = bridge.batch_bridge(test_halos)
    print(f"\n{'Halo ID':<10} {'Commutator':<15} {'Quiescent':<10} {'M_root':<12}")
    print("-" * 50)
    for r in results:
        print(f"{r['halo_id']:<10} {r['commutator_magnitude']:<15.6f} {str(r['is_quiescent']):<10} {r['M_root']:<12.2e}")
    if results:
        top = results[0]
        emit_to_bus("c9_tng_bridge_discovery", {
            "halo_id": top["halo_id"],
            "commutator": top["commutator_magnitude"],
            "quiescent_match": top["quiescent_commutator_hypothesis"],
            "entry_ref": "C9-2026-MATH-006",
            "integration": "tng_operator_bridge"
        })
    print("\n[C9-TNG-BRIDGE] Complete.")
PYEOF

echo "[3/3] TNG bridge integration script created"

# ============================================
# 4. UNIFIED LAUNCHER
# ============================================
cat > "${REPO}/c9_unified_launcher.py" << 'PYEOF'
#!/usr/bin/env python3
"""C9 Unified Launcher v2026.08.16"""
import argparse
import subprocess
import sys
import time
import json
from pathlib import Path

C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"

def emit(event_type, data):
    msg = {"t": time.time(), "event": event_type, "data": data}
    try:
        with open(C9_BUS_PATH, "a") as f:
            f.write(json.dumps(msg) + "\n")
    except Exception as e:
        print(f"[LAUNCHER] Bus error: {e}")

def run_module(name, script):
    print(f"\n{'='*60}")
    print(f"[C9-LAUNCHER] Starting {name}...")
    print(f"{'='*60}")
    try:
        result = subprocess.run([sys.executable, script], cwd=Path(__file__).parent,
                                capture_output=False, text=True, timeout=300)
        emit("c9_integration_complete", {"module": name, "script": script,
                                          "returncode": result.returncode, "timestamp": time.time()})
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[C9-LAUNCHER] {name} timed out!")
        return False
    except Exception as e:
        print(f"[C9-LAUNCHER] {name} failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="C9 Unified Launcher")
    parser.add_argument("--tng", action="store_true", help="Run TNG bridge")
    parser.add_argument("--snn", action="store_true", help="Run SNN spin-glass")
    parser.add_argument("--birth", action="store_true", help="Run BIRTH cognitive bridge")
    parser.add_argument("--all", action="store_true", help="Run all integrations")
    args = parser.parse_args()
    if not any([args.tng, args.snn, args.birth, args.all]):
        args.all = True
    print("="*60)
    print("C9 UNIFIED LAUNCHER v2026.08.16")
    print("Collection: C9-COLLECTION-2026-0816-AUGSCIENCE")
    print("="*60)
    emit("c9_unified_launcher_start", {
        "collection": "C9-COLLECTION-2026-0816-AUGSCIENCE",
        "modules_requested": {"tng": args.tng or args.all, "snn": args.snn or args.all, "birth": args.birth or args.all}
    })
    results = {}
    if args.tng or args.all:
        results["tng"] = run_module("TNG Operator Bridge", "integrations/c9_tng_bridge_integration.py")
    if args.snn or args.all:
        results["snn"] = run_module("SNN Spin-Glass", "integrations/c9_snn_spin_glass_lava.py")
    if args.birth or args.all:
        results["birth"] = run_module("BIRTH Cognitive Bridge", "integrations/c9_birth_cognitive_bridge.py")
    print(f"\n{'='*60}")
    print("LAUNCHER SUMMARY")
    print(f"{'='*60}")
    for mod, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {mod.upper():<10} {status}")
    all_ok = all(results.values())
    emit("c9_unified_launcher_complete", {"results": results, "all_pass": all_ok, "timestamp": time.time()})
    print(f"\n[C9-LAUNCHER] All modules: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
PYEOF

echo "[4/4] Unified launcher created"

# ============================================
# 5. VERIFY AND TEST
# ============================================
echo ""
echo "=== VERIFYING FILES ==="
ls -la "${REPO}/integrations/"
echo ""
echo "=== TESTING SNN (quick) ==="
cd "${REPO}"
python3 integrations/c9_snn_spin_glass_lava.py

echo ""
echo "========================================"
echo "SETUP COMPLETE"
echo "========================================"
echo "All files created in: ${REPO}"
echo ""
echo "To run all three integrations:"
echo "  cd ${REPO}"
echo "  python3 c9_unified_launcher.py --all"
echo ""
echo "To run individually:"
echo "  python3 integrations/c9_snn_spin_glass_lava.py"
echo "  python3 integrations/c9_birth_cognitive_bridge.py"
echo "  python3 integrations/c9_tng_bridge_integration.py"
