"""NightRiver configuration — all path constants and tunables live here."""

import pathlib

# Project root is the directory that contains the nightriver/ package.
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
FIXTURES_DIR = PROJECT_ROOT / "fixtures"

SUBSCRIPTIONS_FILE = DATA_DIR / "subscriptions.json"

# Network
FETCH_TIMEOUT = 10  # seconds

# Cache limits
MAX_ITEMS_PER_FEED = 50


def ensure_dirs() -> None:
    """Create data directories if they don't exist yet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
