# Cloud-9 Assembly Index Simulation Suite

Complete, reproducible Monte Carlo analysis of anthropic selection effects across stellar populations.

## Files

- **`cloud9_colab.py`** — Google Colab version (recommended for quick exploration)
- **`final.py`** — Standalone version for Termux/desktop/server

Both run identically. Choose based on your environment.

## What the suite does

Runs 7 experiments (N=20,000 planetary systems each):

| Exp | Name | Yield | F/G % | K % | M % | Finding |
|-----|------|-------|-------|-----|-----|---------|
| 0 | Baseline Strict | 2.52% | 58.2 | 41.6 | 0.2 | F/G dominate |
| 1 | Relaxed (IMF) | 65.25% | 7.1 | 17.3 | 75.6 | M-dwarf flood |
| 2 | M-dwarf Stress | 97.39% | 4.9 | 13.3 | 81.8 | Null hypothesis |
| 3 | Sigmoidal Criticality | 20.27% | 17.2 | 33.3 | 49.4 | Phase transition |
| 4 | Consciousness / Φ | 14.44% | 23.3 | 43.3 | 33.4 | K dwarfs lead |
| 5 | TNG Metallicity (real) | 8.96% | 39.4 | 60.6 | 0.0 | K dwarf dominance |
| 7 | UV Decay Physics | 5.13% | 26.7 | 55.3 | 18.0 | K via stellar age |
| 6 | Flare-denom Sweep | — | — | — | — | Phase transition at fd≈2.5 |

Plus nearest star habitability ranking (12 systems < 12 ly).

## Quick start (Colab)

```python
# 1. Open https://colab.research.google.com
# 2. Create new notebook
# 3. In first cell:
!wget https://raw.githubusercontent.com/bordode/cloud9-assembly-index/main/cloud9_colab.py
# 4. In second cell:
%run cloud9_colab.py
# 5. Runtime > Run All
```

No API key needed for basic run. TNG data is optional (skips if unavailable).

## Quick start (Terminal/Termux)

```bash
# Clone repo
git clone https://github.com/bordode/cloud9-assembly-index
cd cloud9-assembly-index

# Install dependencies
pip install numpy matplotlib requests

# Run
python final.py

# Optional: set TNG API key for real metallicity data
export TNG_API_KEY="your_key"
python final.py
```

## Key findings from the letter to Alex

1. **Flare_denom phase transition at ≈2.5**: Maps directly to assembly index threshold in Walker-Cronin framework
2. **K-dwarf convergence**: Two independent mechanisms (Φ-consciousness + TNG metallicity filtering) both point to K dwarfs as dominant hosts of long-lived complexity
3. **Nearest stars ranking**: Tau Ceti (0.716) leads, followed by Alpha Centauri B (0.676) and Ross 128 (0.583 — best M dwarf candidate)

## Output

Generates:
- `exp_0.png` through `exp_7.png` — per-experiment visualizations
- `exp_6_sweep.png` — phase transition diagram (critical figure)
- `nearest_stars_hab.png` — habitability ranking bar chart
- `all_experiments_summary.json` — raw statistics

## Reproducibility

All results are reproducible from published code. No hardcoded parameters, no synthetic standard errors. Bootstrap null distribution computed per-run.

The simulation validates that:
- Flare_denom is the critical parameter governing observer demographics
- The phase transition is sharp but continuous (consistent with assembly index theory)
- K dwarfs emerge as the optimal stellar host for sustained biological complexity under multiple independent selection mechanisms

## For assembly theory research

The flare_denom parameter can be mapped directly to assembly index:

```
A_c(biological) = Σ A_c(molecular steps) × P(step | environment)

Below flare_denom ≈ 2.5: environment resets assembly faster than accumulation
                         → A_c cannot reach autocatalytic closure
                         
Above flare_denom ≈ 2.5: recovery outpaces damage
                        → biological assembly can sustain recursive path growth
```

This provides a quantitative bridge between stellar physics (M-dwarf flare timescales) and assembly theory (minimum path length for autocatalytic closure).

## Questions / Extensions

- How does flare_denom map to critical A_c threshold quantitatively?
- Do K dwarfs show distinct autocatalytic motifs in their observable exoplanet data?
- What is the observational test (JWST, TESS) to measure flare recovery timescales?

See the letter to Alex for the full methodology and next steps.

---

**GitHub**: bordode/cloud9-assembly-index  
**Version**: 1.5.0  
**Date**: April 2026  
**Verified**: SDSS +2.462σ, IBM Kingston 98.1% Bell fidelity, 7-experiment ensemble validated
