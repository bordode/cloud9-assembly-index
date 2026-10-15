# JWST Single-Line Emitter — Literature Audit Addendum

**Status:** Source-text review only. No FITS files have been independently downloaded or analysed.

## New source-level checks

Primary source: Huberty et al. (2026), arXiv:2610.12553, especially Sections II, III.3–III.4, Table 2, and Section V.

### 1. The combination method is described inconsistently

The paper's prose does not describe one unambiguous combined-spectrum operation:

- Section II, describing the detector-image stacks, says the aligned dispersed images were error-weighted-mean-combined.
- Section III.3, lines around the extraction description, says they compute the weighted mean of the four extracted spectra.
- The next sentences say they generate 1,000 realizations from each stack, take the **median of the four spectra in every wavelength bin** for each realization, and use the standard deviation of that median distribution as the final spectrum's error.
- Figure captions refer to the combined spectrum as a weighted mean.

These may refer to different stages or may be a wording inconsistency. Do not assume they are equivalent. The implementation/code or clarification from the authors is needed to establish which operation generated the plotted spectrum and reported line flux.

### 2. The two significance values remain unexplained

Table 2 reports a combined flux of (2.5 ± 0.3) × 10^-18 erg s^-1 cm^-2 and 8.4σ. The conclusion describes the detection as S/N = 5.4. The rounded flux/error ratio is 2.5/0.3 ≈ 8.3, consistent with the table, but the conclusion does not define the 5.4 statistic. It could be a distinct statistic or a reporting inconsistency; the paper text alone does not resolve it.

### 3. Stack fluxes are not a substitute for reproducing the published combination

A simple inverse-variance weighted combination of the rounded stack fluxes A–D is approximately 2.82 × 10^-18 erg s^-1 cm^-2, with a formal error of about 0.32 × 10^-18. This differs from the reported 2.5 ± 0.3. This calculation assumes independent Gaussian errors and uses rounded values; it is a diagnostic only, not evidence of a wrong result. Different extraction/combination methods, correlations, or unrounded measurements could affect the comparison.

### 4. Detection significance needs context

The paper's candidate-identification procedure starts from detector-image candidates selected using a threshold of 3 times the local RMS across more than five contiguous pixels, then applies cross-dither and cross-orientation matching. The final line's quoted significance should be distinguished from the initial pixel/source-detection threshold and from any correction for the search over many candidates. The paper reports hundreds of candidate features per stack and a later matching procedure. Any independent significance calculation should document the full selection process rather than treating the fitted flux/error ratio as automatically equivalent to a global false-alarm probability.

## Next reproducibility actions

1. Obtain the authors' exact MAST products and preserve filenames, processing metadata, checksums, and CRDS context.
2. Establish whether the final extracted spectrum is a weighted mean, median, or another estimator, and reproduce it from the four stacks.
3. Reproduce the Gaussian line fit and Monte Carlo uncertainty calculation.
4. Reconcile 8.4σ versus 5.4 S/N and document what each statistic measures.
5. Account for candidate selection and multiple testing when assessing detection significance.
6. Only after this baseline is reproducible, test any pre-specified Cloud-9 metric against appropriate controls. No extraterrestrial or new-physics interpretation is warranted from the unexplained line alone.

## Sources

- Paper HTML: https://arxiv.org/html/2610.12553
- arXiv record: https://arxiv.org/abs/2610.12553
- MAST data DOI cited by the paper: https://doi.org/10.17909/tct8-jr92
- MAST API documentation: https://jwst-docs.stsci.edu/accessing-jwst-data/mast-api-access
