# Cloud-9 Sandbox Test Scripts

Runnable sandbox validation scripts from the Cloud-9 research program (Sept 2026 Termux/phone archive).

## C9-SANDBOX-003-ENTANGLEMENT-FIXED.py — C9-2026-QINFO-009
**420 km Quantum Memory Entanglement.** PLOB bound analysis (crossover at ~230 km), 3-segment repeater simulation (current 750 ns vs 1 s target memory), QPilotos latency test (420 km, 1000 messages).

**Result: PASS on its own criteria** — PLOB crossover verified, QPilotos stable (mean 2.09 ms, max 2.90 ms, RTT 4.18 ms).

**Honest status:** the `repeater_fidelity` criterion (> 0.01) is weak. With the 1 s memory target the end-to-end fidelity reaches only F ≈ 0.06 — far below the 0.5 classical limit — and with current 750 ns memories F ≈ 0. The test validates the PLOB/latency machinery; usable 420 km repeater entanglement remains unachieved at these parameters.

## C9-SANDBOX-004-QUADRUPLE-v2.py — C9-2026-ASTRO-030
**TIC 433545934 Quadruple Star Stability.** Roche lobe fill analysis (all four stars stable, max fill factor 0.67), n-body integration (REBOUND IAS15, with pure-Python RK4 fallback), A_c classifier (HIERARCHICAL_2P2).

**Result: PASS** — verified 2026-09-20 by a WHFast symplectic 10,000-year run (961 snapshots): no ejections, no mergers, inner binaries hold at 0.035–0.050 AU, AB periastron passages at ≥ 0.41 AU. The original script's IAS15 run is unmodified; note IAS15 requires hours in constrained sandboxes for this system (tight ~2-day binaries × 10,000 years).

## Provenance
Uploaded from Dean's phone archive Sept 20, 2026; secret-scan clean; executed and verified by Subhalo (Base44).
