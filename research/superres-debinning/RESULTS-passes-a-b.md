# Passes A and B: drift quantification and the dithered stack

*Results from the study run of 2026-11-14, reported from the run's own output. Figures named below were not rendered in that run and are pending. Every number here comes from the same pipeline and λ grid as the single-frame work in `README.md`, which is what makes the single-vs-multi comparison clean.*

## Part A - the stars-image drift, quantified

Warm-started λ-continuation over a fine σ grid, single frames:

| b | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| stars σ* | 0.018 | 0.012 | 0.016 | 0.011 | 0.007 |
| stars σ*·b | 0.036 | 0.037 | 0.065 | 0.052 | 0.043 |
| hubble σ*·b | 0.177 | >0.3 | >0.4 | >0.5 | >0.6 |

Exponent ≈ −0.82, close to but not exactly 1/b. The product wanders from 0.036 to 0.065, a 1.8× spread around a mean of 0.047. The thread's Andromeda constant (0.075) sits between our stars and hubble values: mid-range for smooth scenes, and the thread had no second scene against which to notice the spread.

**Verdict:** the "law" holds only as *exponent ≈ −1, constant = f(intra-block contrast), error bars ±50%*.

## Part B - dithering dissolves the blind-λ problem

Nine sub-pixel phase-dithered frames, b=3, blind picks measured against the oracle on the identical 6-point λ grid:

| cell | whiteness | L-curve | GCV |
|---|---|---|---|
| hubble σ=0.02 | +1.8% | +1.8% | +0.0% |
| hubble σ=0.05 | +0.0% | +5.4% | +0.0% |
| stars σ=0.02 | +3.4% | +3.4% | +0.0% |
| stars σ=0.05 | +0.0% | +6.0% | +0.0% |

Against the single-frame study (whiteness +18-24%, L-curve worst cell +27.6%, GCV +21% on stars at low noise), the collapse is complete: means of ~1%, ~4%, and 0.0%. GCV matches the oracle in every cell. L-curve improves least (up to +6%) because it is a geometric corner criterion: stacking fixes conditioning, not geometry.

## Physics found en route

1. **Integer-pixel dithering is an alias trap.** Box-3 binning has DFT zeros at both 1/3 and 2/3 cycles/px. Integer or 1/3-resonant phases fail to cancel the 2/3 alias, so period-3 fine structure is invisible to every frame at once. Only genuinely sub-pixel phases break it.
2. **Even-length Fourier shifts are not unitary without band-limiting.** The Nyquist row/column breaks Hermitian symmetry during sub-pixel shifting (0.4 max error on a delta). Projecting out those two spectral lines (≈1.6% of energy) makes shifts unitary to 1e-13, verified against `ndimage.shift` to 5e-9.
3. **Full-phase stacking does not give x/9 exactly, and does not need to.** The averaged normal operator keeps residual off-diagonal coupling between coarse-adjacent Fourier modes of size 1/√K. The spectrum stays tightly clustered, so CG converges quickly; an exact identity was the wrong target.

## Caveats

One noise realization per cell; periodic boundary conditions for the shifts; a single Hutchinson probe; and the coarse 6-point λ grid, so picks are grid-quantized. The single-frame and multi-frame numbers share grid and pipeline, so the comparison itself is unaffected.

## Bottom line

The thread's implied prescription survives independent testing. Single-frame fitting is bottlenecked by unmeasurable, scene-dependent statistics; nine dithered frames make the problem well-posed enough that even the worst blind criterion lands within 6% of the oracle.
