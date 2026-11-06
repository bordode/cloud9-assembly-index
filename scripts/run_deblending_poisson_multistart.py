"""Run the predeclared Poisson deterministic multi-start comparison."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.sandbox.deblending_poisson_multistart import run_multistart_sweep


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/deblending_poisson_multistart.json"))
    args = parser.parse_args()
    result = run_multistart_sweep(trials_per_condition=args.trials)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n",
                           encoding="utf-8")
    print(json.dumps(result["overall"], indent=2, sort_keys=True))
    print(json.dumps(result["paired_poisson_comparison"], indent=2, sort_keys=True))
    print(f"Full results written to {args.output}")


if __name__ == "__main__":
    main()
