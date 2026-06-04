"""
cli.py — command-line entry point.

Step-4 version: a thin argparse wrapper over the current flat SQL files.
It uses the flag names from the README (--study, --stake, --min-hands, --list)
so the interface stays stable, but for now the single study and its file paths
are hardcoded here. When the pipeline/ reorganization happens (step 5), the
hardcoded bits below get replaced by a registry lookup; the flags don't change.
"""

import argparse
import sys

from runner import run_sql_file, resolve_stakes


# ---------------------------------------------------------------------------
# Hardcoded study catalog (placeholder for the future registry).
# Each study maps a CLI name to the SQL files it runs and which params it needs.
# ---------------------------------------------------------------------------
STUDIES = {
    "flop-cbet-texture": {
        "description": "Flop c-bet frequency and sizing by board texture (v1.0)",
        "outputs": {
            "pool_overview":     "sql/v1_0/01_pool_overview.sql",
            "cbet_strategy":     "sql/v1_0/02_flop_cbet_strategy_by_texture.sql",
            "texture_frequency": "sql/v1_0/03_texture_frequency.sql",
        },
        "uses_min_hands": True,
    },
}

# Stakes known to exist in the data (for --list display only; not a filter).
KNOWN_STAKES = ["0.02", "0.05", "0.10", "0.30"]
DEFAULT_MIN_HANDS = 10000


def list_studies():
    print("Available studies:\n")
    for name, meta in STUDIES.items():
        print(f"  {name}")
        print(f"      {meta['description']}")
        print(f"      outputs: {', '.join(meta['outputs'])}")
    print("\nKnown stakes (bb_size):")
    print("  " + "  ".join(KNOWN_STAKES))
    print('\nUse --stake all (default) for every eligible stake.')
    print("Use --output <name> to run a single output (default: all).")


def run_study(study_name, stake_input, min_hands, output_names):
    study = STUDIES[study_name]
    params = resolve_stakes(stake_input)
    if study["uses_min_hands"]:
        params["min_hands"] = min_hands
 
    # Decide which outputs to run.
    if output_names:
        selected = output_names
    else:
        selected = list(study["outputs"])  # all of them
 
    for name in selected:
        path = study["outputs"][name]
        print(f"\n=== {name} ({path}) ===")
        df = run_sql_file(path, params)
        print(df.to_string(index=False))


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
 
    args = parser.parse_args()
 
    if args.list:
        list_studies()
        return
 
    if not args.study:
        parser.error("--study is required (or use --list to see options).")
    if args.study not in STUDIES:
        parser.error(f"unknown study '{args.study}'. Use --list to see options.")
 
    # Validate --output names against the chosen study.
    if args.output:
        valid = STUDIES[args.study]["outputs"]
        bad = [o for o in args.output if o not in valid]
        if bad:
            parser.error(
                f"unknown output(s) {bad} for study '{args.study}'. "
                f"Valid: {', '.join(valid)}"
            )
 
    run_study(args.study, args.stake, args.min_hands, args.output)
 
 
if __name__ == "__main__":
    main()


    