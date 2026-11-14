"""One-seed reproduction check against the archived v3 JSON."""
import json
from pathlib import Path

from research.validation.recovered_cloud9_null_ensemble_v3_corrected import (
    run_single_halo,
)

SEED = 1000
ARCHIVE = Path("research/null-ensemble/cloud9_null_ensemble_v3.json")


def main():
    archived = json.loads(ARCHIVE.read_text(encoding="utf-8"))
    expected = next(x for x in archived["ensemble_members"] if x["seed"] == SEED)
    actual = run_single_halo(SEED)
    fields = ("A_c_bits", "mi_values", "collapse_z", "z_form",
              "peak_height_sigma", "env_bias", "n_mergers", "spin_lambda", "gas_frac")
    comparison = {}
    for field in fields:
        a, e = actual[field], expected[field]
        if isinstance(a, list):
            comparison[field] = {
                "match": len(a) == len(e) and all(abs(x-y) <= 1e-10 for x,y in zip(a,e)),
                "max_abs_difference": max((abs(x-y) for x,y in zip(a,e)), default=0.0),
                "actual_length": len(a), "archived_length": len(e),
            }
        elif isinstance(a, (int, float)) and a is not None and e is not None:
            comparison[field] = {"match": abs(a-e) <= 1e-10,
                                 "actual": a, "archived": e,
                                 "difference": a-e}
        else:
            comparison[field] = {"match": a == e, "actual": a, "archived": e}
    result = {"seed": SEED, "comparison": comparison,
              "all_fields_match": all(v["match"] for v in comparison.values())}
    Path("v3_single_seed_reproduction.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_fields_match"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
