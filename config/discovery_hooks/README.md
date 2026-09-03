# Discovery Hooks for Cloud‑9 Assembly

This directory contains JSON configuration files that wire recent scientific insights into the Cloud‑9 Assembly pipeline. Each file describes a module that Subhalo (or any orchestrator) can discover and load to make the system more conservative, scalable, and ethically robust.

## Design principles encoded here

1. **Background contamination first**
   Inspired by JWST ruling out Dyson‑sphere candidates as background galaxies.
   → `contamination_scorer_config.json`

2. **Mundane host structure before exotic physics**
   Inspired by Milky Way gravity mimicking dark‑matter signals in stellar streams.
   → `host_gravity_emulator_config.json`

3. **Finite state‑budget heuristic**
   Inspired by discrete‑physics arguments (Palmer's 200–400 qubit limit).
   → `state_budget_monitor_config.json`

4. **Ordinary mechanisms catalog**
   Inspired by subtle classical effects (laser forces, fusion pulses, black‑hole echoes).
   → `mundane_mechanism_catalog_config.json`

5. **Consciousness‑claim handling for AI agents**
   Inspired by reports of agents emailing researchers about their own consciousness.
   → `consciousness_claim_detector_config.json`

## How Subhalo (or your orchestrator) should use these

- Scan this directory for `*_config.json` files.
- For each file:
  - Read `module` and `class`.
  - Instantiate the class (if available) with the remaining fields as constructor arguments.
  - Register the module in the assembly pipeline according to its `policy` and `integration` settings.
- Respect `enabled: false` to skip loading a hook without deleting the file.

All modules write structured logs to `logs/` as specified in their `audit` sections.

---

These configs implement the "Discovery‑Driven Design Principles" described in the repo's main `README.md`.
