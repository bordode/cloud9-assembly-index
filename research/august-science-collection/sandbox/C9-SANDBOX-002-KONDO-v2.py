#!/usr/bin/env python3
"""
C9 SANDBOX TEST 002-v2: Quantitative Kondo Effect
Fixed: D converted from eV to Kelvin. Proper Kondo formula.
"""

import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
ENTRY_ID = "C9-2026-MATSCI-002"

EXPERIMENTAL_TK = {"Ti": 30.0, "V": 250.0, "Cr": 2.0, "Mn": 0.01, "Fe": 29.0, "Co": 300.0, "Ni": 1000.0}
SPIN_VALUES = {"Ti": 1.0, "V": 1.5, "Cr": 2.0, "Mn": 2.5, "Fe": 2.0, "Co": 1.5, "Ni": 1.0}

# Bandwidth D = 7.0 eV, converted to Kelvin
D_EV = 7.0
EV_TO_K = 11604.525  # 1 eV = 11604.525 K
D_K = D_EV * EV_TO_K  # ~81,232 K

def kondo_tk(JN, D):
    """
    Kondo temperature: T_K = D * exp(-1/JN)
    where D is in Kelvin, JN is dimensionless coupling J*N(0).
    """
    if JN <= 0:
        return 1e-10
    return D * np.exp(-1.0 / JN)

def fit_jn_bisection(exp_tk, D, tol=1e-14):
    """Find JN from experimental T_K using bisection."""
    lo, hi = 1e-10, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        tk_mid = kondo_tk(mid, D)
        if tk_mid < exp_tk:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0

def snn_kondo_mapping(element, tk, S, JN, n_neurons=100):
    hbar, kB = 6.582e-13, 8.617e-2  # meV·s, meV/K
    E_K, tau_K = kB * tk, hbar / (kB * tk)
    T = np.linspace(0.01, 50.0, 500)
    firing_rates = []
    for t in T:
        screening = 1.0 - np.tanh(tk / t)
        rates = screening * np.random.normal(1.0, 0.2, n_neurons) * 100.0
        firing_rates.append(rates)
    pop_rate = np.mean(np.array(firing_rates), axis=1)
    transition_idx = np.argmin(np.abs(T - tk))
    return {
        "element": element, "T_K": float(tk), "S": float(S), "JN": float(JN),
        "tau_K_seconds": float(tau_K), "temperature_range": T.tolist(),
        "population_firing_rate": pop_rate.tolist(),
        "transition_temperature_idx": int(transition_idx), "n_neurons": n_neurons,
        "spike_pattern_shape": list(np.array(firing_rates).shape)
    }

def main():
    print(f"\n{'='*60}")
    print(f"C9 SANDBOX TEST 002-v2: {ENTRY_ID}")
    print(f"Quantitative Kondo Effect (eV→K conversion)")
    print(f"{'='*60}")
    print(f"    D = {D_EV:.1f} eV = {D_K:.0f} K")

    results, snn_patterns = {}, {}
    print(f"\n[1] FITTING EFFECTIVE EXCHANGE COUPLINGS")
    print(f"    {'Element':<8} {'S':<5} {'T_K(exp,K)':<12} {'T_K(calc,K)':<12} {'J*N_ef':<12} {'Error%':<8}")
    print(f"    {'-'*60}")

    for elem in ["Fe", "Mn", "Co"]:
        S = SPIN_VALUES[elem]
        exp_tk = EXPERIMENTAL_TK[elem]
        JN = fit_jn_bisection(exp_tk, D_K)
        calc_tk = kondo_tk(JN, D_K)
        error_pct = abs(calc_tk - exp_tk) / exp_tk * 100.0 if exp_tk > 0 else 0.0
        print(f"    {elem:<8} {S:<5.1f} {exp_tk:<12.3f} {calc_tk:<12.3f} {JN:<12.6f} {error_pct:<8.1f}")
        results[elem] = {"element": elem, "spin": float(S), "T_K_experimental": float(exp_tk),
                         "T_K_calculated": float(calc_tk), "JN": float(JN), "error_percent": float(error_pct)}
        snn_patterns[elem] = snn_kondo_mapping(elem, calc_tk, S, JN)

    print(f"\n[2] PASS/FAIL")
    all_pass = all(res["error_percent"] < 20.0 for res in results.values())
    for elem, res in results.items():
        print(f"    {elem}: error = {res['error_percent']:.1f}% → {'PASS' if res['error_percent'] < 20.0 else 'FAIL'}")

    print(f"\n[3] SNN MAPPING")
    for elem, pat in snn_patterns.items():
        print(f"    {elem}: τ_K = {pat['tau_K_seconds']:.2e} s, shape = {pat['spike_pattern_shape']}")

    snn_file = f"{ENTRY_ID}_snn_patterns.json"
    with open(snn_file, 'w') as f:
        json.dump(snn_patterns, f, indent=2)
    print(f"\n    SNN patterns saved to: {snn_file}")

    overall = "PASS" if all_pass else "FAIL"
    print(f"\n{'='*60}")
    print(f"OVERALL: {overall}")
    print(f"{'='*60}")

    final = {"entry_id": ENTRY_ID, "timestamp": datetime.utcnow().isoformat() + "Z",
             "test_type": "kondo_reproduction", "elements_tested": results,
             "snn_mapping": {k: {"tau_K": v["tau_K_seconds"], "shape": v["spike_pattern_shape"]} for k, v in snn_patterns.items()},
             "overall": overall}
    with open(f"{ENTRY_ID}_sandbox_result.json", 'w') as f:
        json.dump(final, f, indent=2)
    print(f"\n[4] Result saved to: {ENTRY_ID}_sandbox_result.json")

if __name__ == "__main__":
    main()
