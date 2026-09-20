#!/usr/bin/env python3
"""
Cloud-9: Multi-Scale Assembly & Subhalo Coarse-Graining Entropy Simulator
=========================================================================
Tests Shannon-entropy "snap" dynamics under coarse-graining at scaling
parameters (lambda), per the coarse_graining_config in cloud9_assembly.json.

The simulator generates a synthetic multi-scale density field (embedding
structure at several physical scales), then measures how the entropy of the
field responds as the coarse-graining scale lambda is increased. A scale is
flagged as a phase-transition candidate when the normalized entropy drop
relative to a phase-randomized (surrogate) baseline exceeds the configured
threshold.

This is a synthetic test harness for the metric machinery. Observational
correlations (ghost-galaxy subhalo counts, JWST Little Red Dots, muonium
equivalence tests) are configuration parameters from cloud9_assembly.json,
not data processed by this script.

Run: python3 coarse_grain_test.py
Requires: numpy (only)
"""

import json
import numpy as np


def load_config(path="cloud9_assembly.json"):
    with open(path, "r") as f:
        config = json.load(f)
    print(f"Loaded Cloud 9 Engine v{config['metadata']['version']}")
    print(f"Target Subhalo Count: "
          f"{config['astrophysics_correlations']['ghost_galaxies']['detected_count']}")
    return config


def generate_multiscale_field(n_points, scales, seed=42):
    """Synthetic density field with embedded structure at each scale."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, n_points)
    field = rng.normal(0.0, 0.1, size=n_points)  # baseline noise
    for lam in scales:
        # embed a sinusoidal structure whose wavelength maps to this scale
        freq = n_points / (4.0 * lam)
        phase = rng.uniform(0.0, 2.0 * np.pi)
        amplitude = 0.8  # equal-strength structure at every scale
        field += amplitude * np.sin(2.0 * np.pi * freq * x + phase)
    # embed 48 sharp "subhalo" peaks (matching the ghost-galaxy detected_count
    # in the config), with widths spanning the scale ladder
    n_subhalos = 48
    centers = rng.uniform(0.0, 1.0, size=n_subhalos)
    widths = rng.choice(np.array(scales, dtype=float) / n_points, size=n_subhalos)
    for c, w in zip(centers, widths):
        field += 2.0 * np.exp(-((x - c) ** 2) / (2.0 * w ** 2 + 1e-12))
    # normalize to a positive density-like field
    field -= field.min()
    field /= field.sum() + 1e-12
    return field


def shannon_entropy_bits(probs):
    """Shannon entropy in bits of a normalized probability vector."""
    probs = np.asarray(probs, dtype=float)
    probs = probs[probs > 0]
    return float(-(probs * np.log2(probs)).sum())


def coarse_grain(field, lam):
    """Bin the field into n_bins = len(field)/lam and average."""
    n = len(field)
    n_bins = max(1, n // int(lam))
    trimmed = field[: n_bins * n_bins if False else n_bins * (n // n_bins)]
    return trimmed.reshape(n_bins, -1).mean(axis=1)


def surrogate(field, seed=7):
    """Permutation surrogate: destroys spatial structure, keeps the
    one-point distribution. This is the null model for structure detection
    (a phase-randomized surrogate would preserve the power spectrum and
    therefore the very structure we are testing for)."""
    rng = np.random.default_rng(seed)
    return rng.permutation(field)


def run(config):
    cfg = config["coarse_graining_config"]
    n = cfg["sample_points"]
    scales = cfg["scales"]
    threshold = cfg["phase_transition_threshold"]

    field = generate_multiscale_field(n, scales)
    surr = surrogate(field)

    print(f"\n{'lambda':>8} | {'H_field':>9} | {'H_surr':>9} | {'drop_norm':>10} | transition?")
    print("-" * 62)
    transitions = []
    for lam in scales:
        cg_f = coarse_grain(field, lam)
        cg_s = coarse_grain(surr, lam)
        h_f = shannon_entropy_bits(cg_f / cg_f.sum())
        h_s = shannon_entropy_bits(cg_s / cg_s.sum())
        drop_norm = (h_s - h_f) / h_s if h_s > 0 else 0.0
        hit = drop_norm >= threshold
        if hit:
            transitions.append(lam)
        print(f"{lam:>8} | {h_f:>9.4f} | {h_s:>9.4f} | {drop_norm:>10.4f} | "
              f"{'YES' if hit else 'no'}")

    print("-" * 62)
    if transitions:
        print(f"Phase-transition scales (>= {threshold}): {transitions}")
    else:
        print(f"No phase transitions exceeded threshold {threshold}.")
    lrd = config["astrophysics_correlations"]["little_red_dots"]
    print(f"Config notes: LRD direct-collapse seed mechanism requires "
          f"A_c >= {lrd['assembly_index_ac_min']}; "
          f"muonium test = {config['particle_gravity_correlations']['muonium_beam']['test_type']}.")
    return transitions


if __name__ == "__main__":
    config = load_config()
    run(config)
