# Cloud-9 Results Provenance and Statistical Status

**Status:** Evidence audit in progress  
**Date:** 2026-08-13

This document separates reported numerical results from statistical thresholds, software defaults, and results whose original Colab provenance has not yet been verified.

## Why this document exists

The repository contains several generations of Cloud-9 analysis, including halo/null-model work, TNG-related analyses, empirical scripts, and later synthesis documents. Some older documentation combines results from different runs. This file is the canonical holding place while those runs are reconstructed.

## Statistical values currently encountered

| Value | Current interpretation | Status |
|---|---|---|
| **z = 2.99 sigma** | Reported preliminary Cloud-9 halo result associated with an N=1,000 null ensemble in older documentation | **Reported, provenance still to be verified** |
| **3 sigma** | Statistical criterion described in the original null-model methodology | **Criterion, not a measured Cloud-9 result** |
| **5.41** | Threshold currently embedded in the API/application code | **Software threshold; not established as a halo experimental result** |
| **5.41 sigma experimental result** | No verified underlying halo calculation identified yet | **Do not present as an observed result** |

## Halo/null-model runs

Older repository documentation describes at least two different ensemble sizes:

### Run A — N=1,000

Older documentation reports:

- null ensemble: N=1,000 synthetic halos
- null mean: μ = 62.1 ± 8.4 bits
- Cloud-9: A_c = 87.3 ± 3.2 bits
- reported significance: z = 2.99 sigma
- reported p-value: approximately 0.0014

These numbers are retained as **reported historical results**, not as independently verified results, until the underlying calculation, inputs, and code path are traced.

### Run B — N=10,000

Older methodology text describes a 10,000-halo matched ΛCDM null ensemble. The repository does not currently provide enough verified provenance to attach the 2.99-sigma result to this ensemble.

Therefore the 10,000-halo statement is treated as a **separate calibration/validation run** until its exact output is located.

## Colab provenance

The repository contains archived Colab-oriented analysis code on the research history, including:

- `research/cloud9_v211_colab.py`
- `research/cloud9_v211.py`
- `cloud9_v1_empirical.py`
- `research/null_model_design.py`
- `research/null_ensemble_n100.py`
- `research/c9_tng_merger_extraction.py`

These files should be inspected before any numerical result is promoted to a canonical result. In particular, the analysis should establish which script produced each ensemble size, which data were used, the random seed where applicable, and exactly how the null mean and standard deviation were calculated.

## Rules for future reporting

1. Never combine N=1,000 and N=10,000 as though they were one run.
2. Never describe 3 sigma as an observed Cloud-9 result; it is a criterion unless a calculation explicitly produces that value.
3. Never describe 5.41 as an observed halo significance merely because it is an API threshold.
4. A result is **verified** only when its calculation can be traced to code, inputs, and an output artifact.
5. If the original Colab calculation cannot be reconstructed, retain the historical number but label it **unverified historical result**.
6. New analyses should record: run ID, date, code version/commit, ensemble size, cosmology/data source, random seed, estimator settings, observed A_c, null mean, null standard deviation, z-score, p-value, and output file.

## Canonical DOI

The repository's canonical DOI is:

**10.5281/zenodo.18335567**

The placeholder DOI `10.5281/zenodo.xxxxx` is legacy text and must not be used for citation.

## Scientific interpretation safeguard

Until the numerical provenance is reconstructed, the repository should describe the 2.99-sigma result as **preliminary and requiring independent confirmation**. The existence of a numerical result in an archived document is not by itself evidence that the result has been independently reproduced.
