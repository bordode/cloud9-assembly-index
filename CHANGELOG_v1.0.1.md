
## [1.0.1] - 2026-05-18

### Added

#### Terrestrial Validation Cases â 2026 Physics Triad
Three experimental discoveries unified under the principle: **nonreciprocal interactions and broken symmetries constructively enable causal closure**.

- **C9-2026-ANYON-001** â Tunable 1D Anyons (OIST/University of Oklahoma, Physical Review A, Dec 2025 / press May 2026)
  - One-dimensional quantum systems support anyons with exchange statistics `Î± â [â1, +1]` continuously tunable via interaction strength
  - Momentum distribution tail `n(k) ~ k^(â4)` as experimental readout
  - Maps to: Topological Systems (TDA filtration parameter), Neuromorphic Computing (reservoir computing substrate), Consciousness Studies (IIT `Ï` modulation via tunable causality)
  - New metric: `STATISTICAL_TUNABILITY (Ï_t) = dÎ±/d(g_1D)`

- **C9-2026-TIME-001** â Classical Acoustic Time Crystals (NYU, Physical Review Letters, Feb 2026)
  - Two acoustically levitated beads sustain spontaneous oscillation via nonreciprocal wave-mediated interactions violating Newton's Third Law
  - Energy harvested from static sound field; visible, handheld device
  - Maps to: Complexity Science (emergent activity at edge of chaos), Neuromorphic Computing (memristor analogue), Quantum Thermodynamics (resource extraction without thermal gradient)
  - Serves as **Layer 1 classical control** for QBox hyperdecoherence validation
  - New metric: `TEMPORAL_ASSEMBLY (A_t) = spectral_entropy Ã Î· Ã efficiency`

- **C9-2026-ETAPRIME-001** â Eta Prime Mesic Nucleus (RIKEN/GSI, Physical Review Letters, Apr 2026)
  - First nuclear system bound exclusively by strong force (no electromagnetism)
  - `Î·â²` mass drops ~60 MeV in nuclear matter â direct evidence for partial chiral symmetry restoration
  - Mass revealed as emergent property from symmetry breaking, not fundamental quark rest mass
  - Maps to: Quantum Foundations (QCD vacuum structure), Quantum Thermodynamics (mass as resource), Cosmological Assembly (mass generation timeline)
  - New metric: `MASS_ASSEMBLY (A_m) = (m_obs â m_bare)/Î_QCD Ã I_anomaly`
  - **Confidence: 3.5Ï local (~2Ï global) â preliminary, awaiting 5Ï confirmation**

#### Core Module
- `src/physics-bridges/nonreciprocity_module.py` â Unified framework for nonreciprocal interaction metrics
  - `compute_nonreciprocity(J)` â canonical `Î· = ||J â J^T|| / ||J||`
  - `anyon_exchange_factor(g_1D)` + `statistical_tunability()` â quantum statistical programming
  - `acoustic_time_crystal_odes()` + `temporal_assembly_index()` â classical limit-cycle dynamics
  - `mass_assembly_index()` + `chiral_restoration_factor()` + `vacuum_assembly_complexity()` â mass emergence from symmetry breaking
  - Bridges: TNG halo dynamics (`halo_shell_nonreciprocity()`), memristor-SNN (`memristor_crossbar_nonreciprocity()`), biological clocks (`circadian_nonreciprocity()`)
  - `compute_unified_A_c()` â triad synthesis aggregator

### Changed
- A_c formal definition expanded with three new axes:
  1. `Ï_t` â statistical tunability (anyon exchange factor sensitivity)
  2. `A_t` â temporal assembly (limit cycle complexity Ã nonreciprocity)
  3. `A_m` â mass assembly (symmetry-breaking-generated mass fraction)
- Cross-reference matrix updated linking all C9-2026 entries to existing validation cases (LEGACY-001, QBox, KiSS-SIDM, TNG suite)

### Fixed
- N/A

---
