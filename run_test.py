"""
Interactive CLI to test any persona against any telemetry scenario.
Usage:
  python run_test.py
"""

import sys
from personas.persona_catalog import PERSONAS
from mock_data.scenarios import MOCK_SCENARIOS
from mock_data.bench import format_telemetry_prompt, call_llm

def main():
    print("=" * 70)
    print(" F1 RACE ENGINEER: MULTI-PERSONA INFERENCE TEST BENCH")
    print("=" * 70)
    
    print("\n--- Available Scenarios ---")
    scen_keys = list(MOCK_SCENARIOS.keys())
    for idx, key in enumerate(scen_keys, 1):
        scen = MOCK_SCENARIOS[key]
        print(f"[{idx}] {scen['title']} (Driver: \"{scen['driver_query']}\")")
        
    print("\n--- Available Personas (10 Distinct Archetypes) ---")
    p_keys = list(PERSONAS.keys())
    for idx, p_key in enumerate(p_keys, 1):
        p = PERSONAS[p_key]
        print(f"[{idx}] {p['name']} ({p['archetype']})")
        
    print("\n" + "-" * 70)
    print("Testing Scenario 1: Hunting P2 (VER ahead by 0.85s on 22-lap old Hards)")
    print("-" * 70)
    
    prompt = format_telemetry_prompt("hunting_for_p2")
    
    for p_key in p_keys:
        p = PERSONAS[p_key]
        result = call_llm(p_key, prompt)
        print(f"\n>> [{p['archetype'].upper()}] - {p['name']}")
        print(f"   Radio Call : \"{result['text']}\"")
        print(f"   Latency    : {result['latency_ms']:.1f}ms (Source: {result['source']})")

    print("\n" + "=" * 70)
    print("Testing Scenario 3: Safety Car Deployed (Box vs Stay Out)")
    print("=" * 70)
    prompt_sc = format_telemetry_prompt("safety_car_dilemma")
    for p_key in ["gp_direct", "bono_calm", "chess_master", "ferrari_drama", "iceman_minimal"]:
        p = PERSONAS[p_key]
        result = call_llm(p_key, prompt_sc)
        print(f"\n>> [{p['archetype'].upper()}] - {p['name']}")
        print(f"   Radio Call : \"{result['text']}\"")

if __name__ == "__main__":
    main()
