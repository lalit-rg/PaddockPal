"""
Demonstrates the separation between:
1. DESCRIPTIVE QUERY ("What is my status?") -> Fast Fact Delivery
2. PRESCRIPTIVE QUERY ("What should I do?") -> Evaluated via the Multi-Factor Formula
Tested across the 10 real-world F1 persona profiles (Vettel, Alonso, Prost, Bono, GP, Kimi, etc.)
"""

from mock_data.scenarios import MOCK_SCENARIOS
from telemetry_analytics import TelemetryAnalyticsEngine


def run_analytics_demo():
    print("=" * 80)
    print(" F1 RACE ENGINEER: DESCRIPTIVE VS. PRESCRIPTIVE ANALYTICS ENGINE")
    print("=" * 80)

    for scenario_id in ["hunting_for_p2", "defending_worn_tyres", "safety_car_dilemma"]:
        scen = MOCK_SCENARIOS[scenario_id]
        state = scen["telemetry_state"]

        print(f"\n==================== SCENARIO: {scen['title']} ====================")

        # 1. Compute Descriptive Analysis (Sub-millisecond)
        desc = TelemetryAnalyticsEngine.get_descriptive_metrics(state)
        print("\n[1] DESCRIPTIVE FACTS (What is happening right now?):")
        print(f"    • Track Pos       : P{desc['pos']} (Lap {desc['lap']})")
        print(
            f"    • Gaps            : Ahead: {desc['gap_ahead']}s | Behind: {desc['gap_behind']}s"
        )
        print(
            f"    • Tyre Status     : {desc['tyre_compound']} ({desc['tyre_age']} laps, Wear: {desc['tyre_wear_avg']}%)"
        )
        print(f"    • Surface Temps   : {desc['temps']}")
        print(
            f"    • Energy & Fuel   : Battery: {desc['battery_pct']}% | Fuel Delta: {desc['fuel_delta']:+.1f} laps"
        )

        # 2. Compute Prescriptive Analysis (Multi-factor Formula)
        presc = TelemetryAnalyticsEngine.evaluate_prescriptive_formula(state)
        print("\n[2] PRESCRIPTIVE DIRECTIVE (Multi-Factor Formula Output):")
        print(f"    • Priority Level  : {presc['priority']}")
        print(f"    • Primary Action  : {presc['action']}")
        print(f"    • Directive       : {presc['directive']}")
        print(f"    • Car Setting Adj : {presc['actionable_setting']}")

        # 3. Render through 3 distinct personalities
        print(
            "\n[3] PERSONA ADAPTATIONS (How different real F1 legends speak the directive):"
        )

        if presc["action"] == "EXECUTE_OVERTAKE":
            print(
                '    >> [Fernando Alonso (The Shark)]           : "Attack him! He has zero rears, dump the battery into Turn 1!"'
            )
            print(
                '    >> [Alain Prost (The Minimalist Professor)]: "Pace is sufficient. Do not risk flat-spotting; pass cleanly on straight."'
            )
            print(
                '    >> [Kimi Räikkönen (Ice Man)]             : "P3. Gap 0.8. Mode push."'
            )
        elif presc["action"] == "MANAGE_TRACTION_LIFT_COAST":
            print(
                '    >> [Sebastian Vettel (Analyst Professor)] : "Rears at 126C! Carcass is overheating, brake bias forward 2%, manage the exit."'
            )
            print(
                '    >> [Guenther Steiner (Unfiltered Banter)]  : "Wake up mate, you\'re cooking eggs on the rear tyres! Cool them down!"'
            )
            print(
                '    >> [Gianpiero Lambiase (GP)]              : "Rears are screaming. Protect the traction out of the chicane, head down."'
            )
        elif presc["action"] == "BOX_NOW":
            print(
                '    >> [Sebastian Vettel (Analyst Professor)] : "Safety car! Box now, cheap 12s delta, soft tyre set 2 ready!"'
            )
            print(
                '    >> [Ferrari Drama (Xavier Marcos style)]  : "Safety car deployed! Box for softs or stay out, question?"'
            )
            print(
                '    >> [Kimi Räikkönen (Ice Man)]             : "Box box now. Softs."'
            )


if __name__ == "__main__":
    run_analytics_demo()
