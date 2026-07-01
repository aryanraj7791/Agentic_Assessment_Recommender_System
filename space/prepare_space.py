#!/usr/bin/env python3
"""Copy backend source into space/ for a standalone Hugging Face Space repo.

Usage (from repository root):
    python space/prepare_space.py

Then push the space/ folder contents to your HF Space Git repo:
    cd space && git init && git add . && git commit -m "Deploy to HF Spaces"
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPACE = Path(__file__).resolve().parent

COPY_DIRS = ["app"]
COPY_FILES = [
    ("data/shl_product_catalog.json", "data/shl_product_catalog.json"),
    ("requirements-prod.txt", "requirements.txt"),
    ("app.py", "app.py"),
]


def main() -> None:
    for directory in COPY_DIRS:
        src = ROOT / directory
        dst = SPACE / directory
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(
            src,
            dst,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
        )
        print(f"Copied {src} -> {dst}")

    for src_rel, dst_rel in COPY_FILES:
        src = ROOT / src_rel
        dst = SPACE / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")

    print("\nSpace folder is ready. Push space/ to your Hugging Face Space repository.")


if __name__ == "__main__":
    main()
