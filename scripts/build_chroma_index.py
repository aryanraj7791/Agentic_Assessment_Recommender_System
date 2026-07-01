"""Build the ChromaDB vector index."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
from app.logging_config import configure_logging  # noqa: E402
from app.startup import initialize_app  # noqa: E402


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    initialize_app(settings)
    print(f"ChromaDB index ready at {settings.chroma_path}")


if __name__ == "__main__":
    main()
