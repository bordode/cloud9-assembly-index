"""Run the paired Poisson candidate-depth ablation."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.sandbox.deblending_poisson_candidate_depth import run_candidate_depth_ablation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed-start", type=int, default=20262000)
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/deblending_poisson_candidate_depth.json"))
    args = parser.parse_args()
    result = run_candidate_depth_ablation(
        trials_per_condition=args.trials, seed_start=args.seed_start
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items()
                      if key != "records"}, indent=2, sort_keys=True))
    print(f"Full ablation written to {args.output}")


if __name__ == "__main__":
    main()
