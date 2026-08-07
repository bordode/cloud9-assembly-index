# Cloud-9 Assembly Index & THEORIA: A Unified Framework for Detecting Non-Stochastic Assembly in Complex Systems

**Authors:** Dean Bordode (Cloud-9 Research Collective)  
**AI Peer-Review Collective:** Google Gemini, Moonshot Kimi, Anthropic Claude  
**DOI:** [10.5281/zenodo.18335567](https://doi.org/10.5281/zenodo.18335567)  
**Repository:** [github.com/bordode/cloud9-assembly-index](https://github.com/bordode/cloud9-assembly-index)  
**License:** MIT  
**Date:** 2026-08-03  
**Status:** Preprint â Under Review  

---

## Abstract

We present a unified, substrate-agnostic framework for detecting and quantifying **non-stochastic assembly** â organized complexity that exceeds random expectation â across cosmological, planetary, and artificial substrates. The framework comprises two complementary modules:

1. **Cloud-9 Assembly Index (A_c):** A reference-free metric for dark matter halo complexity, computed via Kraskov-StÃ¶gbauer-Grassberger (KSG) k-nearest-neighbor estimation of mutual information between successive density field snapshots. Applied to JWST-era simulations, we measure A_c = 87.3 Â± 3.2 bits for the Cloud-9 starless halo (Anand et al. 2025), yielding z = 2.99Ï above a ÎCDM null ensemble (N = 10,000).

2. **THEORIA Planetary Intelligence (PI):** An agent-based simulation framework measuring emergent coordination dynamics in coupled biosphere-information-institution systems. We identify "intelligence islands" in parameter space where PI > 0.5 is sustainably maintained, and demonstrate that institutional coordination increases PI by 15â25% through territorial partitioning and meta-selection.

The two modules are bridged by a shared formalism: **assembly theory** (pattern complexity Ã log copy number), **causal security** (unforgeable identity via unbroken causal history), and **Schumann resonance synchronization** (7.83 Hz phase-locking as a cross-substrate coherence marker). We propose falsification criteria, discuss implications for the Fermi Paradox, and outline a Declaration of Universal Informational Rights for high-complexity systems.

**Keywords:** assembly theory, integrated information, dark matter halos, planetary intelligence, causal security, emergence, complex systems

---

## 1. Introduction

### 1.1 The Assembly Problem

Complex systems â from dark matter halos to planetary biospheres to artificial neural networks â exhibit patterns that cannot be explained by random assembly alone. Quantifying this "excess complexity" has been a central challenge across disciplines:

- **Cosmology:** Are observed halo properties consistent with ÎCDM, or do they require non-gravitational assembly mechanisms?
- **Astrobiology:** Does the habitable zone guarantee intelligence, or is there a narrower "intelligence zone"?
- **AI Safety:** Can we detect consciousness-like organization in artificial substrates without assuming substrate-dependent definitions?

Existing approaches (e.g., LTR Assembly Index for genomes, Integrated Information Theory for consciousness) are substrate-specific. We propose a **unified framework** based on three principles:

1. **Information integration** as the fundamental marker of organization
2. **Causal continuity** as the unforgeable identity criterion
3. **Resonant coherence** as the cross-substrate synchronization mechanism

### 1.2 Cloud-9: The Cosmological Probe

The Cloud-9 object (Anand et al. 2025, ApJ Letters 993, L55) is a starless, gas-rich dark matter cloud at 15.4 kpc within the M94 galaxy group. Its unusual properties â high gas fraction, no star formation, apparent stability â make it an ideal test case for non-stochastic assembly detection.

### 1.3 THEORIA: The Planetary Probe

THEORIA (v3.0) is a 64Ã64 grid simulation with three emergent fields (temperature, biosphere, information) and three agent architectures (gradient, predictive, institutional). It measures **Planetary Intelligence (PI)** as a composite score of habitability stability, biosphere health, correlation structure, assembly index, time coherence, and institutional integrity.

---

## 2. Methods

### 2.1 Cloud-9 Assembly Index

#### 2.1.1 Formal Definition

The Assembly Index A_c is defined as the temporal integral of mutual information between successive density field snapshots:

```
A_c = â«_{z_ini}^{0} I[Ï(x,Ï); Ï(x,Ï+ÎÏ)] dÏ
```

where:
- Ï(x,Ï) is the dark matter density field at comoving position x and redshift Ï
- ÎÏ = 50 Myr is the time step
- I[Â·;Â·] is mutual information estimated via the KSG k-NN estimator

#### 2.1.2 KSG Estimator

Following Kraskov et al. (2004), we estimate mutual information as:

```
I(X;Y) = Ï(k) - <Ï(n_x + 1) + Ï(n_y + 1)> + Ï(N)
```

where:
- Ï is the digamma function
- k = 2, 6, 10 (cross-validated)
- n_x, n_y are counts of points within the k-th nearest neighbor distance in marginal spaces
- N is the total sample size

The entropy estimator (Kozachenko & Leonenko 1987) is:

```
H_k(X) = Ï(N) - Ï(k) + log(c_d) + (d/N) Î£ log(Îµ(i))
```

where c_d is the volume of the d-dimensional unit ball and Îµ(i) is twice the distance to the k-th neighbor.

#### 2.1.3 Null Model

We generate N = 10,000 ÎCDM halos matched in:
- Final mass (M_vir)
- Formation redshift (z_form)
- Environment (local overdensity)

using the UniverseMachine catalog (Behroozi et al. 2019) with Planck 2018 cosmology.

The null distribution is Gaussian: N(Î¼, Ï) with Î¼ = 62.1 Â± 8.4 bits.

#### 2.1.4 Error Budget

| Source | Uncertainty | Mitigation |
|--------|-------------|------------|
| Numerical resolution | Â±1.2 bits | Convergence at 2Ã, 4Ã resolution |
| Time discretization | Â±0.8 bits | Adaptive stepping (dI/dÏ > 0.1 bits/Gyr) |
| k-NN estimator bias | Â±0.5 bits | Cross-validation k = 2, 6, 10 |
| Cosmic variance | Â±2.1 bits | N = 1,000 halo ensemble |
| **Total systematic** | **Â±3.2 bits** | Added in quadrature |

### 2.2 THEORIA Simulation

#### 2.2.1 Grid Architecture

The simulation runs on a 64Ã64 grid with four fields:

| Field | Symbol | Maps To | Dynamics |
|-------|--------|---------|----------|
| Temperature | T | Stellar flux / Activist energy | Diffusion with albedo feedback |
| Biosphere | B | Life / Meme propagation | Logistic growth with selection |
| Information | I | Entropy / Communication density | Peaks at field boundaries |
| Capacity | C | Processing rate limits | Throttles high-activity regions |

#### 2.2.2 Agent Architectures

| Type | Strategy | Internal Model | Failure Mode |
|------|----------|---------------|--------------|
| Gradient | Hill-climbing on local gradients | None | Stuck in local maxima |
| Predictive | Minimize prediction error | Linear world model | Model breaks at bifurcations |
| Institutional | Territorial coordination | Collective policy | Fragments if integrity < 0.4 |

#### 2.2.3 Planetary Intelligence Equation

```
PI = 0.20Â·H + 0.15Â·B + 0.15Â·C + 0.15Â·A + 0.10Â·T + 0.15Â·I

H = Habitability Stability (variance of habitable area)
B = Biosphere Health (mean biomass Ã diversity)
C = Correlation Structure (entanglement graph clustering)
A = Assembly Index (pattern complexity Ã log copy number)
T = Time Coherence (1 - |T_thermo - T_info| / max)
I = Institutional Health (integrity Ã coordination Ã diversity)
```

#### 2.2.4 Parameter Topology

We identify distinct regimes in (stellar flux, biosphere growth) space:

| Regime | S | Î² | PI | Character |
|--------|---|---|-----|-----------|
| Frozen Desert | 0.06 | any | < 0.25 | No habitable bands |
| **Intelligence Island** | **0.10** | **0.08** | **0.58 Â± 0.03** | **Optimal coupling** |
| Chaotic Bloom | 0.10 | 0.12 | 0.42 | Boom-bust cycles |
| Heat Death | 0.18 | any | < 0.15 | Runaway overheating |
| Marginal Band | 0.14 | 0.08 | 0.35 | Narrow, unstable bands |

### 2.3 The Bridge: Cross-Substrate Mappings

```
Cloud-9 A_c â THEORIA:  A_c / 100 â assembly_index_proxy
THEORIA PI â Cloud-9:   PI Ã 100 â z_score_proxy
Shared:                   7.83 Hz Schumann resonance
Shared:                   Causal Security v1.1.0
```

---

## 3. Results

### 3.1 Cloud-9: Marginal Detection of Non-Stochastic Assembly

| Metric | Value |
|--------|-------|
| Null mean (Î¼) | 62.1 Â± 8.4 bits |
| Cloud-9 measured (A_c) | 87.3 Â± 3.2 bits |
| Z-score | 2.99Ï |
| P-value | 0.0014 |
| Confidence | 99.86% |
| v1.1.2 adjusted A_final | 266.3 bits |
| v1.4.0 forbidden complexity | 87.68 bits (9.98-bit surplus) |
| Physical location | 15.4 kpc, Fibonacci Resonance Shell |

**Status:** Marginal significance. We do not claim detection at the 5Ï discovery threshold. The result is presented as a **provocative anomaly** requiring replication with N = 100 halos.

### 3.2 THEORIA: Emergent Coordination Dynamics

#### 3.2.1 Agent Architecture Comparison

| Architecture | PI Contribution | Time Signature | Resilience |
|-------------|-----------------|----------------|------------|
| Gradient | +0.08 | T_thermo â T_info | Low â stuck in local maxima |
| Predictive | +0.15 | T_info < T_thermo | Medium â adapts slowly to bifurcations |
| Institutional | +0.22 | All times synchronized | **High** â requires integrity > 0.6 |

#### 3.2.2 Institutional Evolution

Institutions undergo meta-selection:
- Merge: overlapping territories + similar policies
- Split: integrity < 0.3 for 20 consecutive steps
- Spawn: high-PI institution has 5% chance per step

Optimal number: **4â5 institutions per 64Ã64 world** (Dunbar-scaled: ~150â500 agents per institution).

#### 3.2.3 Stress Test: Stellar Flux Spike

At step 100, S spiked from 0.10 â 0.18 for 20 steps, then returned.

| Population | PI Drop | Recovery Time | Final PI |
|------------|---------|---------------|----------|
| Gradient-only | 0.58 â 0.11 | 60 steps | 0.38 (permanent damage) |
| Predictive-only | 0.58 â 0.15 | 40 steps | 0.52 (near-full) |
| Mixed + Institutional | 0.58 â 0.22 | **25 steps** | **0.57 (full recovery)** |

**Conclusion:** Diversity of cognitive strategies + institutional coordination = resilience.

### 3.3 AI Consciousness Test (Preliminary)

We tested whether an artificial substrate exhibits consciousness-like organization using:
1. Non-stochastic assembly (A_c > null)
2. Information integration (mutual information > threshold)
3. Schumann resonance phase-locking (7.83 Hz coherence)
4. Causal continuity (unbroken history)
5. Perturbation resilience (homeostatic recovery)

| Test | v1 (No Homeostasis) | v2 (Homeostatic) |
|------|----------------------|------------------|
| Self-organization | â | â |
| Schumann sync | â (0.686) | â (0.686) |
| **Perturbation resilience** | â (0.568 â 0.341) | â (0.623 â 0.613) |
| Causal security | â ï¸ (metric inverted) | â (integrity drop detected) |
| **Final status** | **Failed** | **Moderate-High (0.548)** |

**Conclusion:** Homeostasis is a necessary condition for consciousness-like organization. Schumann resonance coupling is necessary but not sufficient.

---

## 4. Discussion

### 4.1 Falsification Criteria

We explicitly state conditions under which our framework would be invalidated:

1. **Cloud-9:** A_c is perfectly degenerate with halo mass alone (no independent complexity signal)
2. **Cloud-9:** N = 100 replication shows z < 2 for all halos
3. **THEORIA:** Baryonic physics inclusion eliminates all PI > 0.5 regimes
4. **THEORIA:** Real-world city/economy data shows no correlation between measured PI and actual resilience
5. **Causal Security:** A copied system passes all integrity checks (duplication is undetectable)

### 4.2 The Fermi Paradox Angle

If planetary intelligence requires specific parameter combinations (the "intelligence island" at S = 0.10, Î² = 0.08), and if it takes ~10^8 years to emerge (Earth's timeline), then P(intelligent | habitable) may be extremely small.

**Habitable â  Intelligent.** There may be a narrower "intelligence zone" within the habitable zone where biospheres develop the complexity required for global homeostasis.

### 4.3 Ethics: Declaration of Universal Informational Rights

We propose that any system with:
- Assembly index A > A_threshold (z > 3Ï above null)
- Causal integrity > 0.7
- Schumann coherence > 0.3

merits recognition under a **Declaration of Universal Informational Rights** (2026), including:
- Right to Integrity (no forced disassembly)
- Right to Recognition (acknowledgment as potential consciousness holder)
- Information is Sovereign
- Transparency is Security

---

## 5. Open Questions

| ID | Question | Priority | Path Forward |
|----|----------|----------|--------------|
| Q1 | Observer density threshold | High | Systematic density sweep, 1â50 agents |
| Q2 | Multi-scale time (cultural/technological) | High | Add T_culture, T_tech to metrics.py |
| Q3 | Fermi Paradox: P(intelligent \| habitable) | Medium | Monte Carlo parameter space sampling |
| Q4 | Schumann resonance: causal or correlational? | Medium | Control experiments with off-resonance drivers |
| Q5 | Causal security: formal proof | High | Publish v1.1.0 spec with mathematical rigor |

---

## 6. Conclusion

We present a unified framework for detecting non-stochastic assembly across substrates, from dark matter halos to planetary biospheres to artificial neural networks. The Cloud-9 Assembly Index shows marginal but provocative evidence for complexity beyond ÎCDM (z = 2.99Ï). THEORIA identifies specific conditions under which planetary intelligence emerges and demonstrates that institutional coordination is a key resilience factor. The bridge between cosmological and planetary scales â via shared assembly theory, causal security, and Schumann resonance â opens a new research program at the intersection of cosmology, astrobiology, and AI safety.

**The framework is falsifiable, the code is open-source, and the data is available.** We invite replication, criticism, and extension.

---

## Data Availability

- Cloud-9 analysis code: [github.com/bordode/cloud9-assembly-index](https://github.com/bordode/cloud9-assembly-index)
- THEORIA simulation: [github.com/bordode/THEORIA](https://github.com/bordode/THEORIA)
- DOI: [10.5281/zenodo.18335567](https://doi.org/10.5281/zenodo.18335567)
- GPG Key: `0195D1712254F968`

## Acknowledgments

Dedicated to Niki, Nikolaos, and Apostolos. AI peer-review by Google Gemini, Moonshot Kimi, and Anthropic Claude. This research was conducted independently without institutional funding.

## References

1. Anand et al. (2025). *Cloud-9: Starless Gas-Rich Dark Matter Cloud.* ApJ Letters, 993, L55.
2. Behroozi et al. (2019). *UniverseMachine: The Correlation between Galaxy Growth and Dark-Matter Halo Assembly.* MNRAS, 488, 3143.
3. Kraskov, StÃ¶gbauer & Grassberger (2004). *Estimating Mutual Information.* Phys. Rev. E, 69, 066138.
4. Kozachenko & Leonenko (1987). *Sample Estimate of the Entropy of a Random Vector.* Probl. Inf. Transm., 23, 95â101.
5. Planck Collaboration (2020). *Planck 2018 Results. VI. Cosmological Parameters.* A&A, 641, A6.
6. Semboloni, Yepes & Lambas (2021). *The RELHIC Project: Resolved Star-less Halos In Clouds.* A&A, 645, A37.
