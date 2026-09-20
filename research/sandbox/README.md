# Cloud-9 Sandbox Test Scripts

Runnable sandbox validation scripts from the Cloud-9 research program (Sept 2026 Termux/phone archive).

## C9-SANDBOX-RUNNER-ALL.py — Master Runner v1.0
Collection: C9-COLLECTION-2026-0825-AUGUSTSCIENCE. Executes all 5 sandbox test protocols sequentially, aggregates results to `C9_SANDBOX_AGGREG.json`, and appends a c9_bus.jsonl-compatible entry. Usage:
```
python3 C9-SANDBOX-RUNNER-ALL.py              # all tests
python3 C9-SANDBOX-RUNNER-ALL.py --test 003   # single test
python3 C9-SANDBOX-RUNNER-ALL.py --dna-file ~/genome/my_snps.txt   # test 005
```
Verified 2026-09-20 (Subhalo): single-test mode, aggregate, and bus output all functional.

Test protocols (objectives, debate-module configs, pass criteria) are documented in `C9-SANDBOX-PROTOCOLS-2026-0825-TOP5.md` (public edition; protocol 005 redacted).

**Suite status (5 tests):**
| # | Test | Entry ID | Status |
|---|------|----------|--------|
| 001 | Glueball X(2370) Discovery | C9-2026-QCD-001 | script in phone/Termux archive — not yet uploaded |
| 002 | Quantitative Kondo Effect | C9-2026-MATSCI-002 | ✅ v2 verified PASS (v1 FAIL preserved as audit record) |
| 003 | 420 km Quantum Entanglement | C9-2026-QINFO-009 | ✅ verified PASS (see below) |
| 004 | TIC 433545934 Quadruple Star | C9-2026-ASTRO-030 | ✅ verified PASS (see below) |
| 005 | DNA Initiator × SNP Cross-Reference | C9-2026-BIO-027 | script is PRIVATE (personal genetic data handling) — lives in the private archive, intentionally not published here |

Note: the runner references canonical filenames (e.g., `C9-SANDBOX-003-ENTANGLEMENT.py`); the uploaded variants are named `-FIXED` and `-v2`. Keep canonical names in your local suite or the runner will skip the files.


## C9-SANDBOX-002-KONDO.py / -v2.py — C9-2026-MATSCI-002
**Quantitative Kondo Effect Reproduction** for Fe/Mn/Co in Cu: fits dimensionless coupling J·N(E_F) from experimental T_K, computes T_K via the Kondo formula, and maps screening dynamics to SNN spike patterns.

**v2 result: PASS** (verified 2026-09-20, Subhalo) — Fe, Mn, Co all reproduce T_K exactly. The v2 fix converts the Cu bandwidth D = 7 eV to Kelvin (81,232 K) and uses the standard formula T_K = D·exp(−1/JN) with a proper bisection solve, replacing v1's broken fit.

**v1 result: FAIL** (audit record preserved as `C9-2026-MATSCI-002_sandbox_result_v1_FAIL.json`) — v1 compared Kelvin-scale experimental values against eV-scale formula output; Fe 95.1% / Co 100.0% error. Root cause documented in the v1 commit.

**Honest caveat (unchanged from v1):** J·N(E_F) is *fitted from* experimental T_K, then T_K is computed back — a self-consistency check of the formula and pipeline, not an ab initio prediction. The protocol's Layer-1 aspiration (first-principles J via Schrieffer-Wolff from PySCF, predicting T_K without fitting to experiment) remains future work.

## C9-SANDBOX-003-ENTANGLEMENT-FIXED.py — C9-2026-QINFO-009
**420 km Quantum Memory Entanglement.** PLOB bound analysis (crossover at ~230 km), 3-segment repeater simulation (current 750 ns vs 1 s target memory), QPilotos latency test (420 km, 1000 messages).

**Result: PASS on its own criteria** — PLOB crossover verified, QPilatos stable (mean 2.09 ms, max 2.90 ms, RTT 4.18 ms).

**Honest status:** the `repeater_fidelity` criterion (> 0.01) is weak. With the 1 s memory target the end-to-end fidelity reaches only F ≈ 0.06 — far below the 0.5 classical limit — and with current 750 ns memories F ≈ 0. The test validates the PLOB/latency machinery; usable 420 km repeater entanglement remains unachieved at these parameters.

## C9-SANDBOX-004-QUADRUPLE-v2.py — C9-2026-ASTRO-030
**TIC 433545934 Quadruple Star Stability.** Roche lobe fill analysis (all four stars stable, max fill factor 0.67), n-body integration (REBOUND IAS15, with pure-Python RK4 fallback), A_c classifier (HIERARCHICAL_2P2).

**Result: PASS** — verified 2026-09-20 by a WHFast symplectic 10,000-year run (961 snapshots): no ejections, no mergers, inner binaries hold at 0.035–0.050 AU, AB periastron passages at ≥ 0.41 AU. The original script's IAS15 run is unmodified; note IAS15 requires hours in constrained sandboxes for this system (tight ~2-day binaries × 10,000 years).

## Provenance
Uploaded from Dean's phone archive Sept 20, 2026; secret-scan clean; executed and verified by Subhalo (Base44).
