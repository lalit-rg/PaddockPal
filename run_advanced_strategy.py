"""
Advanced Scenarios testing:
1. Regulatory & Steward orders (Give position back, Track limits black-and-white flag)
2. Traffic Rejoin & Clean Air Window (Avoid falling behind slow traffic)
3. Track Condition & Weather Evolution (Slick to Intermediate crossover)
"""

from personas.persona_catalog import PERSONAS
from racecraft_engine import RacecraftStrategyEngine

COMPLEX_RACE_SCENARIOS = {
    # Scenario A: Off-track overtake (Must give position back)
    "offtrack_pass": {
        "title": "Scenario A: Illegal Overtake (Off-track advantage at Turn 2)",
        "track": "Bahrain",
        "illegal_overtake_detected": True,
        "track_limits_warnings": 2,
        "player": {"gap_to_leader": 0.0, "tyre_compound": "MEDIUM", "tyre_wear_avg_pct": 30.0}
    },

    # Scenario B: Track limits strike 3 (Black and White Flag)
    "track_limits_strike": {
        "title": "Scenario B: Track Limits Warning (Strike 3 / Black & White Flag)",
        "track": "Silverstone",
        "illegal_overtake_detected": False,
        "track_limits_warnings": 3,
        "player": {"gap_to_leader": 4.5, "tyre_compound": "HARD", "tyre_wear_avg_pct": 45.0}
    },

    # Scenario C: Traffic Gap Evaluation (Pitting lands behind a Haas)
    "traffic_pit_dilemma": {
        "title": "Scenario C: Traffic Rejoin Analysis (Undercut vs Traffic Block)",
        "track": "Monza",
        "player": {"gap_to_leader": 15.0, "tyre_compound": "SOFT", "tyre_wear_avg_pct": 62.0},
        "grid_relative_gaps": [
            {"driver": "VER", "gap_to_leader": 0.0},
            {"driver": "NOR", "gap_to_leader": 6.5},
            {"driver": "LEC", "gap_to_leader": 12.0},
            {"driver": "HUL", "gap_to_leader": 39.8} # Rejoin at 15.0 + 24.0 = 39.0s -> DROPS RIGHT BEHIND HUL!
        ]
    },

    # Scenario D: Weather Crossover (Rain starting, track wetness rising)
    "weather_crossover": {
        "title": "Scenario D: Track Evolution (Rain intensity rising to 45%, wetness 24%)",
        "track": "Spa",
        "weather": {
            "track_temp_c": 22,
            "rain_intensity_pct": 45,
            "track_wetness_pct": 24
        },
        "player": {"gap_to_leader": 8.0, "tyre_compound": "SLICK_SOFT", "tyre_wear_avg_pct": 40.0}
    }
}

def run_complex_strategy_eval():
    print("=" * 85)
    print(" F1 RACECRAFT & STRATEGY ENGINE: ADVANCED ON-PREM EVALUATION")
    print("=" * 85)

    for key, state in COMPLEX_RACE_SCENARIOS.items():
        print(f"\n>>> TESTING: {state['title']}")
        verdict = RacecraftStrategyEngine.compute_strategic_verdict(state)
        
        print(f"    [Engine Verdict] Priority: {verdict['priority']} | Code: {verdict.get('code')}")
        print(f"    [Directive]      {verdict['directive']}")
        
        # Check how distinct personalities deliver this call
        print("    [Iconic Personas Adaptation]:")
        if verdict.get("code") == "GIVE_POSITION_BACK":
            print(f"      • GP (The Commander)       : \"Max, give the position back before Turn 4. Don't argue, let him by.\"")
            print(f"      • Alonso (The Shark)       : \"Give the position back, then pass him again on the straight with DRS!\"")
            print(f"      • Guenther Steiner         : \"Give the position back, don't be an idiot and take a penalty!\"")
            print(f"      • Kimi (Ice Man)           : \"Give position back.\"")
        elif verdict.get("code") == "BLACK_AND_WHITE_FLAG":
            print(f"      • Sebastian Vettel (Analyst): \"Black and white flag, watch the track limits at Copse! Stay on the curb!\"")
            print(f"      • Bono (The Anchor)        : \"Track limits warning, keep it between the white lines, target plus 2.\"")
            print(f"      • Kimi (Ice Man)           : \"B&W flag track limits.\"")
        elif verdict.get("code") == "EXTEND_AVOID_TRAFFIC":
            print(f"      • Alain Prost (Professor)  : \"Extend 2 laps. Pitting now lands us behind Hulkenberg. Clean air needed.\"")
            print(f"      • Ferrari Drama (Xavier)   : \"We stay out, we stay out. Traffic behind Hulkenberg, question?\"")
        elif verdict.get("code") == "BOX_WEATHER_CROSSOVER":
            print(f"      • Bono (The Anchor)        : \"Box box, in in in in in! Intermediates ready, crossover reached!\"")
            print(f"      • Sebastian Vettel (Analyst): \"Track wetness 24%! Box now for Inters, do not stay out!\"")

if __name__ == "__main__":
    run_complex_strategy_eval()
