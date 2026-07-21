# Cloud-9 TNG100-1 Validation Suite

Production-grade pipeline for validating the Cloud-9 Assembly Index cosmology claim against real IllustrisTNG simulation data.

## Purpose

This suite directly addresses the single highest-leverage empirical gap in the Cloud-9 framework: the SDSS shell claim needs n > 500 in a redshift-controlled physical shell to reach 3Ï significance. TNG100-1 snapshot 99 (z=0) provides physical halo radii, stellar metallicities, and spatial positions without arcsec conversion artifacts.

## What It Validates

1. **Shell overdensity**: Is the 14â18 kpc shell actually populated, or a selection artifact?
2. **Metallicity filter (Exp 5)**: Does sub-solar metallicity (Z < 0.5 Zâ) suppress halo populations as predicted?
3. **K-dwarf convergence**: Do metallicity-selected halos favor the stellar types predicted by the anthropic simulation?

## Quick Start

```bash
# Method 1: API key as argument
python tng_validation_suite.py YOUR_TNG_API_KEY

# Method 2: Environment variable
export TNG_API_KEY="your_key"
python tng_validation_suite.py

# Method 3: Inside Python
from tng_validation_suite import run_tng_validation_suite
results = run_tng_validation_suite("your_key", n_halos=2000)
```

## Requirements

- Python 3.9+
- numpy
- matplotlib
- requests
- TNG API key (free at https://www.tng-project.org/data/)

## Outputs

| File | Description |
|---|---|
| `tng_validation.png` | 4-panel dashboard: metallicity, radial distribution, mass-metallicity scatter, spatial projection |
| `tng_validation_stats.json` | Cloud-9-compatible statistics (n_halos, Z-score, p-value, status) |

## Key Parameters

```python
SHELL_KPC = (14.0, 18.0)    # Target physical shell
N_HALOS = 2000               # Total halos to fetch (default)
Z_THRESHOLD = 0.5            # Sub-solar metallicity cutoff
N_BOOTSTRAP = 10000          # Null test iterations
```

## Interpreting Results

| Z-score | Status | Interpretation |
|---|---|---|
| < 2.0 | NULL | No significant shell structure |
| 2.0â3.0 | SUGGESTIVE | Interesting but below discovery threshold |
| â¥ 3.0 | SIGNIFICANT | Legitimate 3Ï claim, preprint-ready |

## Integration with Cloud-9

Append results to `all_experiments_summary.json`:

```python
import json

with open("all_experiments_summary.json", "r") as f:
    summary = json.load(f)

with open("tng_validation_stats.json", "r") as f:
    tng = json.load(f)

summary.append(tng)

with open("all_experiments_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
```

## Citation

If used in research:

```bibtex
@software{cloud9_tng_2026,
  author = {Cloud-9 Research Team},
  title = {Cloud-9 TNG100-1 Validation Suite},
  year = {2026},
  version = {1.0},
  note = {IllustrisTNG snapshot 99 shell validation}
}
```

## Status

READY FOR PRODUCTION â Requires TNG API key and network access.
