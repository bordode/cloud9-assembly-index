# Super-resolution debinning: independent replication

Independent check of claims from a public thread on reconstructing binned Hubble-style
images with a pixel-integrated forward model plus a smoothness prior. Everything here is
**my own synthetic-scene replication**, not the original author's data. Numbers are not
directly comparable to the thread's (different scenes, lambda normalization, control).

## Reproduce
```
pip install -r requirements.txt
python superres_study.py --seeds 5      # ~4 min; writes results.json, tables.md, figures/
python superres_study.py --quick        # smoke test
```
Setup: 72x72 synthetic scenes (`nebula`, `stars` with FWHM 1.3 px, `mixed`), block-mean binning
b in {2,3,4}, sensor-pixel noise sigma (binned noise = sigma/b), periodic Laplacian prior,
13-point lambda grid (1e-6..1, half-decade), CG solver, 5 noise seeds (E3 uses 4).
All seeds are fixed; `results.json` holds every per-cell number plus versions.

## Claim status

| claim | source | status |
|---|---|---|
| Correct pixel-integrated data term is the main win; prior is secondary | original thread | not retested here |
| Blind lambda criteria are unreliable on a single frame | original thread | **replicated, scene-dependent** (E1) |
| Whiteness over-regularizes | original thread | **replicated** on smooth scenes (E1) |
| Wrong-way L-curve corner | original thread | **partly replicated**: fails on `stars` at sigma=0.05 (E1) |
| sigma x b = const (0.075) | original thread | **not supported as a universal constant**: `stars` gives 0.052-0.066, smooth scenes never cross by sigma=0.08 (E3) |
| Dithering fixes blind-lambda selection | follow-up claim | **partly supported**: GCV and whiteness improve even at matched total noise; L-curve does not (E2) |

## What the data say (and do not)
- RMSE(lambda) basins are very flat (mean ~3.8 decades within 2% of optimum), so a criterion can
  miss by a decade and cost little. That is why single-frame mean costs look small for GCV.
- GCV fails on point-source scenes at low noise (about 11% mean, 22% worst) and is fine elsewhere.
- Dithering arms use all b*b integer fine-pixel phases. The stacked operator is still rank-deficient
  (box-b filter nulls at k/b cycles/px), so the prior still matters. `dither_matched` inflates
  per-frame noise by sqrt(K) so total noise equals the single frame; it isolates conditioning
  from extra data. Its oracle RMSE is still better than single-frame (0.0324 vs 0.0373).
- Discrepancy principle is omitted (needs known sigma, not data-only).

## Limitations
Synthetic scenes only (no real Hubble crops); periodic boundaries; 2-probe Hutchinson trace for GCV;
half-decade lambda grid; E3 zero-crossings are linearly interpolated on a coarse sigma grid and
"none in range" means no crossing by sigma=0.08. Treat percentages as +/- a few points.

## Results
### E1 - blind-lambda cost over oracle (%, mean / worst), single frame

| scene | sigma | whiteness | L-curve | GCV |
|---|---|---|---|---|
| nebula | 0.02 | 35.0 / 57.1 | 0.2 / 0.5 | 2.1 / 4.0 |
| nebula | 0.05 | 30.2 / 34.9 | 2.3 / 6.5 | 1.8 / 3.8 |
| stars | 0.02 | 10.8 / 21.9 | 1.4 / 2.7 | 10.8 / 21.9 |
| stars | 0.05 | 1.0 / 2.4 | 14.4 / 26.2 | 1.0 / 2.4 |
| mixed | 0.02 | 34.4 / 58.3 | 0.3 / 0.7 | 2.9 / 7.0 |
| mixed | 0.05 | 28.0 / 34.0 | 2.8 / 7.2 | 1.9 / 3.7 |

Mean width of the RMSE basin (within 2% of optimum): **3.8 decades** (grid step 0.5).

### E2 - dithering at b=3 (cost over oracle, %, mean / worst; oracle RMSE in last column)

| mode | whiteness | L-curve | GCV | mean oracle RMSE |
|---|---|---|---|---|
| single | 23.9 / 38.9 | 2.8 / 13.8 | 2.7 / 7.3 | 0.0373 |
| dither_full | 3.2 / 8.0 | 6.1 / 9.6 | 0.2 / 1.1 | 0.0247 |
| dither_matched | 1.1 / 7.8 | 5.7 / 15.5 | 0.2 / 1.2 | 0.0324 |

### E3 - vanishing point (first downward zero-crossing of gain over bilinear)

| scene | b | sigma* | sigma* x b | gain at sigma=0.08 |
|---|---|---|---|---|
| nebula | 2 | none in range | - | +0.9% |
| nebula | 3 | none in range | - | +4.2% |
| nebula | 4 | none in range | - | +9.8% |
| stars | 2 | 0.026 | 0.052 | +10.7% |
| stars | 3 | 0.018 | 0.053 | +6.1% |
| stars | 4 | 0.016 | 0.066 | +0.3% |
| mixed | 2 | none in range | - | +1.1% |
| mixed | 3 | none in range | - | +3.7% |
| mixed | 4 | none in range | - | +9.1% |

Figures: `figures/vanishing_point.png`, `figures/blind_lambda_dither.png`.

## Provenance
Original thread: posts by their author (not included here). Everything in this repo: independent replication.
