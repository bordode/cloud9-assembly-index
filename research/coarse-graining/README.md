# Cloud-9: Multi-Scale Assembly & Subhalo Coarse-Graining

Multi-scale coarse-graining harness for evaluating the **Cosmological Assembly Index (A_c)** and Shannon-entropy "snap" dynamics across scaling parameters (λ), toward subhalo distribution analysis (ghost galaxies), JWST Little Red Dots, and lepton-equivalence test correlations.

**Origin note:** configuration (cloud9_assembly.json v1.4.0) produced via Gemini in September 2026 (Kimi credits exhausted); simulator and documentation reconstructed and integrated by Subhalo (Base44), 2026-09-20.

## What the harness does

1. Generates a synthetic 1D density field embedding structure at multiple scales, including 48 sharp "subhalo" peaks (matching the ghost-galaxy `detected_count` in the config).
2. For each coarse-graining scale λ ∈ {2, 5, 10, 20, 50}, bins the field and computes the Shannon entropy (bits) of the coarse mass distribution.
3. Compares against a **permutation surrogate** (same one-point distribution, destroyed spatial structure) as the null model.
4. Flags a "phase transition" when the normalized entropy drop `(H_null − H_field)/H_null` exceeds the configured threshold (0.85).

## Honest status (2026-09-20)

- On the synthetic field, the normalized entropy drop at every scale remains ~1–2%, far below the 0.85 threshold — the harness correctly **refuses to declare a phase transition** on synthetic structure. The negative branch is validated; the positive branch awaits real observational fields.
- The 0.85 `phase_transition_threshold` is calibrated against phase-coherence measurements (cf. the TNG100-1 mean phase coherence 0.8521 result), which apply to real halo profile stacks — the next integration step is running this coarse-graining ladder over TNG subhalo populations rather than synthetic fields.
- The observational correlations in the config (48 ghost-galaxy subhalo candidates around 3 hosts in the 1e7–1e9 M☉ range; Little Red Dots seeded by direct-collapse SMBH with A_c ≥ 12.4; PSI/ETH 2nd-generation muonium free-fall universality tests) are **configuration parameters**, not data processed here.

## Repository structure

```text
.
├── cloud9_assembly.json   # Primary parameter and observational correlation dump (v1.4.0)
├── coarse_grain_test.py    # Multi-scale coarse-graining entropy simulator
└── README.md               # This file
```

## Usage

```bash
python3 coarse_grain_test.py   # requires numpy only
```

## Cloud-9 context

- Part of the Cloud-9 Assembly Index project: github.com/bordode/cloud9-assembly-index
- A_c methodology: KSG mutual-information estimation between successive density snapshots; Causal Closure Threshold 5.41σ
