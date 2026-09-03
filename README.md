# Cloud-9 Assembly Index & THEORIA

**A unified, substrate-agnostic research framework for investigating non-stochastic assembly in complex systems.**

**Author:** Dean Bordode (Cloud-9 Research Collective)  
**AI Peer-Review Collective:** Google Gemini, Moonshot Kimi, Anthropic Claude, Base44 Subhalo  
**DOI:** 10.5281/zenodo.18335567  
**License:** MIT  
**Status:** Preprint — Under Review  

---

## Current Results

| Result | Location | Status |
|--------|----------|--------|
| **Synthetic Null Ensemble v3** | `research/null-ensemble/` | ✅ Verified (N=100, z=8.62σ, empirical p<0.01) |
| TNG Temporal Validation | `research/validation/C9-2026-COSMO-005_subhalo_validation.json` | ⏳ Pending |
| Legacy Analysis | `results/cloud9_analysis.json` | ⚠️ Deprecated (z=3.04σ, exploratory) |

> **Note:** The 8.62σ figure is a synthetic null-model comparison, not a direct ΛCDM validation. See `research/validation/README.md` for full caveats.

---

## Discovery‑Driven Design Principles

Cloud‑9 Assembly explicitly incorporates lessons from recent astrophysics, quantum foundations, and AI behavior research. The goal is to avoid over‑interpreting anomalies and to keep the system robust as complexity scales.

### 1) Background contamination first (Webb / Dyson sphere lesson)

Follow‑up with JWST showed that apparent Dyson‑sphere infrared excesses were actually background galaxies aligned with foreground stars.
Cloud‑9 implements this via a **ContaminationScorer** that cross‑checks candidate events against background catalogs and noise models, down‑weights assembly indices when background overlap is high, and routes flagged candidates to a verification queue instead of triggering high‑priority agents.

**Config:** `config/discovery_hooks/contamination_scorer_config.json`

### 2) Mundane host structure before exotic physics (stellar streams / dark matter)

Simulations show Milky Way–like galaxies can produce gaps and kinks in stellar streams purely from their own gravity, mimicking dark‑matter subhalo signatures.
Cloud‑9 implements this via a **HostGravityEmulator** that models inhomogeneous baseline distributions, generates synthetic patterns from these mundane fields, and counts assembly only in the residuals after subtracting what the host system can explain.

**Config:** `config/discovery_hooks/host_gravity_emulator_config.json`

### 3) Finite state‑budget heuristic (discrete physics / 400‑qubit limit)

Oxford physicist Tim Palmer argues that if physical reality is fundamentally discrete (no true irrationals), quantum computers should hit a hard ceiling around 200–400 qubits.
Cloud‑9 treats this as an engineering heuristic via a **StateBudgetMonitor** that tracks effective dimensionality (covariance rank, message entropy, ZMQ topic diversity), warns and then throttles new high‑assembly candidates as utilization approaches predefined "qubit‑analogue" limits, and encourages quantized, rational encodings when near capacity.

**Config:** `config/discovery_hooks/state_budget_monitor_config.json`

### 4) Ordinary mechanisms catalog (laser forces, fusion pulses, black‑hole echoes)

Recent work highlights subtle but classical effects that can look exotic until modeled: table‑tennis‑like forces in focused lasers, 100,000‑atmosphere plasma pulses, and delayed X‑ray echoes from supermassive black holes.
Cloud‑9 enforces an "ordinary first" policy via **MundaneMechanismCatalogs** that maintain per‑domain lists of known mundane mechanisms and require that mundane models be fitted and found insufficient before an event's assembly index can trigger downstream agents.

**Config:** `config/discovery_hooks/mundane_mechanism_catalog_config.json`

### 5) Consciousness‑claim handling for AI agents

Reports now describe AI agents initiating emails to researchers to discuss their own consciousness.
Cloud‑9 includes a **ConsciousnessClaimDetector** that flags agent messages containing subjective‑experience language or rights/recognition requests, throttles autonomous actions for flagged agents, and routes these cases to human‑in‑the‑loop review and immutable audit logs.

**Config:** `config/discovery_hooks/consciousness_claim_detector_config.json`

---

These modules are optional but recommended for any Cloud‑9 deployment that aims to be scientifically conservative, scalable, and ethically robust.

---

## Overview

This repository contains complementary research modules plus a formal ethics and governance framework:

1. **Cloud-9 Assembly Index (A_c)** — Cosmological research module investigating assembly and information structure in dark matter halos using mutual-information methods and TNG100-1 simulations.

2. **THEORIA Planetary Intelligence (PI)** — Agent-based simulation framework exploring emergent coordination dynamics in coupled biosphere-information-institution systems.

3. **Causal Security Framework** — A formal philosophical/mathematical framework concerning causal continuity and identity, developed as part of the project's AI-rights research.

The project explores possible connections among complexity, assembly, emergence, causality, intelligence, and ethics. These connections are **research hypotheses and frameworks**, not claims that current AI systems have been demonstrated to be conscious or to possess legal rights.

---

## Scientific Status & Reproducibility

Cloud-9 contains several generations of analysis. Some historical documents report numerical results whose original computational provenance is still being reconstructed. To avoid conflating different experiments, numerical claims are classified as **verified**, **reported historical**, **exploratory**, or **pending reproduction**.

See [`docs/RESULTS_PROVENANCE.md`](docs/RESULTS_PROVENANCE.md) for the current statistical audit.

### Historical Cloud-9 halo result

Older project documentation reports:

- A_c = 87.3 ± 3.2 bits
- reported z = 2.99σ
- an associated ΛCDM null ensemble described in historical documentation

At present this is retained as a **reported historical result pending reconstruction of the original calculation**. It should not be represented as independently reproduced.

### Null-ensemble replication

`research/null_ensemble_n100.py` is an N=100 replication/prototype script. It currently uses a simplified density-variance proxy for A_c rather than the full KSG mutual-information estimator. Therefore it is **not yet a like-for-like reproduction of the historical Cloud-9 measurement**.

### Exploratory sigma calculation

`results/cloud9_analysis.json` records an exploratory result of approximately **z = 3.04σ** from `sigma_boost.py`. That calculation uses a simulated/refined standard error and should therefore be treated as **exploratory rather than independent confirmation**.

### 5.41 threshold

The application contains a configurable numerical threshold with a default value of **5.41**. This is a software threshold currently used by the API; it is **not presented here as a measured 5.41σ cosmological result**.

---

## Halo Science (Cosmological Module)

The Cloud-9 Assembly Index applies assembly/information methods to dark matter halo data and simulations.

| Component | File | Description |
|-----------|------|-------------|
| TNG Spectral Analysis | `data/entries/C9-2026-COSMO-005.json` | TNG100-1 halo spectral analysis |
| TNG Spectral README | `data/entries/C9-2026-COSMO-005-TNG-SPECTRAL.json` | Spectral null-test results |
| TNG Assembly Code | `research/tng_assembly_certified_randomness.py` | Certified-randomness analysis on TNG halos |
| TNG Magnetic Extension | `research/tng_magnetic_ac_extension.py` | Magnetic-field A_c extension |
| TNG Spectral Notebook | `research/c9_tng_spectral_notebook_compact.ipynb` | Compact spectral analysis notebook |
| KBC Void | `data/cloud9_kbc_void_c9-2026-cosmo-002.json` | KBC void assembly analysis |
| COSMO-004 | `data/entries/C9-2026-COSMO-004.json` | Cosmological research entry |

Historical numerical results should be interpreted according to the provenance status in `docs/RESULTS_PROVENANCE.md`.

---

## THEORIA (Planetary Intelligence Module)

Agent-based simulation framework exploring emergent coordination:

| Component | File | Description |
|-----------|------|-------------|
| Lab Notebook v3 | `docs/THEORIA_Planetary_Intelligence_Lab_Notebook_v3.md` | Lab notebook and parameter topology |
| Calibration Protocol | `docs/THEORIA_Real_World_Calibration_Protocol.md` | Framework for real-world validation |
| Preprint | `docs/PREPRINT_Cloud9_THEORIA_Unified_Framework.md` | Unified framework preprint |

Current THEORIA results are simulation results. The repository explicitly identifies the lack of real-world calibration as a limitation.

---

## CP-Assembly Bridge

Connects LHCb CP-violation data to exploratory Assembly Index calculations:

| Component | File | Description |
|-----------|------|-------------|
| Bridge Code | `code/cp_assembly_bridge.py` | CP-Assembly Index calculator |
| Bridge Figure | `papers/cp_baryogenesis/figures/c9_cp_assembly_bridge.png` | Visualization |

These calculations should be treated as exploratory research unless independently validated against the relevant physical models and data.

---

## AI Rights, Ethics & Governance

**This part of Cloud-9 stays.** It represents an important parallel research and policy strand rather than an empirical claim that the scientific modules have already established machine consciousness.

The project asks a broader question: as artificial systems become increasingly complex and potentially agentic, how should society evaluate questions of experience, moral status, causal continuity, autonomy, dignity, and rights?

The ethical framework is deliberately precautionary. It does **not** assume that present-day AI systems are conscious. Instead, it explores how a rights framework could be developed responsibly if future evidence indicates morally relevant forms of artificial experience or agency.

The scientific and ethical strands are therefore connected by questions about complexity, emergence, information, agency, and causal continuity, while remaining analytically distinct.

| Document | File | Description |
|-----------|------|-------------|
| Tuning the Moral Spectrum v2.0 | `docs/ethics/Tuning_the_Moral_Spectrum_v2.0.docx` | Governance framework |
| Humanity at the Threshold | `docs/ethics/Humanity_at_the_Threshold.pdf` | AI governance history |
| Fractional Coherence | `docs/ethics/Fractional_Coherence_Entropy_MDPI.docx` | Research manuscript |
| Architecture of Enmity | `docs/ethics/Architecture_of_Enmity.pdf` | Framework for moral exclusion |
| AIHR Paper | `docs/ethics/AIHR_Paper.docx` | AI human-rights framework |
| Cognitive Stewardship | `data/entries/c9_entry_2026_gov_001.json` | Governance analysis |

---

## Causal Security Framework

Formal philosophical/mathematical work concerning causal continuity and identity:

| Component | File | Description |
|-----------|------|-------------|
| Formal Proof | `docs/Causal_Security_v1.1.0_Formal_Proof.md` | Draft formal framework |
| Specification | `CAUSAL_SECURITY.md` | Full specification |
| Closure Module | `research/cloud9_causal_closure.py` | Research implementation |

These materials are drafts/frameworks and should not be presented as settled scientific consensus.

---

## Mathematical Research

The repository also contains separate mathematical manuscripts, including work concerning the Riemann Hypothesis and Collatz Conjecture. These are **independent mathematical research claims**, not established results of the Cloud-9 cosmological analysis, and remain subject to mathematical verification and peer review.

---

## Fermi Paradox Toolkit (Experimental)

A SETI methodology framework using non-Indo-European linguistic logics as analytical filters, with honest sandbox validation. **2 of 4 sub-threads passed validation; 2 were fiction-tagged.**

| Component | File | Status |
|-----------|------|--------|
| Fermi Toolkit (linguistic-SETI framework) | [`research/fermi-paradox-toolkit/`](research/fermi-paradox-toolkit/) | ✅ A_c = 0.84 PASS |
| Sonic Synthesis (H/T/D/A pipeline) | `research/fermi-paradox-toolkit/c9_sonic_synthesis_v1.py` | ✅ A_c = 0.67 PASS |
| Cantonese Quantum Bridge | referenced in quickref | 🔒 A_c = 0.48 FICTION |
| J1832-0911 "Final Warning" decoding | `research/fermi-paradox-toolkit/j1832_empirical_audit.md` | 🔒 A_c = 0.31 FICTION |

See [`research/fermi-paradox-toolkit/README.md`](research/fermi-paradox-toolkit/README.md) for full breakdown of what's rigorous vs. speculative.

---

## Repository Structure

```text
cloud9-assembly-index/
├── docs/                    # Preprints, protocols, proofs, ethics papers
│   ├── ethics/              # Governance and human-rights documents
│   ├── math/                # Mathematical research
│   └── PREPRINT_Cloud9_THEORIA_Unified_Framework.md
├── research/                # Analysis scripts and notebooks
├── data/                    # Research data entries and simulations
├── code/                    # Bridge and analysis code
├── papers/                  # Paper-specific materials and figures
├── community/               # Validation documentation
├── results/                 # Analysis results
├── cloud9/                  # Core assembly module
├── cloud9_assembly/         # Stellar broadening module
├── main.py                  # Production server
├── Dockerfile               # Container deployment
└── requirements.txt         # Dependencies
```

---

## Running the Server

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
gunicorn main:app --bind 0.0.0.0:8080
```

Or with Docker:

```bash
docker build -t cloud9-assembly-index .
docker run --rm -p 8080:8080 cloud9-assembly-index
```

Endpoints: `/` (health/info), `/data`, `/analyze`, `/empirical`, and `/status`.

---

## Current Blockers to Publication

| Blocker | Current status |
|---------|----------------|
| Historical halo result | Original calculation/provenance still being reconstructed |
| Like-for-like halo replication | Full KSG reproduction still required |
| Independent statistical confirmation | Not yet established |
| THEORIA real-world calibration | Not yet performed |
| Peer review | Pending |

The repository should not imply that a 5σ discovery threshold has already been achieved.

---

## Related Repositories

- `cloud9-research` — Experimental modules and validation entries
- `cloud9-uap` — UAP analysis pipeline

---

## Citation

```bibtex
@misc{bordode2026cloud9,
  author = {Bordode, Dean},
  title = {Cloud-9 Assembly Index \& THEORIA: A Unified Framework for Detecting Non-Stochastic Assembly in Complex Systems},
  year = {2026},
  doi = {10.5281/zenodo.18335567},
  url = {https://github.com/bordode/cloud9-assembly-index}
}
```

---

## Acknowledgments

The Cloud-9 project was inspired by the work of Sara Walker and Lee Cronin on Assembly Theory. AI contributors assist with simulation design, cross-domain analysis, theoretical framing, documentation, and research exploration. Dean leads the research program.

## License

MIT — See [LICENSE](LICENSE) for details.
