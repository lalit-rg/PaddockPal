"""
Unit Tests and Latency Benchmarks for PaddockPal.
Verifies:
1. Tier-1 Deterministic Execution is strictly sub-millisecond (< 1.0ms).
2. Racecraft Strategy Engine triggers regulatory and tactical flags correctly.
3. Multi-sim NormalizedTelemetryFrame contract adherence.
4. FastF1 post-session debrief summary structures.
"""

import time

import pytest

from engine.tier1_engine import Tier1DeterministicEngine
from personas.persona_catalog import PERSONAS
from post_session_engine import PostSessionDebriefEngine
from racecraft_engine import RacecraftStrategyEngine
from telemetry.ring_buffer import TelemetryRingBuffer, TelemetrySnapshot


@pytest.fixture
def ring_buffer():
    rb = TelemetryRingBuffer(capacity=100)
    snap = TelemetrySnapshot(
        timestamp=time.time(),
        lap=15,
        position=3,
        gap_ahead=0.85,
        gap_behind=3.40,
        tyre_compound="MEDIUM",
        tyre_age=8,
        tyre_wear_avg=22.5,
        surface_temps={"FL": 102.0, "FR": 103.0, "RL": 104.0, "RR": 105.0},
        carcass_temps={"FL": 98.0, "FR": 99.0, "RL": 100.0, "RR": 101.0},
        fuel_delta=+0.8,
        ers_battery_pct=74.0,
        drs_active=True,
        speed_kph=315.0,
        gear=7,
        throttle=100.0,
        brake=0.0,
    )
    rb.push(snap)
    return rb


def test_tier1_latency_benchmark(ring_buffer):
    """
    Tier-1 lookups MUST complete in strictly under 1.0ms.
    """
    engine = Tier1DeterministicEngine(ring_buffer, persona_id="gp_direct")

    queries = [
        "What is the gap ahead?",
        "Check tyre temps and wear",
        "Radio check and status update",
    ]

    for q in queries:
        t0 = time.perf_counter()
        res = engine.process_query(q)
        dt_ms = (time.perf_counter() - t0) * 1000

        assert res is not None
        assert dt_ms < 1.0, f"Query '{q}' took {dt_ms:.3f}ms, exceeding 1.0ms SLA!"
        assert res["tier"] == 1


def test_steward_illegal_overtake():
    """
    Steward rules must order driver to yield position when an illegal off-track pass occurs.
    """
    state = {
        "illegal_overtake_detected": True,
        "track_limits_warnings": 1,
        "track": "Bahrain",
    }
    verdict = RacecraftStrategyEngine.compute_strategic_verdict(state)
    assert verdict["priority"] == "CRITICAL_STEWARD"
    assert verdict["code"] == "GIVE_POSITION_BACK"
    assert "Give the position back" in verdict["directive"]


def test_steward_track_limits_strike3():
    """
    3 track limit warnings must trigger Black and White flag warning.
    """
    state = {
        "illegal_overtake_detected": False,
        "track_limits_warnings": 3,
        "track": "Silverstone",
    }
    verdict = RacecraftStrategyEngine.compute_strategic_verdict(state)
    assert verdict["priority"] == "HIGH_STEWARD"
    assert verdict["code"] == "BLACK_AND_WHITE_FLAG"


def test_traffic_rejoin_extend_stint():
    """
    If an undercut rejoins within <2.0s behind a car, strategy must call to EXTEND stint.
    """
    state = {
        "track": "Monza",
        "player": {
            "gap_to_leader": 15.0,
            "tyre_compound": "SOFT",
            "tyre_wear_avg_pct": 62.0,
        },
        "grid_relative_gaps": [
            {"driver": "VER", "gap_to_leader": 0.0},
            {
                "driver": "HUL",
                "gap_to_leader": 39.8,
            },  # Rejoin at 15.0 + 24.0 = 39.0s -> Behind HUL
        ],
    }
    verdict = RacecraftStrategyEngine.compute_strategic_verdict(state)
    assert verdict["code"] == "EXTEND_AVOID_TRAFFIC"


def test_weather_intermediate_crossover():
    """
    Track wetness > 20% must trigger immediate Intermediate pit call.
    """
    state = {
        "track": "Spa",
        "weather": {
            "track_temp_c": 20,
            "rain_intensity_pct": 50,
            "track_wetness_pct": 25,
        },
        "player": {
            "gap_to_leader": 5.0,
            "tyre_compound": "DRY_SLICK",
            "tyre_wear_avg_pct": 30,
        },
    }
    verdict = RacecraftStrategyEngine.compute_strategic_verdict(state)
    assert verdict["priority"] == "CRITICAL_WEATHER"
    assert verdict["code"] == "BOX_WEATHER_CROSSOVER"


def test_all_10_personas_present():
    """
    Ensures all 10 persona archetypes are registered with taglines and sample acks.
    """
    expected_ids = [
        "gp_direct",
        "bono_calm",
        "alonso_tactician",
        "vettel_analyst",
        "prost_minimal",
        "steiner_banter",
        "telemetry_nerd",
        "ferrari_drama",
        "hype_spotter",
        "kimi_minimal",
    ]
    for pid in expected_ids:
        assert pid in PERSONAS, f"Persona '{pid}' missing from persona catalog!"
        p = PERSONAS[pid]
        assert len(p["system_prompt"]) > 10
        assert len(p["sample_acknowledgments"]) > 0


def test_post_session_summary():
    """
    Verifies post-session debrief format.
    """
    call = PostSessionDebriefEngine.generate_radio_call("bono_calm", finish_position=1)
    assert "Get in there Lewis" in call

    summary = PostSessionDebriefEngine.generate_telemetry_debrief_summary(
        {"position": 1}
    )
    assert "tyre_deg_efficiency" in summary
    assert "braking_marker_consistency" in summary
