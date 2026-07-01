"""Evaluate recall against sample conversation expected shortlists."""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAMPLE_DIR = ROOT / "data" / "sample_conversations" / "GenAI_SampleConversations"


def parse_sample(path: Path) -> tuple[list[list[str]], list[str]]:
    text = path.read_text(encoding="utf-8")
    turns = re.split(r"### Turn \d+", text)[1:]
    user_messages: list[str] = []
    expected_names: list[str] = []

    for turn in turns:
        user_match = re.search(r"\*\*User\*\*\s*\n\s*\n>\s*(.*?)(?=\n\n\*\*Agent\*\*)", turn, re.DOTALL)
        if user_match:
            user_messages.append(re.sub(r"\s+", " ", user_match.group(1).strip()))

        table_rows = re.findall(r"\|\s*\d+\s*\|\s*([^|]+)\|", turn)
        if table_rows:
            expected_names = [row.strip() for row in table_rows]

    return user_messages, expected_names


def recall_at_k(recommended: list[str], expected: list[str], k: int = 10) -> float:
    if not expected:
        return 1.0
    top = recommended[:k]
    hits = sum(1 for name in expected if any(name.lower() in r.lower() or r.lower() in name.lower() for r in top))
    return hits / len(expected)


async def run_conversation(base_url: str, user_messages: list[str]) -> list[str]:
    messages: list[dict[str, str]] = []
    final_names: list[str] = []

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        for user_msg in user_messages:
            messages.append({"role": "user", "content": user_msg})
            response = await client.post("/chat", json={"messages": messages})
            response.raise_for_status()
            payload = response.json()
            assistant_reply = payload["reply"]
            messages.append({"role": "assistant", "content": assistant_reply})
            if payload.get("recommendations"):
                final_names = [r["name"] for r in payload["recommendations"]]
            if payload.get("end_of_conversation"):
                break

    return final_names


async def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate sample conversations")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="API base URL")
    args = parser.parse_args()

    if not SAMPLE_DIR.exists():
        print(f"Sample conversations not found at {SAMPLE_DIR}")
        sys.exit(1)

    scores: list[float] = []
    for sample in sorted(SAMPLE_DIR.glob("C*.md")):
        user_messages, expected = parse_sample(sample)
        if not user_messages:
            continue
        recommended = await run_conversation(args.url, user_messages)
        score = recall_at_k(recommended, expected)
        scores.append(score)
        print(f"{sample.name}: recall@10={score:.2f} (expected {len(expected)}, got {len(recommended)})")

    if scores:
        print(f"\nMean recall@10: {sum(scores)/len(scores):.3f}")


if __name__ == "__main__":
    asyncio.run(main())
