# 61 Cygni — Simulated Targeted Beacon, Link & Detection Report

**Status: SIMULATION. This is a detectability study of a hypothetical beacon, not a detection of any signal from 61 Cygni.** Generated October 10, 2026 (Kimi/Gemini, from the Cloud-9 research pipeline).

## Scenario

A tidally-locked habitable-zone planet at 0.39 AU around 61 Cyg A (11.4 ly) transmits a 1-Hz wide beacon at the 21-cm hydrogen line (1420.405751 MHz), EIRP = 3e10 W — near the Breakthrough Listen GBT detection floor at this distance. Receiver modeled as GBT-class (SEFD 10 Jy), 300 s integration.

## Key numbers

| Quantity | Value |
|---|---|
| Distance | 3.496 pc / 11.4 ly |
| Received flux density | 20.5 Jy in 1 Hz |
| GBT detection floor (10σ, 300 s) | ~4.1 Jy |
| Post-integration SNR | 50 (coherent sim mean 140) |
| Orbital velocity | 39.3 km/s |
| Max orbital Doppler drift | −0.125 Hz/s |
| Frequency sweep per 300 s obs | −37.5 Hz across 37 fine channels |

## Interpretation (from the report)

- A civilization even slightly ahead of ours (Kardashev K≈0.5) beaming deliberately toward us is trivially detectable: the 20.5 Jy received is five times the GBT 10-sigma floor.
- The Doppler signature is the discriminator: a steady −0.125 Hz/s drift from orbital acceleration is exactly what turboSETI-style de-drift searches flag as non-terrestrial, since RFI sits still in the topocentric frame.
- Tidal locking means rotation contributes almost nothing — the drift tracks the 108-day orbit, repeating identically each period.

## Files

| File | Contents |
|---|---|
| `beacon_61cyg_report.pdf` | Full link-budget and detection report |
| `beacon_61cyg_timeseries.csv` | 300 one-second cells: peak frequency + excess power sigma |
| `beacon_61cyg_sonified.wav` | Sonified beacon signal |

Connects to: [`docs/61-cygni-thermodynamic-horizon.md`](../../docs/61-cygni-thermodynamic-horizon.md) — the quiet-thermodynamic-maturity argument for why mature intelligence might only be findable by deliberate, in-situ or narrowly-targeted search.
