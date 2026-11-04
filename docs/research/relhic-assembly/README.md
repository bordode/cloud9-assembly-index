# Cloud-9 (M94 RELHIC) — Assembly Index Parameter Set

**Source:** Google Drive, `relhic_cloud9_params.json` and `README.md` (both created 2026-11-02).
**Status:** Parameters captured. **Calculation engine not yet located** — see Gap below.

## Purpose

Parameterise the Assembly Index (`A_c`) framework for **Cloud-9 near M94**, the massive
starless dark matter halo candidate reported from FAST, VLA, and HST observations. The
framework's claim structure is binary at the threshold level:

```
Pure dark matter halo + gas (A_c < 15)   ->  abiotic / primordial RELHIC
Baryonic self-collapse / star formation  ->  complex ordered system
```

The `A_c` baseline of 15.0 in the parameter file is the discriminator between those
two branches, not a measured value.

## Empirical constants (`data/relhic_cloud9_params.json`)

| Field | Value | Meaning |
|---|---|---|
| `target` | Cloud-9 (M94 RELHIC) | Identifier |
| `mass_hi_solar_masses` | 1.0e6 | HI mass, solar masses |
| `velocity_dispersion_km_s` | 12.0 | Gas velocity dispersion |
| `radius_kpc` | 1.4 | Halo radius |
| `distance_mpc` | 4.4 | Distance to M94 |
| `stellar_content` | starless | No detected stellar counterpart |
| `thermal_equilibrium` | true | Assumed thermal state of the gas |
| `assembly_baseline_a_c` | 15.0 | Discriminating `A_c` threshold |

These are the observation-side inputs. Nothing here is a Cloud-9-specific measurement of
`A_c` itself; the sequence depends on the coarse-graining scale chosen for the
multi-scale entropy calculation, which is where the framework's real sensitivity lives.

## Gap: referenced modules are missing

The accompanying README specifies three files:

- `relhic_assembly_calculator.py` — core `A_c` and multi-scale entropy engine
- `test_relhic_assembly.py` — pytest suite for physical thresholds and boundary conditions
- `data/relhic_cloud9_params.json` — this parameter file

Only the third exists. A search of Drive (filename match on `relhic`, `calculator`,
`assembly_calc`) and of the `bordode` GitHub account returned no copy of the calculator
or the test suite. Until the engine is located or rewritten, this repository holds the
**inputs and the specification**, not a runnable result. Per the provenance rules in the
top-level README, no `A_c` figure for Cloud-9 should be quoted as computed.

## Next step

Either recover the calculator from Termux/Colab history, or rebuild it against this
parameter file and the coarse-graining conventions already used in
`research/coarse-graining/`. A rebuilt version should ship with the pytest suite the
README promises, so the threshold logic is testable rather than asserted.
