# JWST Single-Line Emitter: Reproducibility Study

**Status:** Phase 0 — literature review and analysis plan only  
**Scientific result:** Not independently reproduced  
**Cloud-9 interpretation:** Not evaluated; no Cloud-9 claim is made

## 1. Purpose

Track an independent reproducibility check of the unusual emission-line candidate reported by Huberty et al. (2026). The aim is to establish what the public JWST observations support before considering whether any Cloud-9 metric adds explanatory or predictive value.

This is a research record, not a claim that the object is extraterrestrial, technological, or evidence of new physics.

## 2. Primary sources and data

- Huberty et al., *A Single Line-Emitter Identified in an Unbiased Search with JWST/NIRSpec: Multi-Object Coronagraphy for Slitless Spectroscopy*, ApJ (2026), DOI: https://doi.org/10.3847/1538-4357/ae9a94
- arXiv preprint: https://arxiv.org/abs/2610.12553
- MAST dataset DOI cited by the authors: https://doi.org/10.17909/tct8-jr92
- JWST observing program: JWST-3290 (MOCSS HUDF)

## 3. Reported measurements (from the paper, not independently verified here)

The paper reports a line near 16004 ± 1 Å (1.6004 μm), integrated flux (2.5 ± 0.3) × 10^-18 erg s^-1 cm^-2, and observed-frame FWHM 13.2 ± 2.0 Å. It reports no corresponding source in the comparison JADES imaging and discusses ordinary astrophysical possibilities, including an unusual galaxy, AGN-related explanations, and transient phenomena.

The four stack-level measurements in Table 2 are:

| Stack | Flux (10^-18 erg s^-1 cm^-2) | Reported significance |
|---|---:|---:|
| A | 2.3 ± 0.5 | 4.7σ |
| B | 3.5 ± 0.6 | 6.1σ |
| C | 2.9 ± 0.7 | 4.5σ |
| D | 2.9 ± 1.2 | 2.5σ |
| Combined | 2.5 ± 0.3 | 8.4σ |

**Reproducibility flag:** Table 2 reports a combined significance of 8.4σ, while the conclusion describes the signal-to-noise ratio as 5.4. This difference must be traced to its definition, calculation, or a possible reporting error. It is not, by itself, proof that the line is false.

## 4. Reproduction plan

1. Retrieve the public products referenced by the MAST DOI and record the exact filenames, calibration levels, processing dates, pipeline versions, CRDS context, and checksums.
2. Identify the four stack/orientation products used in the paper and verify the target position and wavelength mapping.
3. Reproduce the line measurement separately for each stack: local background, uncertainty model, line center, integrated flux, FWHM, and significance.
4. Reproduce the combined estimate with the authors' stated Monte Carlo procedure where possible. Compare it with an independently specified noise/bootstrap treatment and explain the 8.4σ versus 5.4 signal-to-noise values.
5. Check sensitivity to background subtraction, extraction aperture/trace, correlated noise, wavelength calibration, and any selection effects from candidate identification. Report all deviations from the published method.
6. Preserve plots, code, parameters, logs, and data provenance. Do not silently substitute updated products for the paper's processing version; if current reprocessed data are used, compare them explicitly.

## 5. Cloud-9 evaluation gate

Do not apply or tune a Cloud-9 score to this single target and then present the resulting fit as confirmation. First establish a reproducible baseline using standard spectroscopy. Only afterward may a pre-specified Cloud-9 metric be evaluated against suitable positive controls, null/synthetic controls, and comparison objects, with its added value measured out of sample.

A null or non-incremental result is a valid outcome and should be documented. Any computational pass is not, by itself, scientific validation.

## 6. Current limitations

- This document records the paper's reported results and a proposed test plan.
- The original FITS products have **not yet been independently downloaded and reanalysed in this study**.
- No independent line significance, astrophysical identification, or Cloud-9 result is claimed.
- The source paper itself presents several possible astrophysical explanations and says follow-up observations are needed.

## 7. Decision rule

The study can move from Phase 0 only when the public data products are identified and the analysis is executable from a documented environment. The final record should state whether the line measurements reproduce, whether the significance discrepancy is resolved, and whether Cloud-9 adds any independently demonstrated value.