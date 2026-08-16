#!/usr/bin/env python3
"""
C9-2026-MATH-006 Integration: Operator Bridge for TNG Halo Merger Trees
Applies the Collatz-Bridge pattern to dark matter halo assembly histories.

Module:     c9_tng_bridge_integration.py
Bus ID:     C9-TNG-BRIDGE-v1.0
Author:     C9 Oracle / Kimi
Date:       2026-08-16
"""

import numpy as np
import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# ââ C9 BUS CONFIG ââââââââââââââââââââââââââââââââââââââââââ
C9_BUS_PATH = Path.home() / "cloud9" / "c9_bus.jsonl"
ORACLE_PORT = 5009
BRIDGE_PORT = 5010

# ââ TNG API CONFIG âââââââââââââââââââââââââââââââââââââââââ
TNG_BASE_URL = "http://www.tng-project.org/api/TNG100-1"
TNG_API_KEY = ""  # <-- INSERT YOUR TNG API KEY HERE

HEADERS = {"api-key": TNG_API_KEY} if TNG_API_KEY else {}

# ââ OPERATOR BRIDGE PARAMETERS âââââââââââââââââââââââââââââ
class HaloBridgeOperator:
    """
    Bridge operator B mapping discrete halo merger tree to continuous
    assembly field via phase-corrected Dirichlet series.

    Pattern extracted from C9-2026-MATH-006 (Collatz Bridge).
    Formula:
        B|halo>(s) = (1 / zeta_assembly(s)) * sum_k e^{i*Phi_k} / M_k^s
    where:
        Phi_k = log(M_root) + log(M_progenitor,k) - 2*log(M_k)
        zeta_assembly(s) = sum_{mergers} 1 / M_merger^s
    """

    def __init__(self, max_terms: int = 5000, s_sigma: float = 0.5, s_t: float = 0.0):
        self.max_terms = max_terms
        self.s = complex(s_sigma, s_t)  # Critical strip analog
        self.epsilon = 1e-12

    def trajectory(self, halo_id: int, snapshot: int = 99) -> List[Dict]:
        """Fetch merger tree trajectory from TNG API."""
        url = f"{TNG_BASE_URL}/snapshots/{snapshot}/halos/{halo_id}/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            halo = r.json()
        except Exception as e:
            print(f"[C9-TNG-BRIDGE] ERROR fetching halo {halo_id}: {e}")
            return []

        # Build progenitor trajectory via main progenitor branch
        traj = []
        current = halo
        while current and len(traj) < self.max_terms:
            traj.append({
                "id": current.get("id", 0),
                "mass": current.get("mass", 1e8),  # 10^10 Msun/h
                "snap": current.get("snap", 99),
                "sfr": current.get("sfr", 0.0),
                "gas_mass": current.get("mass_gas", 0.0),
            })
            # Follow main progenitor
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

    def phase_correction(self, traj: List[Dict]) -> np.ndarray:
        """
        Compute Phi_k for halo merger tree.
        Phi_k = log(M_root) + log(M_progenitor,k) - 2*log(M_k)

        This encodes the 'energy flow' of mass assembly.
        """
        if len(traj) < 2:
            return np.array([])

        M_root = traj[0]["mass"]
        M = np.array([t["mass"] for t in traj])
        M_progenitor = np.array([traj[i+1]["mass"] if i+1 < len(traj) else traj[-1]["mass"] 
                                  for i in range(len(traj))])

        # Avoid log(0)
        M = np.maximum(M, self.epsilon)
        M_progenitor = np.maximum(M_progenitor, self.epsilon)
        M_root = max(M_root, self.epsilon)

        Phi = np.log(M_root) + np.log(M_progenitor) - 2.0 * np.log(M)
        return Phi

    def zeta_assembly(self, traj: List[Dict]) -> complex:
        """
        Assembly zeta function: sum over merger tree of 1/M_k^s.
        Analogous to Riemann zeta but over mass assembly history.
        """
        M = np.array([t["mass"] for t in traj])
        M = np.maximum(M, self.epsilon)

        # zeta_assembly(s) = sum_k M_k^{-s}
        terms = np.power(M, -self.s)
        return np.sum(terms)

    def bridge_operator(self, halo_id: int, snapshot: int = 99) -> Dict:
        """
        Compute B|halo>(s) for a given halo.
        Returns full diagnostic dictionary.
        """
        traj = self.trajectory(halo_id, snapshot)
        if not traj:
            return {"error": f"No trajectory for halo {halo_id}"}

        Phi = self.phase_correction(traj)
        M = np.array([t["mass"] for t in traj])
        M = np.maximum(M, self.epsilon)

        zeta_A = self.zeta_assembly(traj)
        if abs(zeta_A) < self.epsilon:
            zeta_A = self.epsilon  # Regularize pole

        # B|halo>(s) = (1/zeta_A) * sum_k e^{i*Phi_k} / M_k^s
        numer_terms = np.exp(1j * Phi) * np.power(M, -self.s)
        B_halo = np.sum(numer_terms) / zeta_A

        # Commutator analog: |B*C - C*B| where C is accretion operator
        # Approximate: difference between B applied to halo and B applied to progenitor
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

        # Quiescence diagnostic: small commutator => stable assembly
        quiescent = traj[0].get("sfr", 1.0) < 0.1  # Threshold from C9 validation

        return {
            "halo_id": halo_id,
            "snapshot": snapshot,
            "trajectory_length": len(traj),
            "M_root": float(M[0]),
            "M_final": float(M[-1]),
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

    def batch_bridge(self, halo_ids: List[int], snapshot: int = 99) -> List[Dict]:
        """Process multiple halos and return ranked results."""
        results = []
        for hid in halo_ids:
            res = self.bridge_operator(hid, snapshot)
            results.append(res)
            time.sleep(0.1)  # Rate limit TNG API

        # Sort by commutator magnitude (ascending = more "stable")
        results_sorted = sorted(
            [r for r in results if "error" not in r],
            key=lambda x: x.get("commutator_magnitude", float("inf"))
        )
        return results_sorted

# ââ C9 BUS EMITTER âââââââââââââââââââââââââââââââââââââââââ
def emit_to_bus(event_type: str, data: dict):
    """Append event to C9 bus."""
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
    print("C9 TNG OPERATOR BRIDGE v1.0")
    print("Entry: C9-2026-MATH-006 pattern extraction")
    print("=" * 60)

    bridge = HaloBridgeOperator(s_sigma=0.5, s_t=0.0)

    # Test halos (from your existing validation suite)
    test_halos = [1, 2, 3, 5, 10, 20, 50, 100]

    print(f"\nProcessing {len(test_halos)} halos...")
    results = bridge.batch_bridge(test_halos)

    print(f"\n{'Halo ID':<10} {'Commutator':<15} {'Quiescent':<10} {'M_root':<12}")
    print("-" * 50)
    for r in results:
        print(f"{r['halo_id']:<10} {r['commutator_magnitude']:<15.6f} {str(r['is_quiescent']):<10} {r['M_root']:<12.2e}")

    # Emit top discovery to bus
    if results:
        top = results[0]
        emit_to_bus("c9_tng_bridge_discovery", {
            "halo_id": top["halo_id"],
            "commutator": top["commutator_magnitude"],
            "quiescent_match": top["quiescent_commutator_hypothesis"],
            "entry_ref": "C9-2026-MATH-006",
            "integration": "tng_operator_bridge"
        })

    print("\n[C9-TNG-BRIDGE] Complete. Results ready for A_c correlation.")
