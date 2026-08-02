from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

# Vercel Python serverless entrypoint.
# MongoDB (via Motor) is an external managed service, so no local/tmp
# filesystem setup is required here as it was for the old SQLite fallback.
__all__ = ["app"]
