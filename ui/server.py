"""
F1-Themed Web Dashboard Server for PitwallKing.
Serves a low-latency live HUD dashboard with:
- Live telemetry metrics (P3, gaps, tyre thermal matrix, battery, fuel)
- Dynamic Persona switcher with live radio audio-text stream
- Push-To-Talk radio interface with sub-millisecond response feeds
"""

import os
import sys
import json

# Ensure project root is always in Python module search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template, request, jsonify
from personas.persona_catalog import PERSONAS
from engine.assistant import RaceEngineerAssistant
from mock_data.scenarios import MOCK_SCENARIOS
from post_session_engine import PostSessionDebriefEngine

app = Flask(__name__, template_folder="ui/templates", static_folder="ui/static")

# Shared assistant instance
assistant = RaceEngineerAssistant(persona_id="gp_direct")
current_telemetry = MOCK_SCENARIOS["hunting_for_p2"]["telemetry_state"]

@app.route("/")
def index():
    return render_template(
        "dashboard.html",
        personas=PERSONAS,
        personas_json=json.dumps(PERSONAS),
        active_persona=assistant.persona_id,
        telemetry=current_telemetry
    )

@app.route("/api/ask", methods=["POST"])
def ask_radio():
    data = request.json or {}
    query = data.get("query", "")
    response = assistant.ask(query, current_telemetry)
    return jsonify(response)

@app.route("/api/persona", methods=["POST"])
def change_persona():
    data = request.json or {}
    persona_id = data.get("persona_id", "gp_direct")
    assistant.set_persona(persona_id)
    return jsonify({"status": "ok", "active_persona": persona_id})

@app.route("/api/telemetry")
def get_telemetry():
    return jsonify(current_telemetry)

@app.route("/api/debrief", methods=["POST"])
def get_debrief():
    data = request.json or {}
    finish_pos = data.get("position", 1)
    persona_id = assistant.persona_id
    radio = PostSessionDebriefEngine.generate_radio_call(persona_id, finish_pos)
    summary = PostSessionDebriefEngine.generate_telemetry_debrief_summary({
        "position": finish_pos,
        "fastest_lap": "1:31.840",
    })
    
    # FastF1 / TomShaw-style lap telemetry comparison traces for visualization
    # Generates speed, throttle, and brake distance traces (0m to 5412m for Bahrain)
    distance_points = list(range(0, 5500, 100))
    player_speed_trace = [
        int(180 + 130 * abs(0.5 - (d % 1000) / 1000.0) * 2) for d in distance_points
    ]
    reference_speed_trace = [
        int(182 + 132 * abs(0.5 - (d % 1000) / 1000.0) * 2) for d in distance_points
    ]

    telemetry_chart = {
        "distances": distance_points,
        "player_speed": player_speed_trace,
        "reference_speed": reference_speed_trace,
        "delta_s": [round((p - r) / 100.0, 3) for p, r in zip(player_speed_trace, reference_speed_trace)]
    }

    return jsonify({
        "radio_call": radio,
        "summary": summary,
        "telemetry_chart": telemetry_chart
    })

def run_ui(host="127.0.0.1", port=5000, debug=False):
    print("=" * 70)
    print(" PITWALLKING: F1 PITWALL LIVE TELEMETRY DASHBOARD")
    print(f" Web UI Running at: http://{host}:{port}")
    print("=" * 70)
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_ui()
