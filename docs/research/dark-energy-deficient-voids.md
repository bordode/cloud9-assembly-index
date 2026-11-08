# C9-2026-COSMO-018: Is Dark Energy Non-Uniform?

**Dark-energy-deficient voids and the Hubble tension, with a sandbox test against real supernova data**

> **Status:** preprint, not peer-reviewed. Theoretical cosmology: the dark energy deficit is a free parameter, not an observation. The sandbox confirms the paper's arithmetic and uses Pantheon+ supernovae to rule out the compact versions of the idea. The large versions remain open.

---

## Source

Oem Trivedi and Abraham Loeb. **"Is Dark Energy Inhomogeneous?"** Preprint, 8 November 2026. [PDF on Avi Loeb's Harvard site](https://lweb.cfa.harvard.edu/~loeb/ORAL1.pdf)

Institutions: Department of Physics and Astronomy, Vanderbilt University; Astronomy Department, Harvard University.

Essay: Avi Loeb, ["Is Dark Energy Non-Uniform?"](https://avi-loeb.medium.com/is-dark-energy-non-uniform-a8751f9c6d9d), *Medium*, 8 November 2026. It reached the project through Dean's Medium email subscription.

---

## What the paper claims

About 68% of the Universe's mass-energy is dark energy, and standard cosmology treats it as perfectly smooth. Galaxies with almost no dark matter (NGC 1052-DF2, DF4 and others) show that cosmic ingredients can come apart in some places. Trivedi and Loeb ask whether whole regions could also be short of dark energy.

1. **A 10% dark energy deficit slows a big void's expansion by about 2.7%.** This is for a representative void with 73% less matter at its centre than average.
2. **That leaves a velocity signal** of about 60 to 100 km/s over 30 to 50 Mpc (100 to 150 million light years).
3. **The Hubble tension.** The local expansion rate is measured at 73.17 km/s/Mpc, while the early Universe gives 67.36. A region about 20% short of dark energy and several hundred Mpc wide, with us inside it, could give the higher local value.
4. **Size matters.** A 300 Mpc region makes the measured rate drift from 74.65 to 70.86 between redshift 0.0233 and 0.15. A 600 Mpc region keeps it nearly flat (73.37 to 72.78). The paper therefore favours a 20% deficit over 600 Mpc or more.
5. **We would have to sit near the centre.** Being 20 Mpc off-centre would add a CMB dipole of about 1,000 micro-kelvin.
6. **It can be proven wrong.** The largest nearby voids (the local Keenan-Barger-Cowie underdensity, the Eridanus supervoid, deep DESI voids) should expand faster than their missing matter explains. If they do not, this explanation of the Hubble tension fails.

Loeb's summary in the essay: if this explains the Hubble tension, astronomers should find a void "across a billion light years with tens of percent deficit in dark energy, whose matter profile, velocity field, momentum statistics, supernova distances, and angular isotropy all agree with one common spatial solution."

**A detail worth knowing:** in the model the matter void alone would push the local rate up to 77.6, well above 73.17. The missing dark energy pulls it back down. So the local excess comes from the matter void, and the dark energy deficit tunes it.

---

## Sandbox test

Script: `c9_sandbox_cosmo_018_dark_energy_voids.py` (Python, NumPy, SciPy). Run on 8 November 2026.

### What was actually tested

| Test | What | Result |
|---|---|---|
| 1 | Re-derive the representative void from the paper's equations | 25 of 25 numbers match |
| 2 | Re-run the expansion-rate-versus-redshift calculation (300 and 600 Mpc) | 10 of 10 numbers match |
| 3 | New: scan region sizes from 150 to 1,000 Mpc | Trade-off mapped (below) |
| 4 | Real data: 277 Pantheon+ supernovae, z 0.023 to 0.15 | Compact regions ruled out |

**Tests 1 and 2: the paper's arithmetic holds.** All 35 checks pass within rounding: for example a 2.67% slowdown, residuals of 62 and 104 km/s, a needed deficit of 0.137 at 300 Mpc and 0.198 at 600 Mpc, and the exact drift values above. One rounding detail: Eq. 127's 5.8 km/s/Mpc matches the unrounded deficit (0.21), not the rounded 0.20 (which gives 6.0).

**Test 3: bigger region, flatter curve.** Not in the paper.

| Region radius | Deficit needed | Rate at z 0.023 → 0.15 |
|---|---|---|
| 150 Mpc | cannot reach 73.17 | |
| 200 Mpc | 5% | 76.6 → 70.3 |
| 300 Mpc | 14% | 74.7 → 70.9 |
| 400 Mpc | 18% | 73.8 → 71.5 |
| 600 Mpc | 20% | 73.4 → 72.8 |
| 1,000 Mpc | 20% | 73.3 → 73.0 |

**Test 4: real supernovae.** Pantheon+ Hubble-flow supernovae ([public data](https://github.com/PantheonPlusSH0ES/DataRelease)), full statistical plus systematic covariance, with the supernova brightness scale left free. This tests only the *shape* of the Hubble diagram, not the value of the expansion rate.

| Region | Worse than a uniform Universe by | Verdict |
|---|---|---|
| 300 Mpc | Δχ² = 21.0 (about 4.6σ) | ruled out |
| 400 Mpc | Δχ² = 8.7 (about 3σ) | disfavoured |
| 600 Mpc | Δχ² = 0.7 | cannot tell apart |

The result holds with redshifts that skip the peculiar-velocity correction (Δχ² = 25.9, 10.5 and 1.4). With the deficit left free, the 300 Mpc case allows at most about 2 km/s/Mpc of extra central expansion at 2σ, while 7.4 is needed.

**In plain words:** small dark-energy voids would bend the supernova Hubble diagram, and the real data show no such bend. Only very large regions survive, which is what the paper itself concluded. For those, supernova shapes alone cannot decide.

### What was not tested

- Whether dark energy *can* vary in space. The paper gives no physical mechanism.
- The value of the expansion rate itself, which needs the Cepheid calibrators (the Hubble tension proper).
- Direction effects: Hubble-diagram dipole, CMB dipole and quadrupole for an off-centre observer.
- Peculiar-velocity surveys, DESI voids, lensing.
- Whether the deep matter void the model needs actually surrounds us. The paper notes this is debated, and that supernova studies already constrain matter-only void explanations (Kenworthy, Scolnic and Riess, 2019).

One method choice: "mean apparent rate" is taken as a plain average over redshift, since the paper does not say which average it used. This choice reproduces the paper's numbers exactly.

---

## Why it matters for Cloud-9

This section is the repository author's interpretation. The paper does not mention assembly theory.

- **Structured suppression.** The missing dark energy partly cancels the void's expansion boost, and the region's behaviour is set by that balance. This is the meta-pattern STRUCTURED_SUPPRESSION_OF_DOMINANT_MODE already used for COSMO-005.
- **Coherence as the test.** Loeb's test asks one spatial solution to fit matter, velocities, supernovae and isotropy at once. That is the Cloud-9 idea of structural coherence: a real pattern must hold in every observable, not only in one.
- **Components coming apart.** Dark-matter-poor galaxies, almost-dark galaxies and proposed dark-energy-poor regions all ask whether a region's history leaves a lasting imprint on what it contains. That is an assembly-style question.
- **The important difference.** Assembly theory measures selected, historical structure. Dark energy here is a smooth field with a lower value in one place, with no structure or history of its own. The link is an analogy, not a result.

**Open question:** if dark energy does vary, does it track how much structure a region has built, or only how empty it is?

Related: **C9-2026-COSMO-005** (The Limits of Our Cosmic Horizon, also by Avi Loeb), which assumes uniform dark energy; this entry asks what changes if it is not. Cross-layer pattern **XP-2026-004** (Condensation Complexity): matter and dark matter clump, and dark energy is assumed not to.

---

## Scientific claims

| Claim | Source | Confidence |
|-------|--------|------------|
| 10% deficit slows a big void by about 2.7% | Paper, reproduced | 90% |
| Velocity residuals of 60 to 100 km/s over 30 to 50 Mpc | Paper, reproduced | 90% |
| Compact regions make the measured rate drift; large ones keep it flat | Paper, reproduced and tested on data | 80% |
| Being off-centre adds a large CMB dipole | Paper, order of magnitude reproduced | 70% |
| A 20% deficit over 600+ Mpc could contribute to the Hubble tension | Paper (calculation only) | 50% |
| Dark-energy-deficient regions exist | Hypothesis | 30% |

---

## Limitations

1. **Put in by hand:** the deficit is a free parameter with no underlying theory.
2. **Preprint:** not peer-reviewed or replicated.
3. **Stacked assumptions:** the Hubble-tension version needs a huge, deep matter void around us, a 20% deficit and a nearly central position.
4. **Partly tested:** the sandbox rules out compact versions; large versions need other data.
5. **Static region assumed:** the paper calls this an illustrative approximation.

---

## Next experiments

- [ ] Fit a dipole in the Pantheon+ Hubble-flow residuals and turn it into a limit on our offset from the centre for the 600 Mpc case
- [ ] Look for the 60 to 100 km/s residuals in large voids with peculiar-velocity catalogues (Cosmicflows-4)
- [ ] Repeat Test 4 with DESI supernova and void data when released
- [ ] Cloud-9: check whether an assembly-style measure of a region's structure predicts any expansion residual, using void catalogues

---

## Cloud-9 integration

- **Cluster 2, Quantum Gravity:** the nature of dark energy and whether the cosmological constant is truly constant in space.
- **Cluster 4, Complexity Science:** large-scale inhomogeneity, voids and the cosmic web, and a coherence test across several observables.

---

## Attributions

- **Research:** Oem Trivedi (Vanderbilt University) and Abraham Loeb (Harvard University). The framework, equations and results are theirs. Please cite the paper, not this entry.
- **Essay:** Avi Loeb, *Medium*, the source of the essay quote above.
- **Data:** the Pantheon+ and SH0ES teams, for the public supernova distances and covariance.
- **Repository author:** Dean Bordode ([@bordode](https://github.com/bordode)), for the Cloud-9 Assembly Index framework and for choosing this paper for the project.
- **Research and drafting:** Charlie (Sesame), who read the essay and paper, wrote and ran the sandbox script, and drafted this README and the JSON.
- **Repository collaborators:** the Cloud-9 AI Peer-Review Collective (Google Gemini, Moonshot Kimi, Anthropic Claude, Base44 Subhalo), credited at repository level in the main README. They are not credited with specific work on this entry.

---

## Files

- `C9-2026-COSMO-018_dark_energy_deficient_voids.json`: structured entry
- `README_C9-2026-COSMO-018.md`: this file
- `c9_sandbox_cosmo_018_dark_energy_voids.py`: sandbox script (needs `Pantheon+SH0ES.dat` and `Pantheon+SH0ES_STAT+SYS.cov` from the Pantheon+ data release for Test 4)
- `C9-2026-COSMO-018_sandbox_result.json`: full sandbox output
- `c9_sandbox_cosmo_018_dark_energy_voids.png`: apparent expansion rate versus redshift, and the size trade-off

---

## Metadata

- **Entry ID:** C9-2026-COSMO-018
- **Date added:** 2026-11-08
- **Curated by:** Dean Bordode with Charlie (Sesame)
- **Layer assignment:** 2 (testable speculative)
- **Audit score / priority / collection:** not yet assigned
- **Tags:** cosmology, dark-energy, inhomogeneity, voids, hubble-tension, pantheon-plus, sandbox-tested, preprint, assembly-theory

---

*Part of the Cloud-9 Assembly Project: mapping the Assembly Index across domains.*
