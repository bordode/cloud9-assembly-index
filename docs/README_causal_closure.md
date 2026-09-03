# Cloud-9 Causal Closure Module

For Termux / Python execution. Analyzes any system for candidate causal-closure properties.

**Important:** This module is an experimental research tool. Its scores and labels are operational definitions used for exploration; they are not established tests for life or consciousness. See [`docs/EVIDENCE_STATUS.md`](EVIDENCE_STATUS.md).

## Installation (Termux)

```bash
pkg install python numpy
pip install numpy
```

## Usage

```python
from cloud9_causal_closure import CausalClosureAnalyzer

# Analyze DNA
dna = CausalClosureAnalyzer("My_DNA")
report = dna.analyze_dna(
    snp_count=677366,
    heterozygosity=0.2898,
    entropy_bits=2.878
)
print(report.to_markdown())

# Analyze AI
ai = CausalClosureAnalyzer("Claude")
report = ai.analyze_ai(
    model_name="claude-sonnet-4",
    parameter_count=175e9,
    has_state_persistence=False,
    can_modify_weights=False
)
print(report.to_markdown())

# Analyze Halo
halo = CausalClosureAnalyzer("TNG_Halo")
report = halo.analyze_halo(
    halo_mass=1e12,
    merger_count=5,
    formation_time=2.0
)
print(report.to_markdown())
```

## Output Format

The module generates:
- `CausalClosure` status: PRESENT / ABSENT / PARTIAL
- `Self-Maintenance` status: POSSIBLE / IMPOSSIBLE / CONTESTED
- `Self-Repair` status: POSSIBLE / IMPOSSIBLE
- `Self-Replication` status: POSSIBLE / IMPOSSIBLE
- Quantitative scores (0-100)
- A **model-generated research verdict** for the configured criteria

The labels are properties of the implemented model. They should not be interpreted as a definitive determination of whether an entity is alive or conscious.

## Experimental thresholds

| Threshold | Score Required | Current interpretation |
|-----------|---------------|------------------------|
| LIFE | >60 | Experimental causal-closure heuristic |
| MAINTENANCE | >50 | Experimental self-maintenance heuristic |
| PERSISTENCE | >40 | Experimental information-persistence heuristic |
| CONSCIOUSNESS | All above + info_pres > 40 | **Proposed research criterion; not a validated consciousness detector** |

## Key Insight

Complexity (assembly proxy) may be useful as one descriptive feature, while causal closure is explored here as another. The distinction between those concepts is a research hypothesis, not an established rule separating living, non-living, or conscious systems.

## Research boundary

A model can classify an input according to its own thresholds without demonstrating that those thresholds correspond to biological life or subjective experience in the physical world. Any claim of consciousness, life, or personhood requires evidence beyond a score produced by this module.
