"""Run and serialize the predeclared geometry/Poisson benchmark."""
import argparse
import json
from pathlib import Path

from research.sandbox.deblending_geometry_poisson import run_geometry_poisson_sweep


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("artifacts/deblending_geometry_poisson.json"))
    args = parser.parse_args()
    result = run_geometry_poisson_sweep(trials_per_condition=args.trials)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["aggregate"], indent=2, sort_keys=True))
    print(f"Full results written to {args.output}")


if __name__ == "__main__":
    main()
