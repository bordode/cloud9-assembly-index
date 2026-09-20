# Cloud 9: Multi-Scale Assembly & Subhalo Coarse-Graining Research

This repository contains numerical models, data schemas, and research scripts for evaluating the **Cosmological Assembly Index ($A_c$)** across multi-scale physical phenomena — from sparse particle event topographies to dark matter subhalo distributions and early-universe Compact High-Redshift Objects (JWST Little Red Dots).

## Highlights (September 2026 Updates)

- **Scale-Dependent Entropy Snaps:** Analyzing Shannon entropy phase transitions under variable coarse-graining scales ($\lambda$).
- **Subhalo Integration:** Mapping parameter sets for ~50 newly detected ghost dwarf galaxy candidates around host halos.
- **Quantum & Gravitational Thresholds:** Testing assembly metrics against 2nd-generation lepton mass interactions (Muonium WEP tests).

## Key Themes & Cloud 9 Connections (source articles, Sept 2026)

| Source | The news | Cloud 9 connection |
|--------|----------|--------------------|
| Phys.org — Dwarf galaxies | ~50 faint dwarf galaxy candidates found around three host galaxies — challenges current cosmological mass function models | Direct input for dark matter subhalo modeling: sparse signal features (dwarf subhalos against background vacuum) exhibit a distinct entropy decay curve under coarse-graining ($\lambda$). These 48+ candidate subhalos give real observational data to calibrate sparse entropy bounds ($A_c$). |
| SmartNews — JWST "Little Red Dots" | Simulations suggest compact high-redshift objects are massive black hole seeds growing without traditional stellar intermediate steps (direct-collapse SMBH) | Early rapid SMBH formation requires high local spatial organization at small observational wavelengths ($\lambda \le 5$): supports a model where the cosmological assembly transition snaps early in high-density pockets rather than building up slowly over cosmic time. |
| Phys.org — PSI/ETH Zurich | Cold muonium particle beam created to test whether 2nd-generation leptons obey the Weak Equivalence Principle under gravity | Testing second-generation mass hierarchies under gravity provides a concrete quantum-to-classical assembly threshold. |
| SmartNews/ScienceDaily — phonon quantum jumps & emergent time | Phonon state quantum jumps; time emerging from entanglement without a global clock | Reinforces the premise that macroscopic observables (time, classical fields) emerge through coarse-graining of fine-grained quantum interactions — mirroring the multi-scale transition test. |

## Origin note

Configuration (cloud9_assembly.json v1.4.0) produced via Gemini in September 2026 (Kimi credits exhausted); simulator, key-themes integration, and documentation reconstructed by Subhalo (Base44), 2026-09-20.

## What the harness does

1. Generates a synthetic 1D density field embedding structure at multiple scales, including 48 sharp "subhalo" peaks (matching the ghost-galaxy `detected_count` in the config).
2. For each coarse-graining scale λ ∈ {2, 5, 10, 20, 50}, bins the field and computes the Shannon entropy (bits) of the coarse mass distribution.
3. Compares against a **permutation surrogate** (same one-point distribution, destroyed spatial structure) as the null model.
4. Flags a "phase transition" when the normalized entropy drop `(H_null − H_field)/H_null` exceeds the configured threshold (0.85).

## Honest status (2026-09-20)

- On the synthetic field, the normalized entropy drop at every scale remains ~1–2%, far below the 0.85 threshold — the harness correctly **refuses to declare a phase transition** on synthetic structure. The negative branch is validated; the positive branch awaits real observational fields.
- The 0.85 `phase_transition_threshold` is calibrated against phase-coherence measurements (cf. the TNG100-1 mean phase coherence 0.8521 result), which apply to real halo profile stacks — the next integration step is running this coarse-graining ladder over the 48+ ghost-galaxy subhalo candidates rather than synthetic fields.
- The observational correlations in the config are **configuration parameters**, not data processed here.

## Repository structure

```text
.
├── cloud9_assembly.json   # Primary parameter configuration and observational dump
├── coarse_grain_test.py   # Multi-scale entropy & scale-transition simulator
└── README.md              # Project documentation
```

## Quick Start (Google Colab / Termux)

```python
import json

with open('cloud9_assembly.json', 'r') as f:
    config = json.load(f)

print(f"Loaded Cloud 9 Suite v{config['metadata']['version']}")
print(f"Subhalo Candidates Modeled: {config['astrophysics_correlations']['ghost_galaxies']['detected_count']}")
```

Full simulation: `python3 coarse_grain_test.py` (requires numpy only).

## License

MIT

## Cloud-9 context

- Part of the Cloud-9 Assembly Index project: github.com/bordode/cloud9-assembly-index
- A_c methodology: KSG mutual-information estimation between successive density snapshots; Causal Closure Threshold 5.41σ
