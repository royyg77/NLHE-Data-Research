"""
pipeline/registry.py

Discovers studies automatically so the front-ends (cli.py, dashboard.py) never
change as studies are added. It walks pipeline/studies/, imports each study
package's study.py, and collects every Study subclass it finds.

Adding a study is now zero edits here: just create
pipeline/studies/<your_study>/study.py with a Study subclass, and it shows up
in --list and the dashboard automatically.

Public API (unchanged from the explicit version, so the front-ends are stable):
  get_study(name)        -> a study instance by its .name
  study_names()          -> list of CLI-facing names
  all_studies()          -> list of study instances
  studies_by_category()  -> {category: [study, ...]}
"""

import importlib
import pkgutil

import pipeline.studies
from pipeline.core.base import Study


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
def _discover():
    """Import every `study` module found anywhere under pipeline/studies/ and
    return the Study subclasses defined across them.
 
    Studies may be nested at any depth -- e.g. both
    pipeline/studies/example/overview/study.py and
    pipeline/studies/postflop/flop_cbet/study.py are found. We walk the whole
    studies tree and import any module named `study`, then collect Study
    subclasses from it.
    """
    found = []
    seen = set()
 
    # walk_packages recurses through every subpackage under pipeline.studies.
    # prefix gives us the full dotted path; we only care about modules whose
    # final component is "study".
    prefix = pipeline.studies.__name__ + "."
    for modinfo in pkgutil.walk_packages(pipeline.studies.__path__, prefix):
        if modinfo.name.rsplit(".", 1)[-1] != "study":
            continue  # only the study.py modules carry Study subclasses
 
        try:
            module = importlib.import_module(modinfo.name)
        except ModuleNotFoundError as e:
            # If the module that failed is the study module itself, it
            # effectively doesn't exist -> skip. Any OTHER missing import
            # (e.g. an uninstalled dependency inside study.py) is a real
            # error and must surface, not vanish.
            if e.name == modinfo.name:
                continue
            raise
 
        for attr in vars(module).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, Study)
                and attr is not Study
                and attr.name  # skip half-defined classes with no name
                and attr not in seen
            ):
                seen.add(attr)
                found.append(attr)
 
    return found


def _study_classes():
    """Discover on each call so newly added study folders are picked up
    without restarting a long-running process (e.g. the dashboard)."""
    return _discover()


# ---------------------------------------------------------------------------
# Lookups for the front-ends
# ---------------------------------------------------------------------------
def all_studies():
    """Return instantiated study objects, one per discovered class."""
    return [cls() for cls in _study_classes()]


def get_study(name):
    """Return an instance of the study whose .name matches `name`.

    Raises KeyError with a helpful message if there's no match.
    """
    for cls in _study_classes():
        if cls.name == name:
            return cls()
    available = ", ".join(sorted(c.name for c in _study_classes()))
    raise KeyError(f"unknown study '{name}'. Available: {available}")


def study_names():
    """Just the CLI-facing names, for validation / --list."""
    return sorted(cls.name for cls in _study_classes())


def studies_by_category():
    """Group studies by their declared category, for grouped display.

    Returns {category: [study, ...]}, categories sorted alphabetically and
    studies within each category sorted by name, for stable output.
    """
    grouped = {}
    for study in all_studies():
        grouped.setdefault(study.category, []).append(study)
    for studies in grouped.values():
        studies.sort(key=lambda s: s.name)
    return {cat: grouped[cat] for cat in sorted(grouped)}