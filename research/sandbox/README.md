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
| 002 | Quantitative Kondo Effect | C9-2026-MATSCI-002 | ⚠️ verified FAIL — unit bug, see below |
| 003 | 420 km Quantum Entanglement | C9-2026-QINFO-009 | ✅ verified PASS (see below) |
| 004 | TIC 433545934 Quadruple Star | C9-2026-ASTRO-030 | ✅ verified PASS (see below) |
| 005 | DNA Initiator × SNP Cross-Reference | C9-2026-BIO-027 | script is PRIVATE (personal genetic data handling) — lives in the private archive, intentionally not published here |

Note: the runner references canonical filenames (e.g., `C9-SANDBOX-003-ENTANGLEMENT.py`); the uploaded variants are named `-FIXED` and `-v2`. Keep canonical names in your local suite or the runner will skip the files.


## C9-SANDBOX-002-KONDO.py — C9-2026-MATSCI-002
**Quantitative Kondo Effect Reproduction.** Fits effective exchange coupling J_eff for Fe/Mn/Co in Cu from experimental T_K, predicts T_K back via the analytical formula D·√(JN)·exp(−1/JN), and maps Kondo screening dynamics to SNN spike patterns.

**Result: FAIL** (verified 2026-09-20, Subhalo) — Fe: 95.1% error, Co: 100.0% error, Mn: 0.0% (circular pass).

**Root cause (diagnosed, not a Kondo-model failure):**
1. **Unit inconsistency:** `EXPERIMENTAL_TK` is in *Kelvin* (Fe 29 K, Co 300 K) but the analytical formula with D=7 eV returns T_K in *eV-scale* units. Values 29 and 300 exceed the formula's maximum reachable output (~12.8), so `brentq` finds no root and the fallback JN ≈ 1/|ln(T_K/D)| approximation is used, which does not reproduce the input.
2. **Circular validation:** J_eff is *fitted from* experimental T_K, then T_K is "predicted" back with the same formula. Even a perfect fit proves self-consistency only, not predictive power. Mn's 0.0% error is exactly this.
3. The protocol's original pass criterion (first-principles PySCF-derived J predicting T_K *without* fitting to experiment) is not what this script implements.

**Suggested fixes:** convert T_K to eV via k_B (8.617e-5 eV/K) before fitting; solve JN from the full transcendental equation numerically rather than the log-approximation; for genuine prediction, derive J via Schrieffer-Wolff from ab initio cluster calculations instead of fitting to experiment.

The SNN mapping section (τ_K extraction, 500×100 firing-rate reservoir) runs correctly and is preserved in the pattern JSON.

## C9-SANDBOX-003-ENTANGLEMENT-FIXED.py — C9-2026-QINFO-009
**420 km Quantum Memory Entanglement.** PLOB bound analysis (crossover at ~230 km), 3-segment repeater simulation (current 750 ns vs 1 s target memory), QPilotos latency test (420 km, 1000 messages).

**Result: PASS on its own criteria** — PLOB crossover verified, QPilatos stable (mean 2.09 ms, max 2.90 ms, RTT 4.18 ms).

**Honest status:** the `repeater_fidelity` criterion (> 0.01) is weak. With the 1 s memory target the end-to-end fidelity reaches only F ≈ 0.06 — far below the 0.5 classical limit — and with current 750 ns memories F ≈ 0. The test validates the PLOB/latency machinery; usable 420 km repeater entanglement remains unachieved at these parameters.

## C9-SANDBOX-004-QUADRUPLE-v2.py — C9-2026-ASTRO-030
**TIC 433545934 Quadruple Star Stability.** Roche lobe fill analysis (all four stars stable, max fill factor 0.67), n-body integration (REBOUND IAS15, with pure-Python RK4 fallback), A_c classifier (HIERARCHICAL_2P2).

**Result: PASS** — verified 2026-09-20 by a WHFast symplectic 10,000-year run (961 snapshots): no ejections, no mergers, inner binaries hold at 0.035–0.050 AU, AB periastron passages at ≥ 0.41 AU. The original script's IAS15 run is unmodified; note IAS15 requires hours in constrained sandboxes for this system (tight ~2-day binaries × 10,000 years).

## Provenance
Uploaded from Dean's phone archive Sept 20, 2026; secret-scan clean; executed and verified by Subhalo (Base44).
