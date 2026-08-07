#!/usr/bin/env python3
"""
Cloud-9 TNG Merger-Evolution Hypothesis â Data Extraction Script
=================================================================
Extracts halo properties, merger trees, and environmental context
from TNG100-1 for testing the merger-driven complexity model.

Author: Cloud-9 Assembly Framework
Date: 2026-08-07
Version: 1.0.0

Requirements:
  pip install illustris_python requests numpy scipy pandas matplotlib

  Or use the TNG API directly:
  https://www.tng-project.org/api/
"""

import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime
from scipy import stats
from scipy.spatial import cKDTree
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://www.tng-project.org/api/TNG100-1"
HEADERS = {"api-key": "YOUR_API_KEY_HERE"}  # Replace with your TNG API key

SNAPSHOT = 99  # z = 0
N_HALOS_TARGET = 2000
MASS_MIN = 1e10  # M_sun
MASS_MAX = 1e15
MIN_PARTICLES = 1000

# Output files
OUTPUT_HALOS = "c9_tng_merger_halos.csv"
OUTPUT_MERGER_TREES = "c9_tng_merger_trees.json"
OUTPUT_RESULTS = "c9_tng_merger_analysis.json"

# ============================================================
# TNG API HELPERS
# ============================================================

def get(path, params=None):
    """Make authenticated GET request to TNG API."""
    r = requests.get(path, params=params, headers=HEADERS)
    r.raise_for_status()
    if r.headers['content-type'] == 'application/json':
        return r.json()
    return r

def get_subhalos(snapshot=99, limit=100, offset=0):
    """Fetch subhalo catalog for a snapshot."""
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/"
    params = {'limit': limit, 'offset': offset}
    return get(url, params)

def get_subhalo(subhalo_id, snapshot=99):
    """Fetch detailed subhalo properties."""
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/"
    return get(url)

def get_merger_tree(subhalo_id, snapshot=99):
    """Fetch merger tree for a subhalo."""
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/merger_tree/"
    try:
        return get(url)
    except:
        return None

def get_cutout(subhalo_id, snapshot=99):
    """Fetch particle cutout for spatial analysis."""
    url = f"{BASE_URL}/snapshots/{snapshot}/subhalos/{subhalo_id}/cutout.hdf5"
    try:
        r = get(url)
        return r.content
    except:
        return None

# ============================================================
# PHASE 1: HALO SAMPLE SELECTION
# ============================================================

def select_halo_sample():
    """
    Select representative halo sample from TNG100-1.
    Criteria: M_200c > 1e10 M_sun, > 1000 particles, diverse mass range.
    """
    print("=" * 70)
    print("PHASE 1: Halo Sample Selection")
    print("=" * 70)

    halos = []
    offset = 0
    batch_size = 100

    while len(halos) < N_HALOS_TARGET:
        print(f"Fetching batch: offset={offset}, have={len(halos)}")
        data = get_subhalos(SNAPSHOT, limit=batch_size, offset=offset)

        if not data.get('results'):
            break

        for sub in data['results']:
            # Basic filters
            mass = sub.get('mass', 0) * 1e10 / 0.704  # Convert to M_sun (h=0.704)

            if mass < MASS_MIN or mass > MASS_MAX:
                continue
            if sub.get('vmax', 0) <= 0:
                continue

            halos.append({
                'subhalo_id': sub['id'],
                'mass': mass,
                'vmax': sub.get('vmax', 0),
                'vmaxrad': sub.get('vmaxrad', 0),
                'halfmassrad': sub.get('halfmassrad', 0),
                'pos_x': sub.get('pos_x', 0),
                'pos_y': sub.get('pos_y', 0),
                'pos_z': sub.get('pos_z', 0),
                'vel_x': sub.get('vel_x', 0),
                'vel_y': sub.get('vel_y', 0),
                'vel_z': sub.get('vel_z', 0),
                'spin_x': sub.get('spin_x', 0),
                'spin_y': sub.get('spin_y', 0),
                'spin_z': sub.get('spin_z', 0),
                'sfr': sub.get('sfr', 0),
                'gasmetallicity': sub.get('gasmetallicity', 0),
                'starmetallicity': sub.get('starmetallicity', 0)
            })

        offset += batch_size

        if offset > 10000:  # Safety limit
            break

    df = pd.DataFrame(halos)

    # Log-spaced mass sampling for diversity
    df['log_mass'] = np.log10(df['mass'])
    df['mass_bin'] = pd.cut(df['log_mass'], bins=10)

    # Sample evenly across mass bins
    sampled = df.groupby('mass_bin', group_keys=False).apply(
        lambda x: x.sample(min(len(x), N_HALOS_TARGET // 10), random_state=42)
    )

    print(f"\nSelected {len(sampled)} halos from {len(df)} candidates")
    print(f"Mass range: {sampled['mass'].min():.2e} - {sampled['mass'].max():.2e} M_sun")

    return sampled

# ============================================================
# PHASE 2: MERGER TREE EXTRACTION
# ============================================================

def extract_merger_trees(df_halos):
    """
    Extract merger trees for selected halos.
    Compute: formation redshift, merger history, time since last major merger.
    """
    print("\n" + "=" * 70)
    print("PHASE 2: Merger Tree Extraction")
    print("=" * 70)

    merger_data = {}

    for idx, row in df_halos.iterrows():
        sid = row['subhalo_id']
        print(f"Processing subhalo {sid}... ({idx+1}/{len(df_halos)})", end='\r')

        tree = get_merger_tree(sid, SNAPSHOT)
        if not tree:
            continue

        # Parse merger tree
        main_branch = tree.get('main_branch_progenitor', [])

        # Formation redshift: when M = M(z=0)/2
        mass_z0 = row['mass']
        formation_z = None
        for prog in main_branch:
            if prog.get('mass', 0) < mass_z0 / 2:
                formation_z = prog.get('snap', 99)
                break

        # Merger history
        mergers = []
        major_mergers = []  # mass ratio > 1:4

        for i in range(1, len(main_branch)):
            prog = main_branch[i]
            prev = main_branch[i-1]

            if prog.get('mass', 0) > prev.get('mass', 0) * 1.1:  # Significant mass jump
                ratio = prev.get('mass', 1) / prog.get('mass', 1)
                mergers.append({
                    'snap': prog.get('snap'),
                    'mass_ratio': ratio,
                    'is_major': ratio > 0.25  # 1:4 ratio
                })
                if ratio > 0.25:
                    major_mergers.append(prog.get('snap'))

        # Time since last major merger (approximate: each snapshot ~0.15 Gyr)
        if major_mergers:
            last_major_snap = max(major_mergers)
            time_since_major = (SNAPSHOT - last_major_snap) * 0.15  # Gyr
        else:
            time_since_major = 13.8  # No major merger since big bang

        merger_data[sid] = {
            'formation_redshift': formation_z,
            'n_mergers': len(mergers),
            'n_major_mergers': len(major_mergers),
            'merger_rate': len(mergers) / 13.8,  # mergers/Gyr
            'time_since_last_major_gyr': time_since_major,
            'last_major_merger_snap': major_mergers[-1] if major_mergers else None,
            'merger_history': mergers
        }

    print(f"\nExtracted merger trees for {len(merger_data)} halos")
    return merger_data

# ============================================================
# PHASE 3: ENVIRONMENTAL CONTEXT
# ============================================================

def compute_environmental_context(df_halos):
    """
    Compute local overdensity, tidal field, and neighbor properties.
    """
    print("\n" + "=" * 70)
    print("PHASE 3: Environmental Context")
    print("=" * 70)

    positions = df_halos[['pos_x', 'pos_y', 'pos_z']].values
    masses = df_halos['mass'].values

    # Build k-d tree for neighbor search
    tree = cKDTree(positions)

    env_data = []

    for idx, row in df_halos.iterrows():
        sid = row['subhalo_id']
        pos = np.array([row['pos_x'], row['pos_y'], row['pos_z']])

        # Find neighbors within 5 Mpc/h (comoving)
        neighbors = tree.query_ball_point(pos, r=5000)  # ckpc/h

        if len(neighbors) > 1:
            neighbor_masses = masses[neighbors]
            local_density = np.sum(neighbor_masses) / (4/3 * np.pi * (5)**3)  # M_sun / (Mpc/h)^3

            # Overdensity
            mean_density = np.mean(masses) / (100/0.704)**3  # Approximate
            overdensity = (local_density - mean_density) / mean_density if mean_density > 0 else 0

            # Neighbor count
            n_neighbors = len(neighbors) - 1

            # Distance to nearest massive neighbor (M > 1e12)
            massive_mask = masses > 1e12
            if np.any(massive_mask):
                massive_positions = positions[massive_mask]
                distances = np.linalg.norm(massive_positions - pos, axis=1)
                dist_to_massive = np.min(distances)
            else:
                dist_to_massive = 50000
        else:
            local_density = 0
            overdensity = -1
            n_neighbors = 0
            dist_to_massive = 50000

        env_data.append({
            'subhalo_id': sid,
            'local_density': local_density,
            'overdensity': overdensity,
            'n_neighbors_5mpc': n_neighbors,
            'dist_to_massive_neighbor_ckpc': dist_to_massive,
            'is_field': overdensity < 0,  # Underdense region
            'is_cluster': overdensity > 5  # Overdense region
        })

    df_env = pd.DataFrame(env_data)
    print(f"Computed environmental context for {len(df_env)} halos")
    print(f"Field halos: {df_env['is_field'].sum()}")
    print(f"Cluster halos: {df_env['is_cluster'].sum()}")

    return df_env

# ============================================================
# PHASE 4: A_c COMPUTATION (Existing v2.1 Formula)
# ============================================================

def compute_ac_v21(row):
    """
    Compute A_c using existing v2.1 formula.
    This is the baseline before adding environmental corrections.
    """
    # Simplified v2.1 components (from your existing code)
    mass = row['mass']
    vmax = row['vmax']
    halfmassrad = row['halfmassrad']

    # H (hierarchical complexity) â proxy from mass structure
    H = np.log10(mass / 1e10) / 5.0  # Normalize
    H = np.clip(H, 0, 1)

    # P (phase space perturbation) â from spin
    spin_mag = np.sqrt(row['spin_x']**2 + row['spin_y']**2 + row['spin_z']**2)
    P = spin_mag * 10  # Approximate
    P = np.clip(P, 0, 1)

    # I (dynamical instability) â from vmax/mass ratio
    I = vmax / (mass / 1e10)**0.33 / 300.0  # Virial velocity proxy
    I = np.clip(I, 0, 1)

    # F (information fragmentation) â from metallicity diversity
    F = abs(row['gasmetallicity'] - row['starmetallicity']) / 0.05
    F = np.clip(F, 0, 1)

    # alpha (temporal acceleration) â from SFR
    alpha = np.log10(row['sfr'] + 1e-10) / 2.0 + 0.5
    alpha = np.clip(alpha, 0, 1)

    A_c = H + P + I + F + alpha
    return {
        'A_c_v21': A_c,
        'H': H, 'P': P, 'I': I, 'F': F, 'alpha': alpha
    }

def compute_ac_with_environment(row, env_row):
    """
    Compute revised A_c with environmental context.
    A_c_total = [H + P + I + F + alpha] Ã (1 + w_env Ã E_env) Ã exp(-T_dyn / Ï_norm)
    """
    base = compute_ac_v21(row)
    ac_base = base['A_c_v21']

    # Environmental context
    w_env = 0.3
    E_env = np.tanh(env_row['overdensity'] / 5.0)  # Normalized overdensity

    # Dynamical age (time since last major merger)
    tau_norm = 2.0  # Gyr
    T_dyn = row.get('time_since_last_major_gyr', 5.0)

    ac_revised = ac_base * (1 + w_env * E_env) * np.exp(-T_dyn / tau_norm)

    return {
        'A_c_v21': ac_base,
        'A_c_revised': ac_revised,
        'E_env': E_env,
        'T_dyn': T_dyn,
        'env_correction': (1 + w_env * E_env),
        'dyn_correction': np.exp(-T_dyn / tau_norm)
    }

# ============================================================
# PHASE 5: STATISTICAL TESTS
# ============================================================

def run_statistical_tests(df):
    """
    Run the 5 testable predictions from the merger-evolution hypothesis.
    """
    print("\n" + "=" * 70)
    print("PHASE 5: Statistical Tests")
    print("=" * 70)

    results = {}

    # Test A: A_c vs time_since_last_major_merger (negative correlation)
    print("\n[Test A] A_c vs Time Since Last Major Merger")
    valid = df.dropna(subset=['A_c_revised', 'time_since_last_major_gyr'])
    if len(valid) > 10:
        r, p = stats.pearsonr(valid['time_since_last_major_gyr'], valid['A_c_revised'])
        print(f"  Pearson r = {r:.3f}, p = {p:.4f}")
        test_a_pass = r < -0.1 and p < 0.05
        print(f"  Prediction: negative correlation")
        print(f"  Result: {'PASS â' if test_a_pass else 'FAIL â'} (r < -0.1, p < 0.05)")
        results['Test_A'] = {'r': r, 'p': p, 'pass': test_a_pass}
    else:
        print("  Insufficient data")
        results['Test_A'] = {'error': 'insufficient_data'}

    # Test B: A_c vs overdensity (stronger than mass)
    print("\n[Test B] A_c vs Overdensity vs Mass")
    valid = df.dropna(subset=['A_c_revised', 'overdensity', 'mass'])
    if len(valid) > 10:
        r_mass, p_mass = stats.pearsonr(np.log10(valid['mass']), valid['A_c_revised'])
        r_env, p_env = stats.pearsonr(valid['overdensity'], valid['A_c_revised'])
        print(f"  r(A_c, mass) = {r_mass:.3f}, p = {p_mass:.4f}")
        print(f"  r(A_c, overdensity) = {r_env:.3f}, p = {p_env:.4f}")
        test_b_pass = abs(r_env) > abs(r_mass)
        print(f"  Prediction: |r_env| > |r_mass|")
        print(f"  Result: {'PASS â' if test_b_pass else 'FAIL â'}")
        results['Test_B'] = {'r_mass': r_mass, 'r_env': r_env, 'pass': test_b_pass}

    # Test C: Merger tree tracking (requires individual halo analysis)
    print("\n[Test C] Merger Tree Tracking")
    print("  REQUIRES: Individual merger tree analysis for 100 major mergers")
    print("  Track A_c before/during/after merger event")
    print("  Expected: Peak at pericenter, exponential decay")
    print("  Status: MANUAL ANALYSIS REQUIRED")
    results['Test_C'] = {'status': 'requires_manual_analysis'}

    # Test D: Substructure fraction vs concentration
    print("\n[Test D] Substructure vs Concentration as A_c Predictor")
    # Proxy: use vmax/mass ratio as substructure indicator
    df['f_sub_proxy'] = df['vmax'] / (df['mass'] / 1e10)**0.33
    df['c_nfw_proxy'] = df['halfmassrad'] / (df['mass'] / 1e10)**0.33

    r_sub, _ = stats.pearsonr(df['f_sub_proxy'], df['A_c_revised'])
    r_c, _ = stats.pearsonr(df['c_nfw_proxy'], df['A_c_revised'])
    print(f"  RÂ²(A_c ~ f_sub_proxy) = {r_sub**2:.3f}")
    print(f"  RÂ²(A_c ~ c_nfw_proxy) = {r_c**2:.3f}")
    test_d_pass = r_sub**2 > r_c**2 * 2
    print(f"  Prediction: RÂ²_sub > 2 Ã RÂ²_c")
    print(f"  Result: {'PASS â' if test_d_pass else 'FAIL â'}")
    results['Test_D'] = {'r2_sub': r_sub**2, 'r2_c': r_c**2, 'pass': test_d_pass}

    # Test E: Field vs Cluster at fixed mass
    print("\n[Test E] Field vs Cluster Halos at Fixed Mass")
    field = df[df['is_field'] == True]
    cluster = df[df['is_cluster'] == True]

    if len(field) > 5 and len(cluster) > 5:
        t_stat, p_val = stats.ttest_ind(cluster['A_c_revised'], field['A_c_revised'])
        print(f"  Field mean A_c: {field['A_c_revised'].mean():.3f} Â± {field['A_c_revised'].std():.3f}")
        print(f"  Cluster mean A_c: {cluster['A_c_revised'].mean():.3f} Â± {cluster['A_c_revised'].std():.3f}")
        print(f"  t-test: t = {t_stat:.3f}, p = {p_val:.4f}")
        test_e_pass = t_stat > 0 and p_val < 0.05
        print(f"  Prediction: cluster > field")
        print(f"  Result: {'PASS â' if test_e_pass else 'FAIL â'}")
        results['Test_E'] = {'t': t_stat, 'p': p_val, 'pass': test_e_pass}
    else:
        print("  Insufficient field/cluster halos")
        results['Test_E'] = {'error': 'insufficient_data'}

    # Summary
    print("\n" + "=" * 70)
    print("STATISTICAL TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results.values() if r.get('pass', False))
    print(f"Passed: {passed}/5")

    return results

# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    print("Cloud-9 TNG Merger-Evolution Hypothesis â Data Extraction")
    print(f"Target: {N_HALOS_TARGET} halos from TNG100-1 snapshot {SNAPSHOT}")
    print()

    # Phase 1: Select halos
    df_halos = select_halo_sample()
    df_halos.to_csv(OUTPUT_HALOS, index=False)
    print(f"Saved: {OUTPUT_HALOS}")

    # Phase 2: Extract merger trees
    merger_data = extract_merger_trees(df_halos)
    with open(OUTPUT_MERGER_TREES, 'w') as f:
        json.dump(merger_data, f, indent=2)
    print(f"Saved: {OUTPUT_MERGER_TREES}")

    # Merge merger data into halo dataframe
    for sid, data in merger_data.items():
        for key, val in data.items():
            if key != 'merger_history':
                df_halos.loc[df_halos['subhalo_id'] == sid, key] = val

    # Phase 3: Environmental context
    df_env = compute_environmental_context(df_halos)
    df_merged = df_halos.merge(df_env, on='subhalo_id')

    # Phase 4: Compute A_c
    print("\n" + "=" * 70)
    print("PHASE 4: Computing A_c (v2.1 + environmental corrections)")
    print("=" * 70)

    ac_results = []
    for idx, row in df_merged.iterrows():
        env_row = df_env[df_env['subhalo_id'] == row['subhalo_id']].iloc[0]
        ac = compute_ac_with_environment(row, env_row)
        ac_results.append(ac)

    df_ac = pd.DataFrame(ac_results)
    df_final = pd.concat([df_merged.reset_index(drop=True), df_ac], axis=1)

    print(f"A_c v2.1 range: [{df_ac['A_c_v21'].min():.3f}, {df_ac['A_c_v21'].max():.3f}]")
    print(f"A_c revised range: [{df_ac['A_c_revised'].min():.3f}, {df_ac['A_c_revised'].max():.3f}]")

    # Phase 5: Statistical tests
    test_results = run_statistical_tests(df_final)

    # Save final results
    final_output = {
        'timestamp': datetime.now().isoformat(),
        'n_halos': len(df_final),
        'test_results': test_results,
        'summary_statistics': {
            'ac_v21_mean': df_ac['A_c_v21'].mean(),
            'ac_v21_std': df_ac['A_c_v21'].std(),
            'ac_revised_mean': df_ac['A_c_revised'].mean(),
            'ac_revised_std': df_ac['A_c_revised'].std(),
            'field_mean_ac': df_final[df_final['is_field']]['A_c_revised'].mean() if df_final['is_field'].sum() > 0 else None,
            'cluster_mean_ac': df_final[df_final['is_cluster']]['A_c_revised'].mean() if df_final['is_cluster'].sum() > 0 else None
        }
    }

    with open(OUTPUT_RESULTS, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"\nSaved: {OUTPUT_RESULTS}")
    print("\nPipeline complete!")

    return df_final, test_results

if __name__ == "__main__":
    # NOTE: Replace YOUR_API_KEY_HERE with actual TNG API key
    print("""
    BEFORE RUNNING:
    1. Get TNG API key from: https://www.tng-project.org/data/access/
    2. Replace YOUR_API_KEY_HERE in HEADERS dict
    3. Install dependencies: pip install requests pandas scipy
    4. Run: python c9_tng_merger_extraction.py

    EXPECTED RUNTIME: 2-4 hours for 2000 halos (API rate limited)
    ALTERNATIVE: Use local TNG data files if available
    """)

    # Uncomment to run:
    # df, results = main()
