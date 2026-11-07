# Adaptive Poisson proposal expansion benchmark

## Question

Can a conditional expansion from the five highest-ranked residual proposals to ranks 6–10 recover the occasional source missed by the fixed top-five pool, while avoiding the nearly doubled fitting cost of an unconditional top-ten search?

## Methods

Three methods are evaluated on identical Poisson count observations:

1. **Top-five:** evaluate ranks 1–5 and choose the successful fit with lowest BIC.
2. **Fixed top-ten:** evaluate ranks 1–10 and choose the successful fit with lowest BIC.
3. **Adaptive top-five-to-ten:** evaluate ranks 1–5 first. If no successful fit lowers the current scene BIC, evaluate ranks 6–10. All candidates are fitted against the same unchanged accepted scene and residual map. Choose the lowest-BIC successful fit from the evaluated candidates and accept it only if it lowers current BIC.

The adaptive method does not use truth, source count, or truth proximity to trigger expansion. The BIC acceptance threshold and stopping rule remain unchanged.

## Paired design

- 27 synthetic trials: three per cell across geometry scales 0.8, 1.0, 1.2 and exposures 1.0, 0.1, 0.03.
- Fresh seed range begins at 20262050.
- Every method receives the same count image within a trial.
- Same pixel-integrated PSF family, Poisson objective, Pearson-residual matched-filter proposal score, 1 px nonmaximum suppression, parameterization, bounds, optimizer tolerances, BIC penalty and acceptance/stopping rules.
- Truth is withheld from detection and used only after each run for one-to-one Hungarian matching within 1 px.

## Primary outcomes

- Mean matched truths, missed truths, unmatched candidates and exact seven-source recoveries.
- Total proposal fits and total optimizer function evaluations, including the initial baseline fit.
- Adaptive expansion frequency.
- Number of expansions that rescue a step, defined as an expanded step where a rank 6–10 candidate is selected and accepted.
- Paired trial-level recovery differences against top-five and fixed top-ten.

## Interpretation limits

This is an exploratory 27-trial synthetic pilot, not a general detector benchmark or evidence of real astronomical performance. Repeated steps and sources within a scene are not independent observations. A rescued step means only that a lower-BIC candidate from ranks 6–10 was accepted under this synthetic setup; it does not establish that the source is physically identifiable in real data.
