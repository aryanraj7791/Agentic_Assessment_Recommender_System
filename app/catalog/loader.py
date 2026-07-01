"""Catalog loading and test-type mapping."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

KEY_TO_TEST_TYPE: dict[str, str] = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Ability & Aptitude": "A",
    "Simulations": "S",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Assessment Exercises": "E",
}

TEST_TYPE_ORDER = ["K", "A", "P", "B", "S", "C", "D", "E"]


@dataclass(frozen=True)
class Assessment:
    entity_id: str
    name: str
    url: str
    description: str
    keys: tuple[str, ...]
    job_levels: tuple[str, ...]
    languages: tuple[str, ...]
    duration: str
    remote: str
    adaptive: str

    @property
    def test_type(self) -> str:
        letters = []
        for letter in TEST_TYPE_ORDER:
            for key in self.keys:
                if KEY_TO_TEST_TYPE.get(key) == letter:
                    letters.append(letter)
                    break
        if not letters and self.keys:
            letters = [KEY_TO_TEST_TYPE.get(self.keys[0], "K")]
        return ",".join(letters) if len(letters) > 1 else (letters[0] if letters else "K")

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "url": self.url,
            "test_type": self.test_type,
            "description": self.description,
            "keys": list(self.keys),
            "job_levels": list(self.job_levels),
            "languages": list(self.languages),
            "duration": self.duration,
            "remote": self.remote,
            "adaptive": self.adaptive,
        }

    def search_text(self) -> str:
        parts = [
            self.name,
            self.description,
            " ".join(self.keys),
            " ".join(self.job_levels),
            " ".join(self.languages),
        ]
        return " ".join(p for p in parts if p).lower()


def _repair_catalog_json(raw: str) -> str:
    """Fix known formatting issues in the provided catalog export."""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", raw)
    cleaned = re.sub(
        r'"name"\s*:\s*"([^"]*?)\s*\n\s*([^"]*?)"',
        lambda m: f'"name": "{m.group(1).strip()} {m.group(2).strip()}"',
        cleaned,
    )
    return cleaned


def _parse_item(raw: dict[str, Any]) -> Assessment | None:
    name = (raw.get("name") or "").strip()
    link = (raw.get("link") or "").strip()
    entity_id = str(raw.get("entity_id") or "").strip()
    if not name or not link or not entity_id:
        return None
    if raw.get("status") not in (None, "ok"):
        return None
    return Assessment(
        entity_id=entity_id,
        name=name,
        url=link,
        description=(raw.get("description") or "").strip(),
        keys=tuple(raw.get("keys") or []),
        job_levels=tuple(raw.get("job_levels") or []),
        languages=tuple(raw.get("languages") or []),
        duration=(raw.get("duration") or "").strip(),
        remote=(raw.get("remote") or "").strip(),
        adaptive=(raw.get("adaptive") or "").strip(),
    )


class Catalog:
    def __init__(self, assessments: list[Assessment]):
        self.assessments = assessments
        self._by_id = {a.entity_id: a for a in assessments}
        self._by_url = {a.url.rstrip("/"): a for a in assessments}
        self._by_name_lower = {a.name.lower(): a for a in assessments}
        self._by_name_norm = {self._normalize_name(a.name): a for a in assessments}

    @staticmethod
    def _normalize_name(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()

    @classmethod
    def load(cls, path: str | Path) -> "Catalog":
        raw_text = Path(path).read_text(encoding="utf-8", errors="replace")
        repaired = _repair_catalog_json(raw_text)
        data = json.loads(repaired)
        assessments: list[Assessment] = []
        for item in data:
            parsed = _parse_item(item)
            if parsed:
                assessments.append(parsed)
        return cls(assessments)

    def get_by_id(self, entity_id: str) -> Assessment | None:
        return self._by_id.get(entity_id)

    def get_by_url(self, url: str) -> Assessment | None:
        return self._by_url.get(url.rstrip("/"))

    def get_by_name(self, name: str) -> Assessment | None:
        if name in self._by_id:
            return self.get_by_id(name)
        direct = self._by_name_lower.get(name.lower())
        if direct:
            return direct
        norm = self._normalize_name(name)
        if norm in self._by_name_norm:
            return self._by_name_norm[norm]
        for assessment in self.assessments:
            assessment_norm = self._normalize_name(assessment.name)
            if norm == assessment_norm or norm in assessment_norm or assessment_norm in norm:
                return assessment
        return None

    def resolve_references(self, refs: list[str]) -> list[Assessment]:
        resolved: list[Assessment] = []
        seen: set[str] = set()
        for ref in refs:
            ref = ref.strip()
            if not ref:
                continue
            match = (
                self.get_by_id(ref)
                or self.get_by_url(ref)
                or self.get_by_name(ref)
            )
            if match and match.entity_id not in seen:
                resolved.append(match)
                seen.add(match.entity_id)
        return resolved

    def __len__(self) -> int:
        return len(self.assessments)
