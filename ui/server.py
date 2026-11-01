"""
F1-Themed Web Dashboard Server for PitwallKing.
Serves a low-latency live HUD dashboard with:
- Live telemetry metrics (P3, gaps, tyre thermal matrix, battery, fuel)
- Dynamic Persona switcher with live radio audio-text stream
- Push-To-Talk radio interface with sub-millisecond response feeds
"""

import json
from flask import Flask, render_template, request, jsonify
from personas.persona_catalog import PERSONAS
from engine.assistant import RaceEngineerAssistant
from mock_data.scenarios import MOCK_SCENARIOS

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

def run_ui(host="127.0.0.1", port=5000, debug=False):
    print("=" * 70)
    print(" PITWALLKING: F1 PITWALL LIVE TELEMETRY DASHBOARD")
    print(f" Web UI Running at: http://{host}:{port}")
    print("=" * 70)
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_ui()
