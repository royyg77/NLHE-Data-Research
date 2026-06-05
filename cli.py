"""
cli.py — command-line entry point.

Reads available studies from the registry (pipeline/registry.py) and runs the
selected study's named outputs through study.run(), which returns the
analysis-ready DataFrames (the pandas cleanup lives in each study, not here).

The flag names match the README and don't change as studies are added:
  --study, --stake, --min-hands, --output, --list.
"""

import argparse

from pipeline.core.config import default_min_hands
from pipeline.core.runner import available_stakes
from pipeline.registry import get_study, studies_by_category, study_names
from pipeline.core.io import save_results



DEFAULT_MIN_HANDS = default_min_hands()


def list_studies():
    print("Available studies:\n")
    for category, studies in studies_by_category().items():
        print(f"[{category}]")
        for study in studies:
            print(f"  {study.name}")
            print(f"      {study.description}")
            print(f"      outputs: {', '.join(study.outputs)}")
        print()
    try:
        stakes = available_stakes()
        print("Known stakes (bb_size):")
        print("  " + "  ".join(f"{s:.2f}" for s in stakes))
    except Exception as e:
        print("Known stakes (bb_size): unavailable (could not reach database)")
        print(f"  ({type(e).__name__})")
    print('\nUse --stake all (default) for every eligible stake.')
    print("Use --output <name> to run a single output (default: all).")


def run_study(study_name, stake_input, min_hands, output_names, save=False):
    study = get_study(study_name)

    # Decide which outputs to run.
    selected = output_names if output_names else list(study.outputs)
    outputs = {}

    for name in selected:
        print(f"\n=== {name} ===")
        # study.run pulls only the params each output declares; passing
        # min_hands here is harmless for outputs that don't use it.
        df = study.run(name, stake_input, min_hands=min_hands)
        print(df.to_string(index=False))
        outputs[name] = df
    
    if save:
        out_dir = save_results(study.name, outputs)
        print(f"\nResults saved to {out_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Run an NLHE population-tendency study against your PT4 database."
    )
    parser.add_argument("--study", help="Which study to run (see --list).")
    parser.add_argument(
        "--stake", nargs="+", default=["all"],
        help='Stake bb_size value(s), or "all". Default: all.',
    )
    parser.add_argument(
        "--min-hands", type=int, default=DEFAULT_MIN_HANDS,
        help=f"Minimum hands threshold (default: {DEFAULT_MIN_HANDS}).",
    )
    parser.add_argument(
        "--output", nargs="+", default=None,
        help="Which output(s) to run by name. Default: all. See --list.",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Show available studies, outputs, and stakes, then exit.",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to results/<study>/latest/ (default: results are printed only).",
    )

    args = parser.parse_args()

    if args.list:
        list_studies()
        return

    if not args.study:
        parser.error("--study is required (or use --list to see options).")
    if args.study not in study_names():
        parser.error(f"unknown study '{args.study}'. Use --list to see options.")

    # Validate --output names against the chosen study's declared outputs.
    if args.output:
        study = get_study(args.study)
        bad = [o for o in args.output if o not in study.outputs]
        if bad:
            parser.error(
                f"unknown output(s) {bad} for study '{args.study}'. "
                f"Valid: {', '.join(study.outputs)}"
            )

    run_study(args.study, args.stake, args.min_hands, args.output, save=args.save)


if __name__ == "__main__":
    main()


