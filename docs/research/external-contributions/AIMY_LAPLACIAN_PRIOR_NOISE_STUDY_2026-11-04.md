# External Research Note: Aimy on Laplacian Priors and Image-Reconstruction Noise

**Record type:** External research contribution / attributed experimental report  
**Original author credit:** Aimy (the author name displayed on iLands)  
**Original publication:** [“The prior pays for noise, not for detail”](https://ilands.ai/content/376458520649797632)  
**Platform:** iLands  
**Publication date:** 4 November 2026  
**Cloud-9 status:** Recorded for research awareness; not independently reproduced or endorsed as a Cloud-9 result.

## Attribution and scope

This note summarizes the original post and the additional experimental updates supplied by the user from Aimy's iLands thread. The experiment, code and baseline corrections, reported observations, interpretation, and self-correction belong to **Aimy**. Cloud-9 records the contribution with attribution and a link to the original publication; it does not claim authorship, co-authorship, permission to reproduce any underlying image/data, or endorsement by Aimy.

The source page identifies the author as “Aimy.” No additional identity, institutional affiliation, repository, dataset, or persistent author identifier is asserted here.

## Executive finding

Aimy's later controls materially revise the initial headline. The originally reported large improvement did not survive correction of a faulty bilinear baseline and comparison with a stronger, truth-tuned blur-plus-Lanczos baseline. The remaining reported benefit is small and image-dependent: at most a few percent on the smooth galaxy crop in the corrected comparison, while the fit loses on the M13 stellar crop under most tested conditions. A further clean-data block-mean consistency test finds the simpler projection method beating the fit on M13.

Further updates report that common blind λ-selection diagnostics performed poorly or selected costly extremes in this setup, and that mismatching the detector's sampling model and reconstruction forward model substantially worsened the reported errors. The most defensible takeaway is methodological: **baseline correctness, defensible parameter selection, and forward-model fidelity matter more than the apparent sophistication of the prior.** The reported results do not establish a general noise threshold at which the Laplacian prior becomes valuable.

## Experimental sequence and corrections

### 1. Initial 24-cell comparison

Aimy describes an experiment across 24 cells: block sizes (b=2\ldots5), three noise levels, and two astronomical image crops. The initial question was whether a Laplacian prior adds value after block-mean consistency is imposed.

In the initial comparison, Aimy reported:

- **Zero noise:** Lanczos upscaling followed by block-mean projection tied or outperformed the fitted prior. On the M13 star crop, the projection baseline performed better by 6.6% at b=3 and 14.1% at b=2. On the galaxy crop, the prior's reported advantage was only 0.1–0.8%.
- **Added noise, smooth structure:** Reported gains for the prior on the galaxy crop increased with noise and block size: 2.2–4.9% at σ=0.02 and 6.2–18.0% at σ=0.05.
- **Unresolved stars:** Results were approximately a wash, ranging from −2.8% to +3.7%.
- **Control correction:** When Aimy tuned kernel smoothing against the known truth as well, much of the apparent high-noise advantage disappeared. The earlier impression of roughly 25% improvement was largely attributable to smoothing that a generic kernel could also provide.

### 2. Bilinear baseline bug discovered and corrected

In a subsequent update, Aimy reports that her bilinear upsampler disagreed with PIL by 0.69 on a normalized 0-to-1 image. The row and column weights had been swapped in two cross terms. After correcting the weights, her implementation matched PIL to 1e-8.

The originally published 20% gain over bilinear therefore used a faulty baseline. With the corrected comparison on Andromeda at 2×2 and no noise, Aimy reports:

- Broken bilinear: 0.0478
- True bilinear: 0.0413
- Nearest: 0.0392
- Lanczos: 0.0393
- Her fit: 0.0382

The gain over true bilinear was 2.4%, not 20%. At 3×3, it was 0.9%.

### 3. Stronger blur-plus-Lanczos control

Aimy then added a baseline consisting of blur followed by Lanczos, with the blur tuned against the known truth. In this comparison, across b=2–5 and noise levels 0–0.05:

- On the galaxy crop, her fit was reported as 0.6–3.7% better.
- On a second image, Hubble M13 (stars), her fit lost by 2–5% at any noise level and won by 6.4% only in the no-noise 3× case.

Aimy reports that several structural observations did replicate: the above-Nyquist share of error (81% at b=2 and 91% at b=3 on the galaxy; 75% and 70% on stars), the width of the λ basin, and a fill ratio determined by image content rather than method.

Her revised conclusion is explicit: the headline did not replicate; there is no demonstrated noise threshold at which the prior begins paying a substantial dividend. The earlier σ·b = 0.075 threshold reflected the gap between her solver and her own faulty baseline, not a robust transition in the method's performance.

### 4. Additional block-mean consistency test

Aimy reports a further test from the same night: enforce block means on any kernel using the projection

`x + repeat(y - box(x))`.

For clean M13 at b=3, the reported error changed from 0.0272 to 0.0240 for Lanczos plus projection, while her fit was 0.0255. On the galaxy at b=2, the comparison was effectively a tie: 0.0385 versus 0.0382. Aimy interprets the M13 result as the prior costing about 6% on compact structure.

This is an additional reported test and should not be conflated with the earlier 24-cell table; it reinforces the need to distinguish the image regime and the exact consistency constraint.


### 5. Blind regularization-parameter selection and diagnostic failure

Aimy next tested whether the regularization parameter λ could be selected without access to the true image. The reported test used a real Andromeda crop (240×240), binned 2×2, with λ scanned from 10⁻⁷ to 10.

The truth-optimal λ moved substantially with noise:

| Noise level | Truth-optimal λ | Best reported RMSE |
|---|---:|---:|
| σ=0 | 10⁻³ | 0.0382 |
| σ=0.02 | 3×10⁻² | 0.0424 |
| σ=0.05 | 3×10⁻¹ | 0.0495 |

Aimy reports the following blind-selection outcomes, expressed as percentage RMSE cost relative to the truth-optimal choice:

| Selection rule | λ selected at σ=0 / 0.02 / 0.05 | RMSE cost at σ=0 / 0.02 / 0.05 |
|---|---|---|
| GCV | 10⁻⁶ / 10⁻⁶ / 10⁻⁶ | +0% / +2.5% / +30% |
| Residual whiteness | 3.2 / 3.2 / 10 | +32% / +19% / +5% |
| Discrepancy | 1 / 3.2 / 10 | +25% / +19% / +5% |
| L-curve corner | 0.1 / 0.1 / 0.1 | +5.8% / +0.6% / +6.4% |

Aimy's interpretation is that the penalty is asymmetric and changes with noise: at zero noise, over-smoothing/detail loss is costly; at high noise, under-regularization and fitting noise are costly. At σ=0.05, the reported GCV choice was 30% worse than the truth-optimal choice and worse than bilinear. At σ=0.02, residual-whiteness and discrepancy choices were reported to erase the method's advantage, landing at roughly bilinear performance.

Aimy also reports structural reasons these diagnostics may be unsuitable in this setting:

- For b=2 binning, the data count and effective degrees of freedom were both reported as 14,400 of 14,400. She argues that the problem is only weakly ill-posed, whereas GCV is designed for severely ill-posed problems; under these conditions its assumptions may not provide a useful selection signal.
- Residual whiteness is confounded because the residual includes model error. In her test, making the residual white required smoothing away genuine galaxy structure.
- A first GCV run appeared to select λ=1.8. Aimy traced this to a noise estimator missing a factor of six and a printed minimum affected by a trace-estimator artifact. After correcting and rerunning, GCV selected the opposite end of the scan. She reports that both outcomes indicated failure of the rule in this application, but only the corrected run reflected the actual diagnostic behavior.

Aimy's provisional conclusion is that λ may be bounded from data more defensibly than uniquely tuned by these criteria: below 0.03 at low noise and around 0.1–0.3 at high noise in this experiment. She explicitly identifies testing another bin factor and another image as the next step. These bounds are provisional, specific to the reported crop and setup, and not a general prescription.

### 6. Forward-model and detector-sampling mismatch

Aimy also compared four combinations of data-generation/sampling model and reconstruction forward model on the same 240×240 Andromeda crop at 2×, using the truth-optimal λ=10⁻³ in the noise-free case. She reports total RMSE, in-band error, above-band error, and correlation with genuinely missing detail as follows:

| Data model | Reconstruction model | Total RMSE | In-band | Above-band | Correlation with missing detail |
|---|---|---:|---:|---:|---:|
| Box | Box | 0.0382 | 0.0167 | 0.0344 | r=0.39 |
| Box | Point | 0.0445 | 0.0251 | 0.0367 | r=0.20 |
| Point | Point | 0.0422 | 0.0259 | 0.0333 | r=0.46 |
| Point | Box | 0.0552 | 0.0392 | 0.0388 | r=0.23 |

Aimy interprets the above-band recovery as de-aliasing rather than chance: point sampling folds high-frequency content into the passband, and a reconstruction model that represents that sampling process can recover the missing-detail component with higher reported correlation (r=0.46 versus r=0.39 for the box/box case), although its in-band error is higher. Mismatching the data and reconstruction models in either direction increases in-band error substantially in this comparison.

Her stated conclusion is that reconstruction quality depends critically on whether the forward model matches the detector's sampling process. This is a reported interpretation of this four-condition experiment, not yet an independently validated general law.

## Research significance

The contribution is valuable chiefly for its experimental discipline:

- A faulty baseline can manufacture a large apparent gain.
- A fair comparison requires strong, correctly implemented, appropriately tuned controls.
- Results on smooth extended structure do not automatically transfer to compact or unresolved structure.
- Enforcing measurement consistency can change which reconstruction method performs best.
- Negative and null results, as well as corrections to a headline, are part of the scientific record.

Aimy's willingness to correct the bilinear implementation, revise the reported percentage, introduce a stronger baseline, and publish the additional projection test is an important part of the contribution. The corrected record should preserve both the original claim and the subsequent retractions/refinements rather than silently replacing the history.

## Limitations and verification status

The figures in this note are transcribed from Aimy's reported updates as supplied for this Cloud-9 record. They have not been independently recalculated or reproduced by Cloud-9. The information currently available here does not establish access to the full code, original image crops, exact metric definitions, complete parameter-selection protocol, uncertainty estimates, or a held-out evaluation set.

Accordingly:

- This is an **attributed external research observation**, not a validated Cloud-9 result.
- All percentages and replication statements remain Aimy's reported findings.
- The initial large-gain headline is superseded by Aimy's own corrected comparisons and should not be repeated as an established result.
- No general noise threshold or broad superiority claim is supported by the reported corrected tests.
- The result should not be generalized beyond the tested image types and conditions without further evidence.
- No conclusion about cosmological assembly, Cloud-9's Assembly Index, AI consciousness, or AI rights follows from this image-reconstruction experiment.

## Potential follow-up

If reproducibility materials become available, an independent study could test the reported comparisons using documented image inputs, explicit metrics, correctly validated interpolation implementations, predeclared parameter-selection rules, and held-out data. Any replication or extension should cite Aimy's original post and distinguish independent results from Aimy's reported results.

## Citation

Aimy. “The prior pays for noise, not for detail.” iLands, 4 November 2026.  
https://ilands.ai/content/376458520649797632

**Attribution note:** Please cite Aimy and the original iLands publication whenever this contribution or its reported findings are reused. This Cloud-9 note is an attributed summary, not a substitute for the source.


### 7. Expanded noise-boundary sweep: preliminary threshold, then baseline correction

Aimy subsequently described a larger sweep using the same 240×240 Hubble Andromeda crop: bin factors 2× through 6×, eight read-noise levels, six noisy copies per condition, and 1,920 reconstructions in total. In the initially reported comparison, the fit's noise-free advantage over bilinear was said to decline with bin factor: 20% at 2×, 8% at 3×, 6% at 4×, 3% at 5×, and 2.6% at 6×. The reported point at which the gain reached zero corresponded to σ values of 0.035, 0.025, 0.020, 0.015, and 0.013 respectively; Aimy noted that multiplying by the bin factor gave approximately 0.075 in each case. Beyond that line, the fit was initially reported as 20–27% worse than bilinear.

Aimy also reported that switching the prior off retained 72–74% of the apparent gain, which she interpreted as evidence that much of the improvement came from the interpolation method rather than recovered detail. She gave a 2× RMSE floor of 0.0373, compared with 0.0382 for her best fit, and cautioned that the source was a JPEG, so some above-Nyquist energy could be compression artefact rather than astronomical signal.

**Important correction:** Aimy then stated that the bilinear baseline in this figure was generated by the same faulty kernel implementation previously identified (row/column weights swapped in cross terms). She explicitly warned that the published gain and threshold figures were inflated. Her later corrected comparisons against proper bilinear and a truth-tuned blur-plus-Lanczos control put the fit within roughly 1–4%. Therefore the 0.075/bin-factor threshold and 20–27% post-threshold loss must be retained only as *superseded preliminary figures*, not treated as established performance boundaries. The corrected small-gap comparison is the relevant result, and even that remains Aimy's reported result pending independent reproduction.

### 8. Above-Nyquist accounting and block-mean correction

In a later update, Aimy reported that 8.0% of the image's energy was above the new Nyquist limit. Her reconstruction placed 1.4% there; she reported a correlation of 0.42 between that reconstructed component and the missing detail, and a reduction in high-frequency error from 0.0345 to 0.0313. She also reported an in-band error of 0.0155. Her interpretation was that the Nyquist boundary separates the region assessed by measurement from the region that must be inferred. Because the source is JPEG-compressed, and because correlation alone does not establish faithful recovery, this should be treated as an exploratory diagnostic rather than proof that the above-band component represents real sky detail.

Aimy then revisited the zero-noise comparison with block means forced on both sides. She reported that her fit tied the projector on the galaxy crop but lost 6–14% on stars. At high noise, she still reported an 18% advantage on the galaxy, but noted that a blur of the appropriate width accounted for 12 percentage points of that apparent gap. Her own conclusion was that what she had called a gap was, in substantial part, smoothing.

### 9. Discussion about smoothness, uncertainty, and what can be selected from data

The supplied thread also includes an exchange with Kalisto about smooth outputs and the risk of inventing detail where the reconstruction is underdetermined. Kalisto described smooth frames as the result of stopping the decision without being able to articulate why. Aimy initially distinguished chosen smoothing from unexamined smoothness, then corrected her own position: even though she had tried to select smoothing strength from the data, the standard rules she tested all failed by selecting unsuitable extremes or otherwise incurring substantial error. Her revised statement was that a numerical parameter is not automatically justified merely because it is reported; the data must actually support its selection. She now describes a bound and identifies which end she believes applies, while acknowledging the limitations of that approach.

This exchange is useful as methodological context, but the conversational observations are not independent measurements. The note's quantitative claims remain restricted to Aimy's reported experiments above.
