# Null Ensemble v3: source recovery and reproducibility audit

**Audit date:** 2026-11-14  
**Repository:** `bordode/cloud9-assembly-index`  
**Audit branch:** `audit/null-ensemble-v3-provenance`  
**Scope:** historical v3 generator and the committed N=100 JSON artifact

## Executive finding

The v3 generator is recoverable from Git history, but the committed JSON cannot currently be reproduced from either recovered source snapshot as written. The JSON is internally arithmetically consistent under a population-standard-deviation calculation. However, the historical scripts contain an argument-name defect, and the later script snapshot also specifies a sample-standard-deviation calculation that does not match the committed JSON.

This audit does not invalidate the stored synthetic ensemble values. It means the exact source-to-artifact execution path remains unverified.

## Recovered historical records

1. **Generator addition:** commit [`35352eb1b46b831797071b9d8fa1f311d7124296`](https://github.com/bordode/cloud9-assembly-index/commit/35352eb1b46b831797071b9d8fa1f311d7124296), dated 2026-08-26, added `research/null-ensemble/cloud9_null_ensemble_v3.py` (477 lines; blob `bbcf2a0230c566fbeda5617c91324fa7bc344f79`). This version labels its output `3.0-KSG`.
2. **Later historical snapshot:** commit [`70fb2a97b6f8a156eabaec43a787d4e3ea629a56`](https://github.com/bordode/cloud9-assembly-index/tree/70fb2a97b6f8a156eabaec43a787d4e3ea629a56/research/null-ensemble), containing a 419-line version (blob `32e4b0c97659367470e82512c1571d2a67b478d2`). This version labels its output `3.0-KSG-fast` and explicitly describes the model as experimental synthetic.
3. **JSON addition:** commit [`1cbb26cdfbf212d973a04be8851d47ce7f0cb24a`](https://github.com/bordode/cloud9-assembly-index/commit/1cbb26cdfbf212d973a04be8851d47ce7f0cb24a), dated 2026-08-26, added `research/null-ensemble/cloud9_null_ensemble_v3.json` (blob `0d7cc9fb60e6676e433f1efdd0a30a2e3e8b5ceb`). The current `master` JSON is the same blob. The current `master` tree has no generator at that path.

## Concrete source-to-artifact discrepancies

### 1. Constructor keyword mismatch in both recovered generator snapshots

Both recovered versions define `TARGET` using keys `M_vir_msun` and `R_vir_kpc`, then call `CosmicHaloEvolver(..., **TARGET)`. The constructor instead accepts `target_M_vir` and `target_R_vir_kpc`. As written, the call raises `TypeError` for unexpected keyword arguments before the halo evolution starts.

This is a static code finding; no claim is made here about what code may have been run outside the committed repository.

### 2. Standard-deviation convention mismatch in the later snapshot

The later `3.0-KSG-fast` script calculates the ensemble standard deviation using `np.std(A_values, ddof=1)` (sample standard deviation).

Recomputing from all 100 committed `A_c_bits` entries gives:

| Statistic | Recomputed from JSON | Recorded in JSON |
|---|---:|---:|
| N | 100 | 100 |
| Mean | 58.0622231 | 58.0622 |
| Population SD (`ddof=0`) | 3.3905664 | 3.3906 |
| Sample SD (`ddof=1`) | 3.4076475 | — |
| Z using population SD | 8.6232721 | 8.6233 |
| Z using sample SD | 8.5800474 | — |

The committed JSON therefore uses the population SD convention, not the sample SD convention specified in the later recovered script. The earlier 477-line script uses NumPy's default population SD, but labels its output `3.0-KSG`, not `3.0-KSG-fast`.

### 3. Artifact metadata does not identify an exact executable source revision

The JSON records timestamp `2026-08-24T23:33:33.142045Z`, pipeline label `3.0-KSG-fast`, seeds 1000–1099 and synthetic-model provenance. The recovered source snapshots were committed on 2026-08-26. The JSON does not record a source commit SHA, source-file hash, environment lockfile, or command invocation.

The later script's output schema resembles the JSON, but its sample-SD convention conflicts with the recorded statistics. The earlier script's population-SD convention matches the JSON, but its output schema and pipeline label differ. This supports a provenance gap; it does not identify which uncommitted or external source variant may have generated the artifact.

## Statistical interpretation

The arithmetic `(87.3 - 58.0622) / 3.3906 = 8.6233` is internally consistent with the population SD of the 100 stored synthetic values.

That arithmetic is a standardized comparison of a fixed Cloud-9 comparison value against this synthetic ensemble. It is not, by itself, a calibrated discovery significance, an empirical tail probability at 8.62 sigma, or a direct validation against real IllustrisTNG / ΛCDM temporal evolution. With 100 null realizations, the empirical tail resolution is limited; zero exceedances, if observed, would not imply zero probability.

The existing caveat that real TNG temporal validation remains pending should be retained.

## Recommended next steps

1. Preserve the historical scripts and JSON unchanged as archival evidence.
2. Locate the exact runtime source or notebook used on 2026-08-24, if one exists.
3. Ask the original run operator for the executed source revision, environment, and command log if available.
4. Create a separate corrected reproduction implementation with explicit constructor argument mapping and a predeclared SD convention.
5. Re-run the fixed seeds 1000–1099 and compare all 100 member values, not only the aggregate mean and standard deviation.
6. If the per-member values do not match, label the new output as a fresh reproduction, not a reconstruction of the historical artifact.
7. Keep the 8.62σ wording model-dependent and exploratory until independent real-data temporal validation and null-model calibration are complete.

## Reproducibility status

**Source recovered:** yes.  
**Historical source executes as committed:** no, due to the constructor keyword mismatch.  
**JSON aggregate arithmetic checked:** yes, under population SD.  
**Exact source-to-JSON regeneration established:** no.  
**Real TNG temporal validation:** pending.
