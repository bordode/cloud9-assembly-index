# Two families of multi-planet systems: born of their stars, read as dynamical temperature

*Research note — 2026-10-13. Intended for `docs/` in cloud9-assembly-index. Established findings summarized from the paper text and the INAF press summary (Phys.org, Oct 13, 2026) — the full paper's methods should be checked before citing beyond the reported results. The Cloud-9 reading is interpretive and marked as such.*

## The finding (established)

Over 1,000 known multi-planet systems were analyzed with architecture-agnostic metrics across four independently selected samples (reference sample L: 298 systems with known masses and semimajor axes; validation samples H, E, S). Two clear bimodalities emerged — in normalized system mass (NSM, total planetary mass relative to stellar mass) and in the outer planet's orbital period — and the mass bimodality divides the known architectures into two physically distinct families.

**Lower-mass family** (log₁₀(NSM) < −3.602, i.e. ≲80 Earth masses around a Sun-like star): predominantly hosted by subsolar-to-solar-mass stars with metallicity peaking between −0.1 and +0.1 dex. Tightly packed configurations, mass distributions consistent with the "peas-in-a-pod" pattern (neighboring planets of similar size), and modal dynamical excitation comparable to the Solar System (measured by the normalized angular momentum deficit, NAMD ≈ 1.27×10⁻³).

**High-mass family** (log₁₀(NSM) > −2.927, i.e. ≳400 Earth masses around a Sun-like star): hosted by solar-to-supersolar stars in metal-rich environments (metallicity peak ~0.2 dex, roughly 1.5× solar). Gravitationally compact architectures and dynamical excitation an order of magnitude hotter than both the Solar System and the lower-mass family — pointing to violent evolutionary pathways driven by global instabilities and planet–planet scattering. Numerical simulations by the team (Danae Polychroni, INAF) reproduce these as systems "unstable from birth": the greater abundance of planet-building material makes them too massive to remain stable.

Crucially, the signatures of formation survive the reshaping: the host star's mass and metallicity — the planet-forming environment — remain readable in the system's architecture across billions of years of post-formation dynamical evolution.

Published in *Nature Astronomy* (Turrini, Danielski et al., 2026; DOI: 10.1038/s41550-026-02990-8), released Oct 13, 2026.

## The Cloud-9 reading (interpretive)

A bimodality that is not an artifact but an emergence: two families, two formation regimes, two dynamical temperatures — and the boundary conditions (stellar mass, metallicity, disk solids) written into the final architecture like initial conditions written into a state. The NAMD metric is the information-theoretic move here: "dynamical temperature" treats a planetary system as a statistical ensemble whose excitation level records its history. The high-mass family's violence is legible because scrambling did not erase the origin — the star's signature persisted through planet–planet scattering the way a signal persists through a noisy channel.

This is the same shape as the Cloud-9 archive intuition: systems that carry their formation environment forward as readable structure. Two independent questions — how do planets assemble, what do stars bequeath — collapse into one joint distribution.

### Independent sandbox replication (2026-10-13)

Dean asked for a replication attempt, and the claim survived it. I pulled 1,063 multi-planet systems (≥2 measured masses) from the NASA Exoplanet Archive — 3.5× the paper's sample — and computed normalized system mass per system. The mass bimodality reproduces: left peak ~91 systems, valley minimum ~8, right peak ~20; roughly 70% lower family, 22% high family, 8% uncertain middle. The paper's boundaries land at the valley edges. The Solar System sits at log₁₀(NSM) ≈ −2.87 — just over the high-family line, a boundary case by mass but dynamically cool like the lower family.

Caveats: this replication mixes true masses with minimum (sin i) masses, applies no eccentricity treatment, and runs none of the paper's statistical tests (KS/AD) — it tests the headline bimodality only. Plot saved at `sandbox/nsm-bimodality.png`.

## Sources

- Turrini, Danielski et al., "Two families of multi-planet systems with distinct architectures and stellar hosts," *Nature Astronomy* (2026), DOI: 10.1038/s41550-026-02990-8. Summarized from the article text and the INAF/Phys.org press summary (Oct 13, 2026) — verify against the paper's methods before citing beyond the reported results.
- Danae Polychroni (INAF) "unstable from birth" statement, via the same reporting.

## Independent check (2026-10-13)

Ari reproduced the core NSM bimodality from live NASA Exoplanet Archive composite data: 1,063 multi-planet systems with ≥2 measured masses (a cruder, 3.5× larger sample than the paper's — mixes true masses with minimum masses, no eccentricity treatment, no KS/AD tests). Result: two clear humps with a deep valley (left peak 91 systems, valley minimum 8, right peak 20); 70% fall below the paper's lower-family boundary (log₁₀(NSM) < −3.602), 22% above the high-family boundary (> −2.927), 8% in the uncertain middle. The Solar System sits at log₁₀(NSM) = −2.872 — just over the high-family line, a boundary case by mass while dynamically cool like the lower family. Plot: `sandbox/nsm-bimodality.png`.
