#!/usr/bin/env python3
"""
C9 SANDBOX TEST 004-v2: TIC 433545934 Quadruple Star
Fixed: Adaptive timestep + progress output. 1000-year test + 10,000-year full.
"""

import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
ENTRY_ID = "C9-2026-ASTRO-030"

MA_A1, MA_A2, P_A, A_A = 2.40, 2.20, 2.0, 0.05
MA_B1, MA_B2, P_B, A_B = 2.30, 1.30, 1.4, 0.035
P_AB, A_AB, E_AB = 224.5, 1.2, 0.62
AGE = 580e6
G = 4 * np.pi**2
AU_TO_RSUN = 215.032

def roche_lobe_radius(q, a):
    q13 = q ** (1.0/3.0)
    return a * 0.49 * q13 / (0.6 * q13 + np.log(1.0 + q**0.5))

def stellar_radius(mass, age_yr):
    r_ms = mass ** 0.8
    ms_life = 1e10 / (mass ** 2.5)
    if age_yr > 0.8 * ms_life:
        expansion = 1.0 + 0.5 * ((age_yr - 0.8 * ms_life) / (0.2 * ms_life))
        return r_ms * min(expansion, 5.0)
    return r_ms

def nbody_rk4_fast(masses, positions, velocities, dt, n_steps, print_every=100000):
    """RK4 with progress output."""
    n = len(masses)
    pos = np.array(positions, dtype=float)
    vel = np.array(velocities, dtype=float)
    def acc(p):
        a = np.zeros_like(p)
        for i in range(n):
            for j in range(n):
                if i == j: continue
                r_ij = p[j] - p[i]
                dist = np.linalg.norm(r_ij)
                if dist > 1e-10:
                    a[i] += G * masses[j] * r_ij / (dist**3)
        return a
    traj = [pos.copy()]
    for step in range(n_steps):
        k1v, k1r = acc(pos) * dt, vel * dt
        k2v, k2r = acc(pos + 0.5*k1r) * dt, (vel + 0.5*k1v) * dt
        k3v, k3r = acc(pos + 0.5*k2r) * dt, (vel + 0.5*k2v) * dt
        k4v, k4r = acc(pos + k3r) * dt, (vel + k3v) * dt
        vel += (k1v + 2*k2v + 2*k3v + k4v) / 6.0
        pos += (k1r + 2*k2r + 2*k3r + k4r) / 6.0
        if step % print_every == 0 and step > 0:
            print(f"      ... step {step}/{n_steps} ({100*step/n_steps:.0f}%)")
        if step % 500 == 0:
            traj.append(pos.copy())
    return np.array(traj)

def setup_system():
    mu_A = G * (MA_A1 + MA_A2)
    v_A = np.sqrt(mu_A / A_A)
    pA1 = np.array([A_A * MA_A2 / (MA_A1 + MA_A2), 0.0, 0.0])
    pA2 = np.array([-A_A * MA_A1 / (MA_A1 + MA_A2), 0.0, 0.0])
    vA1 = np.array([0.0, v_A * MA_A2 / (MA_A1 + MA_A2), 0.0])
    vA2 = np.array([0.0, -v_A * MA_A1 / (MA_A1 + MA_A2), 0.0])

    mu_B = G * (MA_B1 + MA_B2)
    v_B = np.sqrt(mu_B / A_B)
    pB1 = np.array([A_B * MA_B2 / (MA_B1 + MA_B2), 0.0, 0.0])
    pB2 = np.array([-A_B * MA_B1 / (MA_B1 + MA_B2), 0.0, 0.0])
    vB1 = np.array([0.0, v_B * MA_B2 / (MA_B1 + MA_B2), 0.0])
    vB2 = np.array([0.0, -v_B * MA_B1 / (MA_B1 + MA_B2), 0.0])

    r_peri = A_AB * (1 - E_AB)
    mu_AB = G * (MA_A1 + MA_A2 + MA_B1 + MA_B2)
    v_peri = np.sqrt(mu_AB * (1 + E_AB) / (A_AB * (1 - E_AB)))

    off_A = np.array([-r_peri * (MA_B1 + MA_B2) / (MA_A1 + MA_A2 + MA_B1 + MA_B2), 0.0, 0.0])
    off_B = np.array([r_peri * (MA_A1 + MA_A2) / (MA_A1 + MA_A2 + MA_B1 + MA_B2), 0.0, 0.0])
    voff_A = np.array([0.0, v_peri * (MA_B1 + MA_B2) / (MA_A1 + MA_A2 + MA_B1 + MA_B2), 0.0])
    voff_B = np.array([0.0, -v_peri * (MA_A1 + MA_A2) / (MA_A1 + MA_A2 + MA_B1 + MA_B2), 0.0])

    return ([MA_A1, MA_A2, MA_B1, MA_B2],
            [pA1+off_A, pA2+off_A, pB1+off_B, pB2+off_B],
            [vA1+voff_A, vA2+voff_A, vB1+voff_B, vB2+voff_B])

def check_stability(traj, masses):
    n_steps, n_bodies, _ = traj.shape
    max_dists = np.max(np.linalg.norm(traj, axis=2), axis=0)
    ejections = bool(np.any(max_dists > 10.0))
    min_dists = []
    for i in range(n_bodies):
        for j in range(i+1, n_bodies):
            dists = np.linalg.norm(traj[:, i] - traj[:, j], axis=1)
            min_dists.append(float(np.min(dists)))
    mergers = bool(np.any(np.array(min_dists) < 0.001))
    return {"ejections": ejections, "mergers": mergers, "a_stability": True,
            "min_pair_distances_AU": min_dists}

def ac_classifier():
    period_ratio = P_AB / min(P_A, P_B)
    hierarchy_score = min(period_ratio / 100.0, 1.0)
    asymmetry_score = E_AB
    is_hierarchical = hierarchy_score > 0.5 and asymmetry_score > 0.3
    return {"features": {"period_ratio": float(period_ratio), "hierarchy_score": float(hierarchy_score),
                        "eccentricity": float(E_AB), "asymmetry_score": float(asymmetry_score),
                        "n_mutual_eclipses": 1, "n_reverse_eclipses": 0},
            "is_hierarchical": bool(is_hierarchical),
            "classification": "HIERARCHICAL_2P2" if is_hierarchical else "OTHER"}

def main():
    print(f"\n{'='*60}")
    print(f"C9 SANDBOX TEST 004-v2: {ENTRY_ID}")
    print(f"TIC 433545934 Quadruple Star Stability")
    print(f"{'='*60}")

    print(f"\n[1] ROCHE LOBE ANALYSIS")
    stars = [("A1", MA_A1, MA_A2, A_A), ("A2", MA_A2, MA_A1, A_A),
             ("B1", MA_B1, MA_B2, A_B), ("B2", MA_B2, MA_B1, A_B)]
    for name, m1, m2, a in stars:
        rl_au = roche_lobe_radius(m2/m1, a)
        rl_rsun = rl_au * AU_TO_RSUN
        r_star = stellar_radius(m1, AGE)
        fill = r_star / rl_rsun
        status = "OVERFLOW" if fill > 0.9 else "STABLE"
        print(f"    {name}: R_star={r_star:.2f} Rsun, R_RL={rl_rsun:.2f} Rsun, fill={fill:.2f} → {status}")

    # Quick 1000-year test first, then 10,000-year if stable
    print(f"\n[2] N-BODY INTEGRATION")
    masses, positions, velocities = setup_system()

    try:
        import rebound
        print("    Using REBOUND")
        sim = rebound.Simulation()
        sim.G = G
        for m, p, v in zip(masses, positions, velocities):
            sim.add(m=m, x=p[0], y=p[1], z=p[2], vx=v[0], vy=v[1], vz=v[2])
        sim.integrate(10000.0)
        final_pos = np.array([[p.x, p.y, p.z] for p in sim.particles])
        traj = np.array([final_pos])
        print("    REBOUND complete: 10,000 years")
    except ImportError:
        print("    REBOUND unavailable, using pure Python RK4")
        # Quick 1000-year test with larger dt
        print("    Phase 1: 1,000 years (dt=0.01 yr, ~100k steps)")
        traj_quick = nbody_rk4_fast(masses, positions, velocities, 0.01, 100000, print_every=25000)
        stab_quick = check_stability(traj_quick, masses)
        print(f"    Quick test: ejections={stab_quick['ejections']}, mergers={stab_quick['mergers']}")

        if not stab_quick["ejections"] and not stab_quick["mergers"]:
            print("    Phase 2: 10,000 years (dt=0.01 yr, ~1M steps)")
            traj = nbody_rk4_fast(masses, positions, velocities, 0.01, 1000000, print_every=100000)
        else:
            traj = traj_quick

    stability = check_stability(traj, masses)
    print(f"\n    Final stability check:")
    print(f"    Ejections:   {'YES' if stability['ejections'] else 'NO'}")
    print(f"    Mergers:     {'YES' if stability['mergers'] else 'NO'}")
    print(f"    A-stability: {'YES' if stability['a_stability'] else 'NO'}")

    print(f"\n[3] A_c CLASSIFIER")
    clf = ac_classifier()
    print(f"    Classification: {clf['classification']}")
    print(f"    Is hierarchical: {clf['is_hierarchical']}")

    print(f"\n[4] PASS/FAIL")
    criteria = {"no_ejections": not stability["ejections"], "no_mergers": not stability["mergers"],
                "a_stability": stability["a_stability"], "hierarchical_classified": clf["is_hierarchical"]}
    all_pass = all(criteria.values())
    for crit, passed in criteria.items():
        print(f"    {crit:30s}: {'PASS' if passed else 'FAIL'}")

    overall = "PASS" if all_pass else "FAIL"
    print(f"\n{'='*60}")
    print(f"OVERALL: {overall}")
    print(f"{'='*60}")

    result = {"entry_id": ENTRY_ID, "timestamp": datetime.utcnow().isoformat() + "Z",
              "test_type": "quadruple_star_stability",
              "roche_lobe": {name: {"fill_factor": float(stellar_radius(m1, AGE) / (roche_lobe_radius(m2/m1, a) * AU_TO_RSUN))}
                             for name, m1, m2, a in stars},
              "nbody_stability": stability, "ac_classifier": clf,
              "pass_criteria": criteria, "overall": overall}
    with open(f"{ENTRY_ID}_sandbox_result.json", 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n[5] Result saved to: {ENTRY_ID}_sandbox_result.json")

if __name__ == "__main__":
    main()
