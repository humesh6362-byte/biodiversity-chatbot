"""Very small in-memory conversation store, keyed by session_id.

For a production deployment this would be Redis or a DB table, but an
in-memory dict is enough to demonstrate multi-turn memory + slot-filling for
a hackathon submission. State is lost on process restart — noted in the
README as a known limitation.
"""
from typing import Dict, List, Any

_sessions: Dict[str, Dict[str, Any]] = {}


def get_session(session_id: str) -> Dict[str, Any]:
    if session_id not in _sessions:
        _sessions[session_id] = {"history": [], "slots": {}}
    return _sessions[session_id]


def add_turn(session_id: str, role: str, content: str) -> None:
    session = get_session(session_id)
    session["history"].append({"role": role, "content": content})
    # keep the last 12 turns to bound prompt size
    session["history"] = session["history"][-12:]


def update_slots(session_id: str, new_slots: dict) -> dict:
    session = get_session(session_id)
    for key, value in new_slots.items():
        if value is not None:
            session["slots"][key] = value
    return session["slots"]
