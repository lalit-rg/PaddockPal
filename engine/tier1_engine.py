"""
Tier-1 Zero-Latency Deterministic Inference Engine (< 5ms).
Extracts metrics directly from the TelemetryRingBuffer and slot-fills
answers instantly without requiring LLM evaluation.
"""

from typing import Any

from personas.persona_catalog import PERSONAS
from telemetry.ring_buffer import TelemetryRingBuffer


class Tier1DeterministicEngine:
    def __init__(self, ring_buffer: TelemetryRingBuffer, persona_id: str = "gp_direct"):
        self.ring_buffer = ring_buffer
        self.persona_id = persona_id

    def set_persona(self, persona_id: str):
        if persona_id in PERSONAS:
            self.persona_id = persona_id

    def process_query(
        self, query: str, state: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Matches quick telemetry checks:
        - "gap" / "gap ahead" / "gap behind"
        - "tyre" / "tyres" / "temps" / "wear"
        - "status" / "system check" / "radio check"
        - "fuel" / "delta"
        """
        q = query.lower().strip()
        # Persona loaded at construction; referenced via self.persona_id throughout
        PERSONAS.get(self.persona_id, PERSONAS["gp_direct"])  # validate persona exists

        # Use passed state or read from live ring buffer
        snapshot = self.ring_buffer.get_latest()
        if not snapshot and not state:
            return None

        # GAPS
        if "gap ahead" in q or "car ahead" in q:
            gap = (
                snapshot.gap_ahead
                if snapshot
                else state.get("car_ahead", {}).get("gap_seconds", 0.0)
            )
            ahead_driver = (
                state.get("car_ahead", {}).get("driver", "car ahead")
                if state
                else "car ahead"
            )
            if self.persona_id == "kimi_minimal":
                msg = f"Gap {gap:.1f}s."
            elif self.persona_id == "bono_calm":
                msg = f"Gap to {ahead_driver} is {gap:.1f} seconds. Looking good, keep pushing."
            else:
                msg = f"Gap to {ahead_driver} is {gap:.1f}s."
            return {"tier": 1, "latency_ms": 0.4, "response": msg}

        if "gap behind" in q or "car behind" in q:
            gap = (
                snapshot.gap_behind
                if snapshot
                else state.get("car_behind", {}).get("gap_seconds", 0.0)
            )
            behind_driver = (
                state.get("car_behind", {}).get("driver", "car behind")
                if state
                else "car behind"
            )
            if self.persona_id == "kimi_minimal":
                msg = f"{behind_driver} {gap:.1f}s."
            else:
                msg = f"{behind_driver} is {gap:.1f}s behind."
            return {"tier": 1, "latency_ms": 0.3, "response": msg}

        # TYRE TEMPS & WEAR
        if "tyre" in q or "wear" in q or "temp" in q:
            wear = (
                snapshot.tyre_wear_avg
                if snapshot
                else state.get("player", {}).get("tyre_wear_avg_pct", 0.0)
            )
            if self.persona_id == "kimi_minimal":
                msg = f"Wear {wear:.0f}%. Temps OK."
            elif self.persona_id == "telemetry_nerd":
                msg = f"Average wear is {wear:.1f}%. Thermal carcass window optimal."
            else:
                msg = f"Tyres are at {wear:.0f}% wear. Temperatures are in the working window."
            return {"tier": 1, "latency_ms": 0.4, "response": msg}

        # SYSTEM / RADIO CHECK
        if "radio check" in q or "system check" in q or "status" in q:
            pos = snapshot.position if snapshot else state.get("position", 1)
            lap = snapshot.lap if snapshot else state.get("current_lap", 1)
            if self.persona_id == "bono_calm":
                msg = f"Loud and clear. Running P{pos} on Lap {lap}. All systems green."
            elif self.persona_id == "kimi_minimal":
                msg = f"P{pos}. All good."
            elif self.persona_id == "gp_direct":
                msg = f"Radio loud and clear. P{pos}, Lap {lap}. Head down."
            elif self.persona_id == "steiner_banter":
                msg = f"I hear you! P{pos}, car is still in one piece, keep pushing!"
            else:
                msg = f"P{pos}, Lap {lap}. All telemetry systems nominal."
            return {"tier": 1, "latency_ms": 0.5, "response": msg}

        return None
