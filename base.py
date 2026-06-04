"""
pipeline/core/base.py

The Study contract. Every study subclasses Study and fills in the class
attributes + run(). The registry and front-ends only ever talk to this
interface, so they never need to know a study's internals.
"""

from pathlib import Path
import sys


class Study:
    # --- identity (the registry reads these to list/group studies) ---
    name = ""            # CLI-friendly id, e.g. "flop-cbet-texture"
    category = ""        # grouping label, e.g. "Single-Raised Pots"
    description = ""     # one-line summary for --list / dashboard

    # --- what the study accepts (CLI validates against this) ---
    params = []          # e.g. ["stake", "min_hands"]

    # --- what the study produces ---
    # name -> {"sql": <filename in this study's sql/ dir>, "params": [...]}
    # the per-output params list is what lets one output use min_hands and
    # another not -- the runner only passes what each output declares.
    outputs = {}

    def sql_dir(self):
        """Absolute path to this study's sql/ folder, resolved from the
        module file's own location so it works regardless of cwd."""
        module_file = sys.modules[self.__class__.__module__].__file__
        return Path(module_file).resolve().parent / "sql"

    def run(self, output_name, params):
        """Execute one named output and return its result (DataFrame and/or
        figure). Subclasses implement this -- typically: load the SQL for
        output_name, call runner.run_sql_file, then apply the stats/plotting
        that currently live in the notebook."""
        raise NotImplementedError