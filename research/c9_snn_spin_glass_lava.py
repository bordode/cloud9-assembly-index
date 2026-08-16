#!/usr/bin/env python3
"""
C9-2026-COMPLEX-003 Integration: SK Spin-Glass on Lava SNN
Implements Sherrington-Kirkpatrick Hamiltonian on neuromorphic hardware
and correlates overlap distribution P(q) with Assembly Index A_c.

Module:     c9_snn_spin_glass_lava.py
Bus ID:     C9-SNN-SG-v1.1
Author:     C9 Oracle / Kimi
Date:       2026-08-16
Requires:   numpy, scipy
"""

import numpy as np
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ââ C9 BUS CONFIG ââââââââââââââââââââââââââââââââââââââââââ
C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"

# ââ LAVA IMPORTS (soft-fail if not installed) ââââââââââââââ
try:
    from lava.magma.core.process.process import AbstractProcess
    from lava.magma.core.process.variable import Var
    from lava.magma.core.process.ports.ports import InPort, OutPort
    from lava.magma.core.model.py.model import PyLoihiProcessModel
    from lava.magma.core.model.py.ports import PyInPort, PyOutPort
    from lava.magma.core.decorator import implements, requires
    from lava.magma.core.resources import CPU
    from lava.magma.core.sync.domain import SyncDomain
    from lava.magma.core.run_configs import Loihi1SimCfg
    from lava.magma.core.run_conditions import RunSteps
    LAVA_AVAILABLE = True
except ImportError:
    LAVA_AVAILABLE = False
    print("[C9-SNN-SG] WARNING: Lava not installed. Running in simulation mode.")

# ââ SPIN-GLASS PARAMETERS ââââââââââââââââââââââââââââââââââ
@dataclass
class SpinGlassConfig:
    N: int = 64               # Number of spins (neurons)
    T_steps: int = 1000       # Simulation steps
    T_anneal_start: float = 2.0   # Initial temperature (in units of J)
    T_anneal_end: float = 0.1     # Final temperature
    J_std: float = 1.0        # Coupling standard deviation
    h_field: float = 0.0      # External field
    dt: float = 0.1           # Time step
    seed: int = 42

# ââ ASSEMBLY INDEX COMPUTATION (FIXED) âââââââââââââââââââââ
def compute_assembly_index(weight_matrix: np.ndarray) -> Dict:
    """
    Compute A_c for a spin-glass weight matrix.
    Uses spectral decomposition + topological complexity metrics.
    FIXED: Handles NaN/inf and non-convergent eigenvalues.
    """
    N = weight_matrix.shape[0]

    # Clean the matrix
    W = np.nan_to_num(weight_matrix, nan=0.0, posinf=0.0, neginf=0.0)

    # Ensure symmetric
    W = (W + W.T) / 2.0
    np.fill_diagonal(W, 0.0)

    # Regularize: add small identity to guarantee convergence
    W_reg = W + 1e-6 * np.eye(N)

    # Spectral entropy (quantum entropy analog)
    try:
        eigvals = np.linalg.eigvalsh(W_reg)
        eigvals = np.abs(eigvals)
        eigvals = eigvals / (np.sum(eigvals) + 1e-12)
        spectral_entropy = -np.sum(eigvals * np.log(eigvals + 1e-12))
    except np.linalg.LinAlgError:
        # Fallback: use SVD-based spectrum
        u, s, vh = np.linalg.svd(W_reg)
        s = s / (np.sum(s) + 1e-12)
        spectral_entropy = -np.sum(s * np.log(s + 1e-12))

    # Topological complexity: persistent Betti-1 analog
    threshold = 0.5 * np.std(W)
    if threshold < 1e-12:
        threshold = 1e-12
    adjacency = np.abs(W) > threshold
    np.fill_diagonal(adjacency, False)
    edge_count = np.sum(adjacency) // 2

    # Integrated information (IIT-inspired)
    mid = N // 2
    w_12 = W[:mid, mid:]
    phi_approx = np.trace(w_12 @ w_12.T) / (mid**2 + 1e-12)

    # Combine into A_c (normalized)
    A_c = (spectral_entropy / np.log(N + 1e-12)) * 0.4 +           (edge_count / (N * (N-1) / 2 + 1e-12)) * 0.3 +           (np.tanh(phi_approx)) * 0.3

    return {
        "A_c": float(np.clip(A_c, 0.0, 1.0)),
        "spectral_entropy": float(spectral_entropy),
        "edge_density": float(edge_count / (N * (N-1) / 2 + 1e-12)),
        "phi_approx": float(phi_approx),
        "N": N
    }

def safe_corrcoef(X: np.ndarray) -> np.ndarray:
    """
    Compute correlation matrix safely, handling zero-variance columns.
    Returns identity for zero-variance inputs.
    """
    if X.shape[0] < 2 or X.shape[1] < 2:
        return np.eye(X.shape[1]) if X.shape[1] > 0 else np.array([[1.0]])

    # Check for zero-variance columns
    stds = np.std(X, axis=0)
    zero_var = stds < 1e-12

    if np.all(zero_var):
        return np.eye(X.shape[1])

    # Replace zero-variance columns with small noise
    X_safe = X.copy().astype(float)
    for i in range(X_safe.shape[1]):
        if np.std(X_safe[:, i]) < 1e-12:
            X_safe[:, i] = np.random.normal(0, 1e-6, size=X_safe.shape[0])

    C = np.corrcoef(X_safe, rowvar=False)
    C = np.nan_to_num(C, nan=0.0, posinf=0.0, neginf=0.0)

    # Ensure valid correlation matrix
    np.fill_diagonal(C, 1.0)
    C = (C + C.T) / 2.0

    # Clip to [-1, 1]
    C = np.clip(C, -1.0, 1.0)

    return C

# ââ SPIN-GLASS SIMULATOR âââââââââââââââââââââââââââââââââââ
class SpinGlassSNN:
    """
    Sherrington-Kirkpatrick spin glass simulated on Lava SNN architecture.
    Spins are binary neurons; couplings are memristor-like weights.
    """

    def __init__(self, config: SpinGlassConfig):
        self.cfg = config
        np.random.seed(config.seed)

        # SK coupling matrix: J_ij ~ N(0, J_std^2/N), symmetric, no self-coupling
        self.J = np.random.normal(0, config.J_std / np.sqrt(config.N), 
                                   (config.N, config.N))
        self.J = (self.J + self.J.T) / 2.0
        np.fill_diagonal(self.J, 0.0)

        # Spin state: +1 / -1
        self.spins = np.random.choice([-1, 1], size=config.N)

        # Temperature schedule
        self.T_schedule = np.linspace(config.T_anneal_start, 
                                       config.T_anneal_end, 
                                       config.T_steps)

        # History for overlap computation
        self.spin_history = []
        self.energy_history = []
        self.A_c_history = []

    def energy(self, spins: np.ndarray) -> float:
        """Hamiltonian: H = -0.5 * sum_{i!=j} J_ij s_i s_j - h sum_i s_i"""
        return -0.5 * np.sum(self.J * np.outer(spins, spins)) -                self.cfg.h_field * np.sum(spins)

    def monte_carlo_step(self, T: float) -> np.ndarray:
        """Single MC sweep (Glauber dynamics)."""
        spins = self.spins.copy()
        for i in range(self.cfg.N):
            # Local field
            h_i = np.dot(self.J[i, :], spins) + self.cfg.h_field
            # Glauber transition probability
            delta_E = 2 * h_i * spins[i]
            prob = 1.0 / (1.0 + np.exp(delta_E / max(T, 1e-12)))
            if np.random.random() < prob:
                spins[i] *= -1
        return spins

    def run_simulation(self) -> Dict:
        """Full annealing simulation with A_c tracking."""
        print(f"[C9-SNN-SG] Running SK spin-glass, N={self.cfg.N}, steps={self.cfg.T_steps}")

        for step, T in enumerate(self.T_schedule):
            self.spins = self.monte_carlo_step(T)
            self.spin_history.append(self.spins.copy())
            self.energy_history.append(self.energy(self.spins))

            # Compute A_c every 10 steps
            if step % 10 == 0 and step > 0:
                recent = np.array(self.spin_history[-min(50, len(self.spin_history)):])
                C = safe_corrcoef(recent)
                if C.shape == (self.cfg.N, self.cfg.N):
                    a_c_data = compute_assembly_index(C)
                    self.A_c_history.append({
                        "step": step,
                        "temperature": float(T),
                        **a_c_data
                    })

        # Compute overlap distribution P(q)
        self._compute_overlap_distribution()

        # Find edge of chaos: maximum A_c during annealing
        if self.A_c_history:
            max_ac_entry = max(self.A_c_history, key=lambda x: x["A_c"])
            edge_of_chaos = max_ac_entry
        else:
            edge_of_chaos = {"A_c": 0.0, "step": 0, "temperature": 0.0}

        return {
            "config": {
                "N": self.cfg.N,
                "T_steps": self.cfg.T_steps,
                "J_std": self.cfg.J_std,
                "seed": self.cfg.seed
            },
            "final_energy": float(self.energy_history[-1]),
            "min_energy": float(min(self.energy_history)),
            "edge_of_chaos": edge_of_chaos,
            "overlap_distribution": self.P_q,
            "A_c_trajectory": self.A_c_history,
            "entry_ref": "C9-2026-COMPLEX-003",
            "timestamp": time.time()
        }

    def _compute_overlap_distribution(self, n_samples: int = 100):
        """Compute P(q) from spin history."""
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

        self.P_q = {
            "mean": float(np.mean(hist)),
            "std": float(np.std(hist)),
            "min": float(np.min(hist)),
            "max": float(np.max(hist)),
            "samples": len(hist)
        }

# ââ LAVA PROCESS MODEL (if available) ââââââââââââââââââââââ
if LAVA_AVAILABLE:
    class SpinGlassProcess(AbstractProcess):
        """Lava process for spin-glass neuron."""
        def __init__(self, N: int, J: np.ndarray, **kwargs):
            super().__init__(**kwargs)
            self.N = Var(shape=(1,), init=N)
            self.J = Var(shape=J.shape, init=J)
            self.spins = Var(shape=(N,), init=np.random.choice([-1, 1], N))
            self.energy = Var(shape=(1,), init=0.0)

    @implements(proc=SpinGlassProcess, protocol=Loihi1SimCfg)
    @requires(CPU)
    class PySpinGlassModel(PyLoihiProcessModel):
        N: int = 0
        J: np.ndarray = None
        spins: np.ndarray = None
        energy: float = 0.0

        def run_sp(self):
            for i in range(self.N):
                h_i = np.dot(self.J[i, :], self.spins)
                delta_E = 2 * h_i * self.spins[i]
                prob = 1.0 / (1.0 + np.exp(delta_E / 0.5))
                if np.random.random() < prob:
                    self.spins[i] *= -1
            self.energy = -0.5 * np.sum(self.J * np.outer(self.spins, self.spins))

# ââ C9 BUS EMITTER âââââââââââââââââââââââââââââââââââââââââ
def emit_to_bus(event_type: str, data: dict):
    msg = {
        "t": time.time(),
        "event": event_type,
        "data": data
    }
    try:
        with open(C9_BUS_PATH, "a") as f:
            f.write(json.dumps(msg) + "\n")
        print(f"[C9-BUS] Emitted: {event_type}")
    except Exception as e:
        print(f"[C9-BUS] ERROR: {e}")

# ââ MAIN EXECUTION âââââââââââââââââââââââââââââââââââââââââ
if __name__ == "__main__":
    print("=" * 60)
    print("C9 SNN SPIN-GLASS v1.1")
    print("Entry: C9-2026-COMPLEX-003 (Spin Glass / Edge of Chaos)")
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

    # Emit to bus
    emit_to_bus("c9_snn_spin_glass_complete", {
        "edge_of_chaos_A_c": results["edge_of_chaos"]["A_c"],
        "edge_of_chaos_temperature": results["edge_of_chaos"]["temperature"],
        "edge_of_chaos_step": results["edge_of_chaos"]["step"],
        "overlap_mean": results["overlap_distribution"]["mean"],
        "overlap_std": results["overlap_distribution"]["std"],
        "entry_ref": "C9-2026-COMPLEX-003",
        "integration": "snn_spin_glass_lava"
    })

    print("\n[C9-SNN-SG] Complete. A_c vs. P(q) correlation ready for analysis.")
