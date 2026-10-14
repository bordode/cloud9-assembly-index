# 70 Ophiuchi AB - Life-Prospect Assembly Index

A portable data package indexing the habitability screening of the 70 Ophiuchi AB
binary system (16.6 light-years away). Generated October 10, 2026.

## Contents

| File | Purpose |
|---|---|
| `70oph_assembly_index.json` | Structured index: system parameters, habitable zones, stress-test results, sources |
| `70oph_planet_grid.csv` | Orbit-by-orbit grid: semi-major axis, incident flux, equilibrium temperature, orbital period, HZ classification |
| `70oph_eccentricity_test.csv` | Kozai-Lidov stress test: mutual inclination vs peak eccentricity vs percent of time in habitable flux |

## Quick start in AWS Cloud9

1. Create or open a Cloud9 environment (Amazon Linux or Ubuntu image).
2. Upload the three files to your workspace root via **File > Upload Local Files**.
3. Inspect the index:

   ```bash
   python3 -m json.tool 70oph_assembly_index.json | less
   ```

4. Load into a script or notebook:

   ```python
   import json, pandas as pd
   idx = json.load(open("70oph_assembly_index.json"))["assembly_index"]
   grid = pd.read_csv("70oph_planet_grid.csv")
   print(idx["habitable_zones"]["70_Oph_A"])
   print(grid[grid.zone == "habitable zone"])
   ```

## Key results

- 70 Oph A: habitable orbits 0.75-1.25 AU, Teq 195-251 K, 253-544 day years, no tidal locking.
- 70 Oph B: habitable orbits 0.39-0.64 AU, Teq 198-254 K, 103-216 day years, likely tidally locked.
- Planets coplanar with the binary (< 39.2 deg) never undergo Kozai eccentricity cycling
  and remain in habitable flux 100% of modeled time; 45 deg misalignment still leaves ~85-91%.
- No giant planets exist in either habitable zone (century of radial velocity data).

## Sources

- Li et al., "A Century of Radial Velocity and Astrometric Monitoring of 70 Oph AB",
  Astrophysical Journal, doi:10.3847/1538-4357/ae9f52
- "Assessing Planetary Stability and Long-Term Habitability in Nearby Stellar
  Binaries: 70 Oph, 36 Oph, gamma Leo", arXiv:2608.13243 (flux criteria: 0.2-1.1 S_earth)

## Caveats

This is a simplified analytic screening, not a full N-body integration. Planet
formation in ~23 AU binaries is theoretically less efficient; stellar activity is
significant; and no planets have actually been detected in this system yet.
