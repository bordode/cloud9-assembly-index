# Cloud-9 Causal Closure Module

For Termux / Python execution. Analyzes any system for causal closure properties.

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
- Final verdict: Is Alive? Is Conscious?

## Thresholds

| Threshold | Score Required | Meaning |
|-----------|---------------|---------|
| LIFE | >60 | Causal closure sufficient for life |
| MAINTENANCE | >50 | Self-maintenance loop functional |
| PERSISTENCE | >40 | Information preservation over time |
| CONSCIOUSNESS | All above + info_pres > 40 | Cloud-9 consciousness criterion |

## Key Insight

Complexity (assembly proxy) is necessary but insufficient. Causal closure is the distinguishing criterion between living and non-living systems.
