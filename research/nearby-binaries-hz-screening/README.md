# Nearby Binaries HZ Screening — 61 Cyg AB + 70 Oph AB

Joint habitable-zone screening grid for the two nearest Sun-like binary systems, generated October 10-11, 2026. Companion to the news analysis "Search For Alien Worlds Narrows Around Two Stars Just 16 Light-Years Away" (Oct 2026): a century of radial-velocity and astrometric monitoring has ruled out giant planets in the habitable zones of both binaries.

## Files

| File | Contents |
|---|---|
| `planet_grid_2systems.csv` | Orbit-by-orbit grid for all four stars (61 Cyg A/B, 70 Oph A/B): semi-major axis, effective flux, equilibrium temperature, period, HZ classification |
| `eccentricity_test_2systems.csv` | Kozai-Lidov eccentricity stress test for both binaries: mutual inclination vs peak eccentricity vs time in habitable flux |

Per-system detail: [`research/70-ophuchi/`](../70-ophuchi/) and [`research/61-cygni-beacon/`](../61-cygni-beacon/).

## Sources

- Li et al., "A Century of Radial Velocity and Astrometric Monitoring of 70 Oph AB", *ApJ*, doi:10.3847/1538-4357/ae9f52
- "Assessing Planetary Stability and Long-Term Habitability in Nearby Stellar Binaries: 70 Oph, 36 Oph, gamma Leo", arXiv:2608.13243 (flux criteria 0.2–1.1 S⊕)

**Caveat:** simplified analytic screening, not full N-body integration. No planets have been detected in either system.
