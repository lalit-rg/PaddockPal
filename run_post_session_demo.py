"""
Post-Session Test: Verifies post-race radio messages, congratulatory / debrief protocols,
and FastF1-style telemetry summary extraction across personas.
"""

from post_session_engine import PostSessionDebriefEngine
from personas.persona_catalog import PERSONAS

def run_post_session_demo():
    print("=" * 80)
    print(" F1 RACE ENGINEER: POST-SESSION RADIO & TELEMETRY DEBRIEF")
    print("=" * 80)

    # 1. P1 WIN CELEBRATION
    print("\n--- [CASE 1: CHECKERED FLAG P1 WIN] ---")
    for pid in ["bono_calm", "gp_direct", "vettel_analyst", "steiner_banter", "alonso_tactician", "kimi_minimal"]:
        p = PERSONAS[pid]
        call = PostSessionDebriefEngine.generate_radio_call(pid, finish_position=1)
        print(f">> {p['name']}:")
        print(f"   \"{call}\"\n")

    # 2. TOUGH RACE P9 RECOVERY
    print("--- [CASE 2: DIFFICULT RACE P9 FINISH] ---")
    for pid in ["bono_calm", "gp_direct", "steiner_banter", "prost_minimal"]:
        p = PERSONAS[pid]
        call = PostSessionDebriefEngine.generate_radio_call(pid, finish_position=9)
        print(f">> {p['name']}:")
        print(f"   \"{call}\"\n")

    # 3. TELEMETRY DEBRIEF METRICS SUMMARY
    print("=" * 80)
    print("--- FASTF1-STYLE TELEMETRY DEBRIEF SUMMARY ---")
    print("=" * 80)
    debrief = PostSessionDebriefEngine.generate_telemetry_debrief_summary({
        "position": 1,
        "fastest_lap": "1:31.840",
    })
    for k, v in debrief.items():
        print(f"  • {k.replace('_', ' ').title():<30}: {v}")

if __name__ == "__main__":
    run_post_session_demo()
