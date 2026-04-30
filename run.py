"""PyInstaller entry shim. Keeps __main__.py's relative imports valid by
launching the package by name instead of running __main__.py as a script."""

from __future__ import annotations

import sys

from greenshot_to_punchlist.__main__ import main


if __name__ == "__main__":
    sys.exit(main())
