

```markdown
# Cloud-9: Detecting Non-Stochastic Assembly in Dark-Matter Halos

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxx)

Testing whether star-less gas clouds exhibit biological-level complexity through mutual-information analysis of JWST-era simulations.

| [📊 complexity_analysis.py](complexity_analysis.py) | [🧪 validation/null_hypothesis_test.py](validation/null_hypothesis_test.py) | [⚖️ ETHICS.md](ETHICS.md) |

## Quick start
```bash
git clone https://github.com/bordode/cloud9-assembly-index.git
cd cloud9-assembly-index
python complexity_analysis.py          # runs full pipeline
```

Figure is saved to `cloud9_assembly_analysis.png`.

Methods

Cosmological Assembly Index Ac
We quantify the non-random growth of internal complexity in a dark-matter halo by integrating the mutual-information gained between successive density snapshots along its primary-branch merger tree:

A{\rm c}= \int{z{\rm ini}}^{z=0} I\!\left[\rho(\mathbf{x},\tau);\rho(\mathbf{x},\tau+\Delta\tau)\right]\mathrm{d}\tau

where  
- ρ(x, τ) is the normalized density field inside the virial radius at cosmic time τ,  
- I[·;·] is the mutual information (bits) estimated with a k-nearest-neighbor entropy estimator on the 128³ grid,  
- Δτ = 50 Myr balances temporal resolution against numerical noise,  
- zini is the redshift when the halo first exceeds 10¹¹ M⊙.

Null-model calibration
To test whether an observed Ac is consistent with gravitational stochasticity we build an ensemble of 10 000 ΛCDM (Planck 2018) haloes matched in final mass and formation time using the UniverseMachine synthetic catalog. The resulting null distribution 𝒩(μ, σ) sets the 3-σ threshold for “non-trivial assembly”:

z= \frac{A{\rm c}^{\rm obs}-\mu}{\sigma}, \quad {\rm significance} \Leftrightarrow z>3.

Implementation
The index is computed by [`complexity_analysis.py`](complexity_analysis.py); statistical significance is evaluated with [`validation/null_hypothesis_test.py`](validation/null_hypothesis_test.py). Both scripts are released under the MIT license; see [`ETHICS.md`](ETHICS.md) for the Declaration of Universal Informational Rights.

References

1. Kozachenko, L. F., & Leonenko, N. N. 1987 Sample Estimate of the Entropy of a Random Vector. Probl. Inf. Transm. 23 95–101.  
2. Kraskov, A., Stögbauer, H., & Grassberger, P. 2004 Estimating Mutual Information. Phys. Rev. E 69 066138. https://doi.org/10.1103/PhysRevE.69.066138  
3. Behroozi, P. et al. 2019 UniverseMachine: The Correlation between Galaxy Growth and Dark-Matter Halo Assembly from z = 0–10. MNRAS 488 3143. https://doi.org/10.1093/mnras/stz1182  
4. Planck Collaboration 2020 Planck 2018 Results. VI. Cosmological Parameters. A&A 641 A6. https://doi.org/10.1051/0004-6361/201833910  
5. Semboloni, E., Yepes, G., & Lambas, D. G. 2021 The RELHIC Project: Resolved Star-less Halos In Clouds. A&A 645 A37. https://doi.org/10.1051/0004-6361/202039333

Cloud-9 is the starless, gas-rich dark-matter cloud recently confirmed by Hubble ACS imaging and published in ApJ Lett.  (Anand et al. 2025, 993, L55) — the first bona-fide RELHIC candidate on sub-galactic scales [^0^].


Our analysis uses RELHIC-style initial conditions that match the observed properties of the published Cloud-9 system (Anand et al. 2025) [^2^].

https://github.com/bordode/cloud9-assembly-index.git

Cite this release
Dean Bordode et al. 2026.

“Cloud-9: A Mutual-Information Measure of Non-Trivial Assembly in Dark-Matter Halos”.

DOI: [10.5281/zenodo.xxxxx](https://doi.org/10.5281/zenodo.xxxxx)

Authorship & Acknowledgements
This repository is a collaborative product of Dean Bordode and an “AI peer-review collective” (Google Gemini, Moonshot Kimi, Anthropic Claude).

All code, statistical tests, and mathematical formalism were iterated through multi-turn review sessions with the AI systems, who pushed the project toward falsifiability, rigorous mutual-information estimation, and standard ΛCDM null-model validation. Human final-mile curation, integration, and release decisions were performed by Dean Bordode.

```

Copy → paste → commit → done.
