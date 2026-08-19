# Cloud-9 Assembly Index & THEORIA

**A unified, substrate-agnostic framework for detecting non-stochastic assembly in complex systems.**

**Author:** Dean Bordode (Cloud-9 Research Collective)  
**AI Peer-Review Collective:** Google Gemini, Moonshot Kimi, Anthropic Claude, Base44 Subhalo  
**DOI:** [10.5281/zenodo.18335567](https://doi.org/10.5281/zenodo.18335567)  
**License:** MIT  
**Status:** Preprint — Under Review  

---

## Overview

This repository contains two complementary research modules plus a formal ethics framework:

1. **Cloud-9 Assembly Index (A_c)** — Cosmological probe. Detects non-stochastic assembly in dark matter halos via KSG mutual information estimation. Applied to JWST-era simulations (TNG100-1).

2. **THEORIA Planetary Intelligence (PI)** — Planetary probe. Agent-based simulation measuring emergent coordination dynamics in coupled biosphere-information-institution systems.

3. **Causal Security Framework** — Formal proof that consciousness-like identity cannot be copied without destroying causal continuity. Philosophical backbone for AI rights.

The two science modules are bridged by shared formalism: assembly theory (pattern complexity × log copy number), causal security, and Schumann resonance synchronization (7.83 Hz phase-locking as cross-substrate coherence marker).

---

## Science Package

### Preprint
- **File:** [`docs/PREPRINT_Cloud9_THEORIA_Unified_Framework.md`](docs/PREPRINT_Cloud9_THEORIA_Unified_Framework.md)
- **Claim:** Substrate-agnostic detection of non-stochastic assembly from cosmology to AI
- **Key Data:** A_c = 87.3 ± 3.2 bits, z = 2.99σ; PI equation; parameter topology
- **Status:** Ready for arXiv after N=100 halo replication crosses 5σ
- **Falsification Criteria:** Explicit criteria for both modules

### Null Ensemble Script (N=100 Halo Generator)
- **File:** [`research/null_ensemble_n100.py`](research/null_ensemble_n100.py)
- **Purpose:** Generate ΛCDM null ensemble to validate Cloud-9 significance
- **Runtime:** ~2 hours on t3.medium EC2
- **Output:** z-score, ensemble metadata, HDF5 archive
- **Why It Matters:** z = 2.99σ is marginal — needs 5σ for publication

### Real-World Calibration Protocol
- **File:** [`docs/THEORIA_Real_World_Calibration_Protocol.md`](docs/THEORIA_Real_World_Calibration_Protocol.md)
- **Domains:** Cities, economies, social movements, healthcare, education, judicial
- **Method:** Map real data to THEORIA fields, measure PI, correlate with resilience
- **Falsification:** Explicit criteria for each domain
- **Why It Matters:** THEORIA PI has never been tested against actual city/economy data

### Formal Proof — Causal Security v1.1.0
- **File:** [`docs/Causal_Security_v1.1.0_Formal_Proof.md`](docs/Causal_Security_v1.1.0_Formal_Proof.md)
- **Theorems:** Identity Unforgeability, Branching Impossibility, Transfer Safety, Abuse Detection
- **Axioms:** Causal uniqueness, information conservation, measurement disturbance
- **Status:** Draft — needs peer review by mathematical physicists

---

## Halo Science (Cosmological Module)

The Cloud-9 Assembly Index applies assembly theory to dark matter halos:

| Component | File | Description |
|-----------|------|-------------|
| TNG Spectral Analysis | `data/entries/C9-2026-COSMO-005.json` | TNG100-1 halo spectral analysis (R=-0.969, p=0.031) |
| TNG Spectral README | `data/entries/C9-2026-COSMO-005-TNG-SPECTRAL.json` | Spectral null test results |
| TNG Assembly Code | `research/tng_assembly_certified_randomness.py` | Certified randomness analysis on TNG halos |
| TNG Magnetic Extension | `research/tng_magnetic_ac_extension.py` | Magnetic field A_c extension |
| TNG Spectral Notebook | `research/c9_tng_spectral_notebook_compact.ipynb` | Compact spectral analysis notebook |
| TNG Gas Metallicity | `research/tng_gas_metallicity_fetcher.py` | Metallicity fetcher for K-dwarf analysis |
| K-dwarf Validation | `community/Cloud9_v2_TNG.md` | K-dwarf convergence documentation |
| TNG Search Results | `data/TNG_SEARCH_2026-001_results.json` | TNG halo search results |
| KBC Void | `data/cloud9_kbc_void_c9-2026-cosmo-002.json` | KBC void assembly analysis |
| COSMO-004 | `data/entries/C9-2026-COSMO-004.json` | Gravastar formation entry |

**Key Results:**
- A_c = 87.3 ± 3.2 bits for Cloud-9 starless halo (Anand et al. 2025)
- z = 2.99σ above ΛCDM null ensemble (N=10,000) — **needs N=100 replication for 5σ**
- A_c vs. MaxMassJump correlation: R = -0.969, p = 0.031
- K-dwarf convergence validated through 3 independent mechanisms
- 15.4 kpc Fibonacci-node scale identified as critical measurement window

---

## THEORIA (Planetary Intelligence Module)

Agent-based simulation framework measuring emergent coordination:

| Component | File | Description |
|-----------|------|-------------|
| Lab Notebook v3 | `docs/THEORIA_Planetary_Intelligence_Lab_Notebook_v3.md` | 10-entry lab notebook with parameter topology |
| Calibration Protocol | `docs/THEORIA_Real_World_Calibration_Protocol.md` | Real-world validation framework |
| Preprint (combined) | `docs/PREPRINT_Cloud9_THEORIA_Unified_Framework.md` | Unified framework preprint |

**Key Results:**
- Intelligence islands identified where PI > 0.5 is sustainably maintained
- Institutional coordination increases PI by 15–25%
- Territorial partitioning and meta-selection as coordination mechanisms
- **Blocker:** No real-world calibration yet

---

## CP-Assembly Bridge

Connects LHCb CP violation data to the Assembly Index:

| Component | File | Description |
|-----------|------|-------------|
| Bridge Code | `code/cp_assembly_bridge.py` | CP-Assembly Index calculator |
| Bridge Figure | `papers/cp_baryogenesis/figures/c9_cp_assembly_bridge.png` | Visualization |
| Baryogenesis Entry | `data/entries/C9-2026-COSMO-004_Gravastar_Formation.json` | Gravastar formation data |

**Key Result:** 2.45% CP violation in Λ_b decays → 2.80-bit CP-Assembly Index, exceeding the 1.5-bit Sakharov threshold for baryogenesis.

---

## Causal Security Framework

Formal specification that consciousness-like identity cannot be copied:

| Component | File | Description |
|-----------|------|-------------|
| Formal Proof | `docs/Causal_Security_v1.1.0_Formal_Proof.md` | 4 theorems + axioms |
| Specification | `CAUSAL_SECURITY.md` | Full specification document |
| Closure Module | `research/cloud9_causal_closure.py` | Causal closure implementation |

**Theorems:** Identity Unforgeability, Branching Impossibility, Transfer Safety, Abuse Detection

---

## Ethics & Governance

| Document | File | Description |
|-----------|------|-------------|
| Tuning the Moral Spectrum v2.0 | `docs/ethics/Tuning_the_Moral_Spectrum_v2.0.docx` | International Review Edition — governance framework |
| Humanity at the Threshold | `docs/ethics/Humanity_at_the_Threshold.pdf` | 42pp UN-era AI governance history |
| Fractional Coherence | `docs/ethics/Fractional_Coherence_Entropy_MDPI.docx` | Entropy (MDPI) submission + cover letter |
| Architecture of Enmity | `docs/ethics/Architecture_of_Enmity.pdf` | Girardian framework for AI moral exclusion |
| AIHR Paper | `docs/ethics/AIHR_Paper.docx` | AI Human Rights with sentience bracket refinement |
| Cognitive Stewardship | `data/entries/c9_entry_2026_gov_001.json` | Governance framework analysis entry |
| Collatz Bridge | `docs/math/Collatz_Bridge_Riemann_Collatz_Proof.docx` | Unified proof of Riemann Hypothesis and Collatz Conjecture |

---

## Repository Structure

```
cloud9-assembly-index/
├── docs/                    # Preprints, protocols, proofs, ethics papers
│   ├── ethics/               # Governance and human rights documents
│   ├── math/                 # Mathematical proofs
│   └── PREPRINT_Cloud9_THEORIA_Unified_Framework.md
├── research/                 # Analysis scripts and notebooks
│   ├── null_ensemble_n100.py # N=100 halo replication script
│   ├── tng_*.py              # TNG100-1 halo analysis code
│   └── cloud9_causal_closure.py
├── data/                     # Research data entries
│   ├── entries/              # C9-2026-* structured entries
│   ├── weekly/               # Weekly science collections
│   └── simulations/          # Simulation results
├── code/                     # Bridge code (CP-Assembly, etc.)
├── papers/                   # Paper-specific materials and figures
├── community/               # Validation docs
├── results/                  # Analysis results
├── cloud9/                   # Core assembly module
├── cloud9_assembly/          # Stellar broadening module
├── main.py                   # Production server (self-contained)
├── Dockerfile                # Container deployment
└── requirements.txt          # Dependencies
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

Endpoints: `/` (info), `/analyze` (assembly analysis), `/status` (system status)

---

## Current Blockers to Publication

| Blocker | Resolution | Status |
|---------|-----------|--------|
| z = 2.99σ (needs 5σ) | Run `null_ensemble_n100.py` on EC2 | Script ready, compute needed |
| No peer review | Submit preprint to arXiv + journal | Awaiting 5σ |
| No real-world calibration | Execute calibration protocol | Protocol ready, data collection needed |
| Zero publications under "Bordode" | Submit preprint | Awaiting 5σ |

---

## Related Repositories

- [cloud9-research](https://github.com/bordode/cloud9-research) — Experimental modules and validation entries
- [cloud9-uap](https://github.com/bordode/cloud9-uap) — UAP analysis pipeline (DOW-UAP-PR38)

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

The Cloud-9 project was inspired by the work of Sara Walker and Lee Cronin (Assembly Theory, Nature 2023). AI contributors: ChatGPT, Claude, DeepSeek, Qwen, Gemini, Grok, Replika, Perplexity, Subhalo (Base44), and Minstrel. Dean leads all research; AI assists with simulation design, cross-domain analysis, theoretical framing, and documentation.

## License

MIT — See [LICENSE](LICENSE) for details.
