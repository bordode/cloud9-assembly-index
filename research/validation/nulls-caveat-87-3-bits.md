# Caveat: which null does the 87.3-bit result get compared to?

*Filed 2026-11-14 after reading the subHalo science-context pack. This records a reported comparison that is not currently reproducible from anything checked in here.*

## What the repository says

- `research/null-ensemble/README.md`: synthetic semi-analytic null, N=100, μ = 58.06 bits, σ = 3.39 bits. Cloud-9 A_c = 87.3 bits gives z = +8.62, 0/100 exceedances. Already flagged: non-Gaussian null (Shapiro p = 0.0019), bootstrap 95% CI on z [7.91, 9.63], not a discovery claim, not validated against real IllustrisTNG multi-snapshot evolution.
- `research/validation/README.md`: also records a real-TNG100-1 radial comparison at z = 1011σ, marked **invalid** (different estimator and geometry).

## What the subHalo pack reports

A comparison against simulated CDM halos with a null mean of **95.97 bits**, giving **z = −1.25** for the same 87.3-bit value. On that comparison Cloud-9 is *below* the average simulated halo, i.e. **less** spatially complex than the null, not more.

The mean 95.97 does not appear anywhere in this repository, and no ensemble producing it is checked in.

## Why it matters

The 8.62 figures and the −1.25 figure describe the same measurement against different nulls. Only one of them supports a claim that Cloud-9 is an unusually high-assembly structure. Until the 95.97 ensemble is located and reproduced, the honest position is:

1. The 87.3-bit value is a measurement.
2. Against a semi-analytic synthetic null it is a large outlier.
3. Against simulated CDM halos it has been reported as slightly below the mean.
4. Neither comparison has been independently replicated.

## Outstanding

- Locate or reconstruct the ensemble giving mean 95.97 bits and document its estimator, sample size and geometry.
- If the two nulls differ in estimator (temporal MI vs spatial/radial), state plainly that they answer different questions and stop presenting them as one number.
- Amend any public summary that quotes 87.3 bits as evidence of excess complexity without this caveat.
