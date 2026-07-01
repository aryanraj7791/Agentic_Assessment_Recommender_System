"""Conversation state reconstructed from message history."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.models import ChatMessage


@dataclass
class ConversationState:
    messages: list[ChatMessage]
    turn_count: int
    latest_user_message: str
    full_text: str
    prior_shortlist_names: list[str] = field(default_factory=list)
    user_confirmed: bool = False
    has_prior_shortlist: bool = False


CONFIRM_PHRASES = (
    "thanks",
    "confirmed",
    "perfect",
    "that works",
    "locking it in",
    "keep the shortlist",
    "as-is",
    "as above",
    "good to go",
    "that covers it",
)


def reconstruct_state(messages: list[ChatMessage]) -> ConversationState:
    latest_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    full_text = "\n".join(f"{m.role}: {m.content}" for m in messages)
    prior_names = _extract_shortlist_from_history(messages)
    lower = latest_user.lower()

    return ConversationState(
        messages=messages,
        turn_count=len(messages),
        latest_user_message=latest_user,
        full_text=full_text,
        prior_shortlist_names=prior_names,
        user_confirmed=any(phrase in lower for phrase in CONFIRM_PHRASES),
        has_prior_shortlist=bool(prior_names),
    )


def _extract_shortlist_from_history(messages: list[ChatMessage]) -> list[str]:
    """Parse assessment names mentioned in the most recent assistant message."""
    if len(messages) < 2:
        return []

    last_assistant = next((m.content for m in reversed(messages[:-1]) if m.role == "assistant"), "")
    if not last_assistant:
        return []

    names: list[str] = []
    for line in last_assistant.splitlines():
        match = re.match(r"^\d+\.\s+(.+?)(?:\s+\(|$)", line.strip())
        if match:
            names.append(match.group(1).strip())
    return names
