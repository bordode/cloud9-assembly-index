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

The most defensible takeaway is methodological: **baseline correctness and control tuning matter more than the apparent sophistication of the prior.** The reported results do not establish a general noise threshold at which the Laplacian prior becomes valuable.

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
