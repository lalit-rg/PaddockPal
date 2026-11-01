"""
Test Bench: Runs telemetry scenarios through Personas using standard inference protocols.
Supports:
- Direct mock/simulation mode (instant zero-dependency testing of prompt effectiveness)
- OpenAI-compatible endpoint (vLLM / Ollama / llama.cpp / Groq / OpenAI)
- Gemini REST API (via raw urllib, zero third-party dependency)
"""

import json
import os
import time
from typing import Any

from mock_data.scenarios import MOCK_SCENARIOS
from personas.persona_catalog import PERSONAS


def format_telemetry_prompt(scenario_key: str) -> str:
    scenario = MOCK_SCENARIOS[scenario_key]
    telem = scenario["telemetry_state"]
    query = scenario["driver_query"]

    # Senior Inference Engineer: Highly compressed telemetry snapshot representation (token efficiency)
    prompt = (
        f"--- LIVE TELEMETRY SNAPSHOT ---\n"
        f"Track: {telem.get('track', 'Unknown')} | Lap: {telem.get('current_lap')}/{telem.get('total_laps')} | Pos: P{telem.get('position')}\n"
    )

    if telem.get("safety_car_status"):
        prompt += f"Status: {telem.get('safety_car_status')}\n"

    car_ahead = telem.get("car_ahead")
    if car_ahead:
        prompt += f"Ahead: {car_ahead.get('driver')} (Gap: {car_ahead.get('gap_seconds')}s, Tyre: {car_ahead.get('tyre_compound')}-{car_ahead.get('tyre_age_laps', '?')} laps)\n"
    else:
        prompt += "Ahead: Leader (Clear air)\n"

    car_behind = telem.get("car_behind")
    if car_behind:
        prompt += f"Behind: {car_behind.get('driver')} (Gap: {car_behind.get('gap_seconds')}s, Tyre: {car_behind.get('tyre_compound')}-{car_behind.get('tyre_age_laps', '?')} laps)\n"

    player = telem.get("player", {})
    prompt += (
        f"Car: Tyre {player.get('tyre_compound')} ({player.get('tyre_age_laps', 0)} laps, Wear: {player.get('tyre_wear_avg_pct', 0)}%) | "
        f"Fuel: {player.get('fuel_delta_laps', 0):+.1f} laps | Battery: {player.get('ers_battery_pct', 0)}%\n"
    )

    if "tyre_surface_temps" in player:
        temps = player["tyre_surface_temps"]
        prompt += f"Temps(FL/FR/RL/RR): {temps['FL']}C/{temps['FR']}C/{temps['RL']}C/{temps['RR']}C\n"

    if "distance_to_pit_entry_m" in player:
        prompt += f"Pit Entry: {player['distance_to_pit_entry_m']}m ahead | SC Pit Delta: {player.get('pit_delta_under_sc_seconds')}s\n"

    prompt += f'--- DRIVER RADIO ---\n"{query}"\n'
    prompt += "Respond as the race engineer:"
    return prompt


def call_llm(persona_id: str, prompt: str) -> dict[str, Any]:
    persona = PERSONAS[persona_id]
    sys_prompt = persona["system_prompt"]
    # API key presence is checked per-provider below; no unified key needed

    start_time = time.perf_counter()

    # If API key is available, call the remote LLM
    if os.getenv("GEMINI_API_KEY"):
        import urllib.request

        key = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"System Persona: {sys_prompt}\n\nTask:\n{prompt}"}
                    ],
                }
            ],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 60},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode("utf-8"))
                text = res["candidates"][0]["content"]["parts"][0]["text"].strip()
                latency_ms = (time.perf_counter() - start_time) * 1000
                return {
                    "text": text,
                    "latency_ms": latency_ms,
                    "source": "gemini-cloud",
                }
        except (OSError, KeyError, ValueError):
            pass  # fallback to local mock benchmark on any network/parse error

    # Fallback / Simulated Inference for Zero-latency offline evaluation
    # Deterministic simulation matching each persona's tone for benchmarking
    simulated_responses = {
        "gp_direct": {
            "hunting_for_p2": "Gap to Max is 0.8. You have DRS and 0.8 laps fuel in hand. Mode push now.",
            "defending_worn_tyres": "Negative, stay out. Hamilton is 0.4 behind. Park it on the apex in Curva Grande, head down.",
            "safety_car_dilemma": "Box box! Soft tyre set 2. We pit from P2, commit now!",
            "system_check_status": "P4. Gap ahead 1.9 to Piastri. Temps nominal, car is clean. Get on with it.",
        },
        "bono_calm": {
            "hunting_for_p2": "Okay, gap is 0.8 to Max. You have DRS. It's Hammer time, let's hunt him down.",
            "defending_worn_tyres": "Understood, rears are hot at 125. Hamilton is 0.4 behind. Manage the exits, do not box.",
            "safety_car_dilemma": "Box box, box box. Pitting for Softs. Rejoin P3 with fresh rubber. You've got this.",
            "system_check_status": "Loud and clear. P4, 1.9 to Piastri. Tyre wear 34%, all temps in the window.",
        },
        "drill_hunter": {
            "hunting_for_p2": "Max's hards are 22 laps old, he's bleeding grip! Unleash the battery, dive into Turn 1 now!",
            "defending_worn_tyres": "Fight him off! Break his tow on the straight, dump your ERS before the chicane!",
            "safety_car_dilemma": "Box box! Slap on the softs and let's go on the attack at the restart!",
            "system_check_status": "All systems green! Piastri is 1.9 ahead, reel him in!",
        },
        "chess_master": {
            "hunting_for_p2": "Gap 0.8. Max is on 22-lap hards. Protect your rears out of Turn 4, overtake is inevitable.",
            "defending_worn_tyres": "Pitting drops us to P4. Hamilton will degrade soon. Protect the exit, play the long game.",
            "safety_car_dilemma": "Box this lap. Delta under SC is only 12s. Soft set 2 gives us optimal tyre offset.",
            "system_check_status": "Status nominal. Tyre deg at 34%, tracking 0.2% better than target. Fuel positive.",
        },
        "dry_humor": {
            "hunting_for_p2": "Max is 0.8 ahead. Try not to use his gearbox as your brake marker this time.",
            "defending_worn_tyres": "Rears are cooking breakfast. Stay on track, Lewis isn't giving you an autograph.",
            "safety_car_dilemma": "Box box. Don't miss the pit wall, free pit stop incoming.",
            "system_check_status": "Radio works. Car is in one piece, which is a pleasant surprise. Carry on.",
        },
        "telemetry_nerd": {
            "hunting_for_p2": "Delta -0.85s. DRS active. Optimal tyre temp window: 104C. Deploy ERS sector 2.",
            "defending_worn_tyres": "Rear surface 126C, 68% deg. Hamilton 0.45s behind. Brake bias +2% forward recommended.",
            "safety_car_dilemma": "Box box. SC delta 12s vs 23.5s normal. Fresh Soft 2 will have +1.4s/lap delta.",
            "system_check_status": "P4. Delta +1.9s. FL 100C, FR 104C. Battery 61%. Zero aero damage.",
        },
        "ferrari_drama": {
            "hunting_for_p2": "We see the gap is 0.8. Mode push or stay behind, question?",
            "defending_worn_tyres": "Tyres are dead. We are checking Plan D. Stay out, question?",
            "safety_car_dilemma": "Safety car deployed! Box for softs or stay out for track position, question?",
            "system_check_status": "Radio is loud. We are checking telemetry. Stay focused.",
        },
        "podium_defender": {
            "hunting_for_p2": "Close the 0.8s gap cleanly. Save 10% battery for the main straight pass.",
            "defending_worn_tyres": "Rears are critical. Park it right on the apex, break Hamilton's tow on exit!",
            "safety_car_dilemma": "Box box! If we stay out we are sitting ducks. Pitting secures the podium.",
            "system_check_status": "P4 secure. 2.3s buffer to Sainz. Defend the inside line if he closes.",
        },
        "hype_spotter": {
            "hunting_for_p2": "You're all over him buddy! 8 tenths back, DRS wide open! Smoke him into Turn 1!",
            "defending_worn_tyres": "Dig deep! Lewis is on your bumper, make your car as wide as a truck!",
            "safety_car_dilemma": "Yellow yellow yellow! Box box box, let's grab some fresh boots!",
            "system_check_status": "Reading you 5 by 5! P4 and flying, keep hammering it!",
        },
        "iceman_minimal": {
            "hunting_for_p2": "P3. Gap 0.8. DRS. Push.",
            "defending_worn_tyres": "Negative box. Rears hot. Defend.",
            "safety_car_dilemma": "Box box now. Softs.",
            "system_check_status": "P4. All good. Head down.",
        },
    }

    # Determine best simulated response by scanning scenario keys in the prompt
    resp = simulated_responses.get(persona_id, {}).get(
        "hunting_for_p2", "Copy, pushing now."
    )

    # lookup by query matching
    for scen_key, scen in MOCK_SCENARIOS.items():
        if scen["driver_query"] in prompt:
            resp = simulated_responses.get(persona_id, {}).get(scen_key, resp)
            break

    latency_ms = 1.2  # Tier 1 / pre-computed local mock
    return {"text": resp, "latency_ms": latency_ms, "source": "local-simulated"}
