# Blind-λ selection and phase-dithered stacking: preliminary pilot

**Date:** 2026-11-07  
**Status:** preliminary research note; results transcribed from the researcher’s supplied run summary, not independently reproduced from raw artifacts in this repository.  
**Scope:** Laplacian-prior reconstruction, blind regularisation selection, and multi-frame phase diversity. This note is separate from the Poisson PSF-deblending benchmarks.

## 1. Questions

1. Does the width of the oracle-RMSE basin change with noise level, potentially explaining why a crude switching rule can appear successful?
2. Does phase-dithered multi-frame acquisition improve blind-λ selection beyond what would be expected from simply collecting more independent exposures?

## 2. Single-frame results supplied for this pilot

### 2.1 Basin width and convergence check

The reported RMSE(λ) basin spans approximately **0.5–3 decades within 2% of the optimum**, depending on cell. A loose-versus-tight conjugate-gradient check reportedly agreed to four decimal places. This supports (but does not yet independently establish) the interpretation that the basin is genuinely broad rather than merely flattened by loose solver convergence.

The interpretation should remain local to the tested forward model, scene set, λ grid, and solver tolerances. A scalar agreement to four decimal places is not a substitute for publishing the full per-λ residual/convergence traces.

### 2.2 Scene dependence of blind criteria

A 36-cell sweep was reported: three scenes × binning factors b=2,3,4 × noise σ=0.02,0.05, with four data-only selection rules. Reported mean RMSE penalty relative to the oracle-λ result:

| Criterion | σ=0.02 | σ=0.05 | Reported behaviour |
|---|---:|---:|---|
| Whiteness | 18.9% | 12.9% | Picks roughly 1.5–2.5 decades too high |
| L-curve | 3.4% | 8.5% | Can hit the oracle on stars at low noise; wrong-way corner on moon/stars at high noise |
| GCV | 4.4% | 1.1% | Near oracle on some scenes; large scene-specific failure on stars at low noise |

The supplied account reports the L-curve selecting a λ about one decade below the oracle in some moon/star cells at σ=0.05, while the oracle λ increases. It also reports opposite GCV failure directions across scene contexts: under-regularisation in the Andromeda post and over-regularisation in the star-field pilot.

These are not universal properties of the named criteria. They are evidence that their behaviour depends on the forward operator, scene spectrum, noise regime, discretisation, and implementation.

### 2.3 Warm-started star-field drift

Reported optimal noise thresholds:

| b | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|
| Star-field σ* | 0.018 | 0.012 | 0.016 | 0.011 | 0.007 |
| Star-field σ* × b | 0.036 | 0.037 | 0.065 | 0.052 | 0.043 |

The star-field product ranges from 0.036 to 0.065 (about 1.8×); its mean is approximately 0.047. The reported log-log exponent is about −0.82, near but not exactly −1.

For Hubble, the supplied σ*×b values were lower bounds: b=2: 0.177; b=3: >0.3; b=4: >0.4; b=5: >0.5; b=6: >0.6. These should not be plotted or treated as exact estimates.

**Interpretation:** an approximate inverse-bin-size trend may describe the star field over this tested range, but the coefficient is scene-dependent. A universal constant such as 0.075 is not supported by these cross-scene values.

## 3. Nine-phase dithered-stack pilot

The supplied pilot used nine sub-pixel phase-dithered frames at b=3 and compared blind-criterion choices with the oracle on the same six-point λ grid.

| Cell | Whiteness penalty | L-curve penalty | GCV penalty |
|---|---:|---:|---:|
| Hubble, σ=0.02 | 1.8% | 1.8% | 0.0% |
| Hubble, σ=0.05 | 0.0% | 5.4% | 0.0% |
| Stars, σ=0.02 | 3.4% | 3.4% | 0.0% |
| Stars, σ=0.05 | 0.0% | 6.0% | 0.0% |

The researcher reports that the single-frame baseline had substantially larger penalties (whiteness typically around 18–24%, a worst L-curve cell around 27.6%, and a GCV star/low-noise cell around 21%). The dithered stack therefore appears markedly more stable in this pilot.

**Important interpretation limit:** these results do not yet show that phase diversity itself caused the improvement. Nine frames may also mean nine times the total exposure or nine independent noise realizations. The necessary control is a nine-frame **non-dithered** stack with the same total exposure, noise model, and processing budget.

## 4. Implementation and numerical caveats reported

The supplied debugging notes report:

- Integer-pixel shifts were found to preserve a period-three alias/nullspace under box-3 binning; genuinely sub-pixel phase offsets were needed to break it.
- Even-length Fourier sub-pixel shifts violated the intended unitary property at Nyquist unless the affected Nyquist lines were projected out.
- After that projection, shift checks reportedly agreed with scipy.ndimage.shift to about 5e-9 and an adjointness/unitarity diagnostic to about 1e-13.
- The projection removed approximately 1.6% of energy.
- Periodic boundary conditions were used.
- The multi-frame normal operator retained small off-diagonal coupling; exact identity of the averaged normal operator was not required for fast CG convergence.

These implementation details are material. The Nyquist projection changes the effective signal space and must be stated in the forward model; it should not be hidden as a numerical convenience.

## 5. Required follow-up: separate phase diversity from exposure gain

The next benchmark should compare, on identical scenes and matched total photon/noise budgets:

1. **Single frame:** one exposure, baseline.
2. **Nine repeated, zero-dither frames:** nine independent noise realizations with no phase diversity.
3. **Nine phase-dithered frames:** same number of frames and same per-frame exposure as arm 2.
4. **Optional phase ablations:** 3 and 5 well-spaced phases, plus a deliberately aliased/integer-shift control.

For each arm:

- Use identical underlying scenes, binning, PSF/forward operator, total exposure, and noise-generation convention.
- Make the noise independence/correlation model explicit. If read noise and photon noise are both present, model them separately.
- Compare both fixed per-frame exposure and fixed total exposure if the intended application needs both interpretations.
- Use multiple independent noise seeds per scene/cell.
- Use the same λ grid for paired comparisons, then refine around the selected and oracle minima.
- Increase Hutchinson probes and report estimator variance; one probe is insufficient to establish stable GCV behaviour.
- Report full RMSE(λ), criterion(λ), CG residual histories, iteration counts, and oracle basin width.
- Report singular/eigenvalue spectra or condition estimates for the stacked forward/normal operator.
- Check adjointness numerically for every shift operator and disclose the Nyquist projection.
- Include non-periodic or padded-boundary sensitivity checks.
- Report per-cell results and uncertainty intervals, not only means.

### Main discriminating test

If the nine-frame zero-dither stack improves blind-λ selection almost as much as the phase-dithered stack, the apparent gain is primarily attributable to repeated measurements / improved noise statistics. If the phase-dithered stack materially outperforms the matched zero-dither stack at equal total exposure, that is evidence for a genuine phase-diversity contribution.

## 6. Provisional conclusion

The supplied pilot supports two cautious claims:

1. The apparent noise–binning threshold is not a universal constant; it varies with scene structure, and the tested star-field trend is only approximately inverse in b.
2. Nine-phase stacking is promising for blind-λ stability, but its causal mechanism remains unresolved until it is compared with a matched nine-frame zero-dither control.

The broad oracle basin may explain why some inaccurate λ choices incur only a small RMSE penalty. It does **not** by itself explain the multi-frame improvement, nor does it establish that a switching rule will generalise to unseen scenes.

## 7. Provenance

All numerical results in this note are transcribed from the research summary supplied in the conversation on 2026-11-07. Raw arrays, source code, run logs, and figure-generation scripts were not included with that summary and have not been independently inspected for this note. The figures generated for the conversation are illustrative plots of the supplied summary values, not substitutes for raw benchmark artifacts.
