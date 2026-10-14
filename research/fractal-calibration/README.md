# Fractal Estimator Calibration — Brain / Universe / AI Trifold

**Methods notebook (calibration discipline). Generated October 2026; Colab-sourced.** Part of the Brain / Universe / AI trifold project: before claiming fractal structure in real data, learn what the dimension estimators can and cannot distinguish on labeled test sets.

## Pre-registered discipline

- Same estimators and same scale windows for every dataset — rules fixed in advance, no post-hoc tuning
- Scale windows defined as fractions of each dataset's extent
- A dataset is called "scale-invariant" only if it passes pre-set criteria
- Every test set has a known label (true dimension, or "not a fractal")

## Contents

| Section | What it does |
|---|---|
| Step 1 | Labeled test generators + estimator calibration battery + correlation integrals |
| Step 2 | Real cosmic web data via the IllustrisTNG API |
| Step 3 | Real data vs. calibration baseline comparison |
| Extra | Unbiased cosmic-web sample run; raw API subhalo loader; pre-registered 3D volume-grid occupancy test |

## Security note

TNG API access uses the Colab Secrets manager (`userdata.get('TNG_KEY')`) — no credential values are embedded in the notebook or its outputs (verified).

Connects to: the TNG100-1 halo spectral analysis (R = −0.969) in the Cloud-9 research collection — the calibration here is what makes dimension claims on that data meaningful.
