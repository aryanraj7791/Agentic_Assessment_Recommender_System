"""Pandas-based catalog preprocessing."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd

from app.catalog.loader import Assessment, Catalog, _repair_catalog_json


def preprocess_catalog(raw_path: str | Path) -> pd.DataFrame:
    """Load, repair, and normalize the SHL catalog into a clean DataFrame."""
    raw_text = Path(raw_path).read_text(encoding="utf-8", errors="replace")
    repaired = _repair_catalog_json(raw_text)
    df = pd.read_json(StringIO(repaired))

    df = df[df["status"].fillna("ok").eq("ok")]
    df["name"] = df["name"].astype(str).str.strip()
    df["link"] = df["link"].astype(str).str.strip()
    df["entity_id"] = df["entity_id"].astype(str).str.strip()
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    df["duration"] = df["duration"].fillna("").astype(str).str.strip()
    df["remote"] = df["remote"].fillna("").astype(str).str.strip()
    df["adaptive"] = df["adaptive"].fillna("").astype(str).str.strip()

    df = df[df["name"].ne("") & df["link"].ne("") & df["entity_id"].ne("")]
    df = df.drop_duplicates(subset=["entity_id"], keep="first")
    return df.reset_index(drop=True)


def dataframe_to_assessments(df: pd.DataFrame) -> list[Assessment]:
    assessments: list[Assessment] = []
    for row in df.to_dict(orient="records"):
        assessments.append(
            Assessment(
                entity_id=str(row["entity_id"]),
                name=str(row["name"]),
                url=str(row["link"]),
                description=str(row.get("description") or ""),
                keys=tuple(row.get("keys") or []),
                job_levels=tuple(row.get("job_levels") or []),
                languages=tuple(row.get("languages") or []),
                duration=str(row.get("duration") or ""),
                remote=str(row.get("remote") or ""),
                adaptive=str(row.get("adaptive") or ""),
            )
        )
    return assessments


def load_catalog_dataframe(path: str | Path) -> pd.DataFrame:
    return preprocess_catalog(path)


def load_catalog_from_dataframe(df: pd.DataFrame) -> Catalog:
    return Catalog(dataframe_to_assessments(df))
