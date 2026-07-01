"""Hugging Face Spaces entrypoint.

HF Spaces (sdk: fastapi) imports this module and serves `app` on port 7860.
"""

from app.main import app

__all__ = ["app"]
