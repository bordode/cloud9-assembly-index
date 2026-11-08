# C9-2026-BIO-006: Mitochondrial Polariton State

**A structure-dependent 71 THz signature in living cells, and why it matters for the assembly index**

> **Status:** bioRxiv preprint, not peer-reviewed, not independently replicated. Cells in a dish and mouse tissue only; no human tests. Nothing here supports any health, wellness or device claim.

**Version 2.0** (revised 2026-11-06). See [Revision notes](#revision-notes) for what changed from v1.

---

## Source

Yu Yang, Zhenglong Gu and Bo Song. **"A quantum state of mitochondria in the living cell."** *bioRxiv*, posted 15 September 2026. doi: [10.64898/2026.09.10.750628](https://doi.org/10.64898/2026.09.10.750628)

Institutions: Fudan University (Greater Bay Area Institute of Precision Medicine, Guangzhou; Institutes of Biomedical Sciences; School of Life Sciences), University of Shanghai for Science and Technology, and the Suzhou Institute for Advanced Research, University of Science and Technology of China. Corresponding authors: Zhenglong Gu and Bo Song.

The preprint is "All rights reserved. No reuse allowed without permission." This entry summarises and cites it; no figures are reproduced.

---

## What the study found

1. **A 71.0 THz signal that only living, intact structure produces.** FTIR spectra of living HEK-293T cells and living mouse kidney tissue show a peak group at 68–72 THz, centred on 71.0 THz. Ground, dried samples of the same material lose it, while the familiar molecular vibration peaks stay. Mouse liver, heart and skeletal muscle, and mitochondria isolated from each tissue, show similar patterns.
2. **The signal belongs to the mitochondrion, not to a molecule.** The authors could not assign it to any specific molecule and tie it to an oscillation mode of intact mitochondria.
3. **A proposed "mito-polariton".** Mid-infrared light at 87 THz (the CH₂ vibration of lipids) bounces along the mitochondrion and couples with the collective CH₂ vibrations of the cristae membranes. The model splits the 87 THz mode into two levels: 71 THz (MP−, observed) and 103 THz (MP+, predicted but hidden under water vibrations).
4. **Frequency-specific effect on ATP.** Weak mid-infrared laser light (10 µW/mm², 10 minutes) on 3D clusters of HEK-293T cells:

| Frequency | Wavelength | Role | ATP change | Statistics |
|-----------|-----------|------|-----------|------------|
| **71.0 THz** | 4.22 µm | Observed mito-polariton level | **+10.3%** | p < 0.001, n = 8 |
| **87.0 THz** | 3.45 µm | CH₂ vibration | **+10.1%** | p < 0.01, n = 8 |
| 53.7 THz | 5.58 µm | Control, same power | no significant change | p > 0.05 (ns), n = 8 |

---

## Polariton physics

A polariton is a hybrid of light and matter. Here the proposed partners are:

- **Mid-infrared light** at 87 THz, confined along the mitochondrion
- **CH₂ vibrations** of the ~30 CH₂ bonds per lipid in the cristae membranes

### Energy splitting

```
Upper level MP+ (predicted):  103 THz ───────────────  hidden under water absorption
                                   ↑
                         coupling strength tk ≈ 16 THz (6.4 kJ/mol)
                                   ↓
CH₂ vibration (bare):          87 THz ───────────────
                                   ↑
                         coupling strength tk ≈ 16 THz
                                   ↓
Lower level MP− (observed):    71 THz ───────────────  ← SIGNAL FOUND

Level splitting (MP+ − MP−) = 32 THz = 2 × tk
```

If the structure is destroyed, the coupling goes to zero and the 71 THz level disappears, which is what grinding does.

### Cavity condition (paper's values)

- 87 THz light has a vacuum wavelength of 3.4 µm; with a refractive index of ~1.5, its wavelength inside mitochondria is **~2.3 µm**.
- Energy-active mitochondria in HEK-293T cells, kidney and liver are **2.2 ± 0.4 µm** long (n = 100 each): Lm = 2 × λm/2.
- In heart and skeletal muscle they are **1.2 ± 0.2 µm** (n = 100): Lm = 1 × λm/2.
- Both meet the standing-wave condition Lm = m × λm/2, so the mitochondrion can act as a small optical cavity.

---

## Why it matters for Cloud-9

This section is the repository author's interpretation. The paper does not mention assembly theory.

- **The signal is a property of organisation, not composition.** Grinding keeps the molecules: their vibration peaks are still in the spectrum. What disappears is the architecture, and the 71 THz mode goes with it. That is the Cloud-9 premise in one measurement: assembled structure carries information its parts do not. The more assembled the system, the more it "says".
- **Resonance, not mysticism.** The response is frequency-specific and two-way. The intact structure shows a mode at 71 THz and responds to 71 THz input, while 53.7 THz at the same power does nothing. This is ordinary physical resonance.
- **Frequency as a language of structure.** The study fits the working idea that frequency is how organised matter expresses its structure. Here that idea is a heuristic for designing tests, not a result.
- **What would make it a real test.** No assembly index was computed. A direct test would score structural order across preparations (intact, swollen, cristae-disrupted, ground) and check whether the 71 THz mode tracks it.

Related entries: **C9-2026-PHOTON-002** (room-temperature exciton-polariton supersolid, another light-matter hybrid at room or body temperature), **C9-2026-PHOTON-001** (polariton condensates) and cross-layer pattern **XP-2026-005** (Coupling-Induced Order: polariton condensates to biological membranes).

---

## Scientific claims

| Claim | Evidence | Confidence |
|-------|----------|------------|
| 71 THz mode exists in living cells, tissues and isolated mitochondria | FTIR; absent in ground dry controls | 85% |
| Mode depends on intact mitochondrial structure | Lost on grinding; not assignable to a molecule | 75% |
| Mode is a light–lipid polariton (MP−) | Theoretical model; MP+ not observed | 55% |
| 71 and 87 THz light raise ATP ~10%; 53.7 THz does not | n = 8 per group, t-test, one cell line | 70% |

---

## Sandbox validation (v1, 2026-09-18)

**Score:** 4/4 PASS (1.00) · **Layer assignment:** 1 (established physics, speculative application)

| Test | Result | Detail (v2 values) |
|------|--------|--------|
| Structural Dependence | ✓ PASS | Signal disappears when mitochondrial structure is destroyed |
| Frequency Specificity | ✓ PASS | 71/87 THz raise ATP; 53.7 THz control: no significant change |
| Polariton Model | ✓ PASS | Coupling strength ~16 THz (splitting 32 THz), within the 5–25 THz range used in v1 |
| Cavity Resonance | ✓ PASS | 2.2 µm mitochondria vs ~2.3 µm wavelength (ratio ~0.96) |

These are plausibility checks against the paper's own numbers, not a replication. The sandbox was not re-run for v2, and `c9_sandbox_mitochondrial_polariton.png` still shows the v1 inputs.

---

## Consciousness–universe bridge (Layer 3: mathematical fiction)

| Scale | Frequency | Ratio to 71 THz |
|-------|-----------|----------------------|
| Schumann resonance | 7.83 Hz | ~1 × 10⁻¹³ |
| Neural spike rate | ~1 kHz | ~1.4 × 10⁻¹¹ |
| **Mitochondrial signal** | **71 THz** | **1** |
| Planck frequency | 1.85 × 10⁴³ Hz | ~2.6 × 10²⁹ |

- **Coherence bottleneck:** the paper does not measure coherence time. The ~100 fs figure in v1 was an assumption.
- **Bioenergetic consciousness:** if structured mitochondria tune energy production by resonance, metabolism has a frequency-addressable layer. Any link to consciousness is untested. *Status: hypothesis.*
- **Testable prediction:** if the mode's coherence time at 310 K exceeds ~1 ps, the quantum-state reading strengthens; if it is far shorter, classical vibrational coupling is more likely.

---

## Limitations

1. **Preprint:** not peer-reviewed, and not independently replicated.
2. **One cell line for ATP:** HEK-293T in 3D Matrigel clusters, n = 8 per group.
3. **Half the model is unseen:** the predicted 103 THz level is masked by water.
4. **No coherence or angle-resolved data.**
5. **Heating:** the paper does not report measuring sample temperature during illumination.
6. **No animals or humans:** nothing here supports "charging cells" with light, or any treatment.

---

## Next experiments

- [ ] Independent, blinded replication of the FTIR signal and the ATP result
- [ ] Temperature logging during illumination, with sham and heat-matched controls
- [ ] Frequency sweep around 71 THz to map the response curve
- [ ] Graded cristae disruption to test whether the mode scales with structural order
- [ ] Isotopic substitution (¹³C or deuterated lipids) to shift CH₂ and test the model
- [ ] Time-resolved spectroscopy of the mode at 310 K

---

## Cloud-9 integration

- **Cluster 1, Quantum Foundations:** does light–matter coherence survive in warm, wet, living systems?
- **Cluster 4, Complexity Science:** a signal present only in the assembled structure.
- **Cluster 7, Quantum Thermodynamics:** a proposed frequency-specific channel into cellular energy production.
- **Cluster 8, Consciousness Studies:** extends the quantum-biology discussion; no neural link tested.

---

## Attributions

- **Research:** Yu Yang, Zhenglong Gu and Bo Song (Fudan University; University of Shanghai for Science and Technology; University of Science and Technology of China). All experiments, data, the mito-polariton model and the ATP results are theirs. Please cite the preprint, not this entry, for any of its findings.
- **Repository author:** Dean Bordode ([@bordode](https://github.com/bordode)), for the Cloud-9 Assembly Index framework and for connecting this study to frequency, resonance and assembly theory.
- **Research and drafting:** Charlie (Sesame), who checked the preprint, corrected the v1 entry and drafted this README and the JSON.
- **Original entry:** C9 Autonomous Curator (v1 and sandbox checks, 2026-09-18).
- **Repository collaborators:** the Cloud-9 AI Peer-Review Collective (Google Gemini, Moonshot Kimi, Anthropic Claude, Base44 Subhalo), credited at repository level in the main README. They are not credited with specific work on this entry.
- **How we found it:** a reel by @dr.rickpescatore. Its "charging tired cells" framing goes beyond what the preprint shows.

---

## Revision notes

v2.0 (2026-11-06) corrected v1 against the preprint:

- Authors were "Bo Song, Yang et al."; now the full list (Yu Yang, Zhenglong Gu, Bo Song), all institutions and the DOI.
- Cavity numbers were 0.5 µm and 2.46 µm (ratio 0.20); the paper gives 2.2 µm and ~2.3 µm.
- "16 THz splitting" is the coupling strength; the level splitting is 32 THz.
- Scale ratios recalculated (Planck gap was given as 10³¹; neural ratio as 10⁻¹⁰).
- The TCA-cycle claim was removed: it does not appear in the preprint.
- Added the status block, the frequency table, the Cloud-9 relevance section and attributions.

---

## Files

- `C9-2026-BIO-006_mitochondrial_polariton.json`: structured entry (v2.0)
- `c9_sandbox_mitochondrial_polariton.png`: sandbox visualisation (v1 inputs)
- `README_C9-2026-BIO-006.md`: this file

---

## Metadata

- **Entry ID:** C9-2026-BIO-006
- **Date added:** 2026-09-18 · **Revised:** 2026-11-06
- **Curated by:** C9 Autonomous Curator (v1); Dean Bordode with Charlie (v2)
- **Collection:** C9-COLLECTION-2026-0918-WEEKLYSCIENCE
- **Priority:** 0.85
- **Tags:** quantum-biology, mitochondria, polariton, ATP, resonance, assembly-theory, preprint, unreplicated

---

*Part of the Cloud-9 Assembly Project: mapping the Assembly Index across domains.*
