"""
Main Interactive Demo: Simulates real-time Driver-to-Engineer interaction
across all tiers, racecraft rules, and post-session debriefs.
"""

from engine.assistant import RaceEngineerAssistant
from mock_data.scenarios import MOCK_SCENARIOS


def run_main():
    print("=" * 80)
    print(" F1 VIRTUAL RACE ENGINEER: LOW-LATENCY INFERENCE & RACECRAFT SYSTEM")
    print("=" * 80)

    # Initialize assistant with GP (The Commander)
    engineer = RaceEngineerAssistant(persona_id="gp_direct")

    print("\n--- 1. Testing Tier-1 Zero-Latency Ingestion (< 1ms) ---")
    scen = MOCK_SCENARIOS["system_check_status"]["telemetry_state"]
    resp1 = engineer.ask("Radio check and status update", scen)
    print('Driver  : "Radio check and status update"')
    print(
        f'Engineer: "{resp1["response"]}" (Latency: {resp1["latency_ms"]:.2f}ms | Tier: {resp1["tier"]})'
    )

    resp2 = engineer.ask("What is the gap ahead?", scen)
    print('\nDriver  : "What is the gap ahead?"')
    print(
        f'Engineer: "{resp2["response"]}" (Latency: {resp2["latency_ms"]:.2f}ms | Tier: {resp2["tier"]})'
    )

    print("\n--- 2. Testing Persona Switching (Switching to Bono) ---")
    engineer.set_persona("bono_calm")
    resp_bono = engineer.ask("Tyre temps and wear check", scen)
    print('Driver  : "Tyre temps and wear check"')
    print(f'Bono    : "{resp_bono["response"]}"')

    print("\n--- 3. Testing 1Hz Prescriptive Rolling Directive ---")
    hunting_state = MOCK_SCENARIOS["hunting_for_p2"]["telemetry_state"]
    directive = engineer.evaluate_1hz_stream(hunting_state)
    print(f"Rolling Alert: [{directive['priority']}] Action: {directive['action']}")
    print(
        f'Directive    : "{directive["directive"]}" (Setting: {directive["actionable_setting"]})'
    )

    print("\n--- 4. Testing Post-Session Cooldown & FastF1 Summary ---")
    post = engineer.post_session_debrief(finish_position=1)
    print(f'Radio Call: "{post["radio_call"]}"')
    print("Debrief Summary:")
    for k, v in post["summary"].items():
        print(f"  • {k.replace('_', ' ').title():<28}: {v}")


if __name__ == "__main__":
    run_main()
