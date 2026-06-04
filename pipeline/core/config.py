"""
pipeline/core/config.py

Loads non-secret defaults from config/settings.yaml. Secrets (DB credentials)
stay in .env and are handled in db.py -- nothing sensitive lives here.

Front-ends read defaults through this module instead of hardcoding them, so a
change to the pool's stakes or the default min-hands is a one-line edit in the
YAML, not a code change.
"""

from pathlib import Path

import yaml


# config/ sits at the project root, one level above pipeline/
_SETTINGS_PATH = Path(__file__).resolve().parents[2] / "config" / "settings.yaml"


def load_settings():
    """Read settings.yaml into a dict. Returns {} if the file is missing."""
    if not _SETTINGS_PATH.exists():
        return {}
    with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}



def default_min_hands():
    """Default minimum-hands threshold."""
    return load_settings().get("default_min_hands", 10000)


