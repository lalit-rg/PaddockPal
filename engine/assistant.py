"""
Unified Race Engineer Runner:
Orchestrates:
1. Telemetry ingestion & ring buffer
2. Intent classification (Tier 1 Instant vs Tier 3 Deep Strategy)
3. Racecraft evaluation (Flags, Traffic slots, Weather crossover, Multi-factor Prescriptive Directives)
4. Post-session telemetry debrief and celebrations
"""

import time
from typing import Any

from engine.tier1_engine import Tier1DeterministicEngine
from mock_data.bench import call_llm
from personas.persona_catalog import PERSONAS
from post_session_engine import PostSessionDebriefEngine
from racecraft_engine import RacecraftStrategyEngine
from telemetry.ring_buffer import TelemetryRingBuffer
from telemetry_analytics import TelemetryAnalyticsEngine


class RaceEngineerAssistant:
    def __init__(self, persona_id: str = "gp_direct"):
        self.ring_buffer = TelemetryRingBuffer()
        self.persona_id = persona_id
        self.tier1_engine = Tier1DeterministicEngine(self.ring_buffer, persona_id)

    def set_persona(self, persona_id: str):
        if persona_id in PERSONAS:
            self.persona_id = persona_id
            self.tier1_engine.set_persona(persona_id)

    def ask(self, query: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Processes driver radio voice input:
        - First checks Tier-1 Deterministic Engine (<1ms)
        - If not a direct metric, checks Racecraft Engine rules (flags, stewards, traffic)
        - Otherwise delegates to Tier-3 LLM reasoning with speculative masking
        """
        start = time.perf_counter()

        # 1. Tier-1 Instant Metric
        t1_resp = self.tier1_engine.process_query(query, state)
        if t1_resp:
            return t1_resp

        # 2. Racecraft Critical Directives
        if state:
            racecraft_verdict = RacecraftStrategyEngine.compute_strategic_verdict(state)
            if racecraft_verdict and racecraft_verdict.get("priority") in [
                "CRITICAL_STEWARD",
                "CRITICAL_WEATHER",
            ]:
                return {
                    "tier": "Racecraft-Rule",
                    "latency_ms": (time.perf_counter() - start) * 1000,
                    "response": racecraft_verdict["directive"],
                }

        # 3. Tier-3 LLM Deep Strategy
        # Instant acknowledgment masking (so driver hears 'Copy, standby' in <30ms)
        p = PERSONAS.get(self.persona_id, PERSONAS["gp_direct"])
        ack = p["sample_acknowledgments"][0]

        # In a real environment, format compressed state and call model
        sim_resp = call_llm(self.persona_id, f'--- DRIVER RADIO ---\n"{query}"\n')
        return {
            "tier": 3,
            "latency_ms": sim_resp["latency_ms"],
            "masking_ack": ack,
            "response": sim_resp["text"],
        }

    def evaluate_1hz_stream(self, state: dict[str, Any]) -> dict[str, Any] | None:
        """
        Background rolling prescriptive sweep evaluated once every second.
        Returns directives only if an actionable threshold is breached (Priority Queue).
        """
        prescriptive = TelemetryAnalyticsEngine.evaluate_prescriptive_formula(state)
        if prescriptive["priority"] in ["CRITICAL", "HIGH"]:
            return prescriptive
        return None

    def post_session_debrief(
        self, finish_position: int, session_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Post-race radio call & FastF1-style telemetry summary.
        """
        radio = PostSessionDebriefEngine.generate_radio_call(
            self.persona_id, finish_position
        )
        summary = PostSessionDebriefEngine.generate_telemetry_debrief_summary(
            session_data or {"position": finish_position}
        )
        return {"radio_call": radio, "summary": summary}
