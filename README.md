# PitWallOS: High-Frequency Multi-Sim Telemetry & Racecraft Copilot

> **Low-latency, local-first virtual race engineer and telemetry engine for sim-racing and esports.**
> Supports EA Sports F1 (2023–2025) via UDP, Assetto Corsa / ACC via Windows Shared Memory, and iRacing via pyirsdk.

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Sim Support](https://img.shields.io/badge/sims-F1%20%7C%20ACC%20%7C%20iRacing-red.svg)](#multi-sim-modularity)
[![Latency Tier](https://img.shields.io/badge/Tier--1%20Lookup-%3C0.5ms-brightgreen.svg)](#the-latency-hierarchy)

---

## Why PitWallOS?

In competitive sim racing, human driver reaction time is ~200ms. Sending telemetry to a commercial cloud LLM introduces 1.5–3.0 seconds of latency—making the output outdated before it can be spoken.

PitWallOS replaces naive LLM wrappers with a **tiered inference architecture**:
1. **Tier 1 (< 0.5ms):** Lock-free circular state buffer that directly serves metric lookups (gaps, tyre temps, telemetry status) without language models.
2. **Tier 2 (80–150ms):** Local quantized SLM runner with pre-warmed KV cache for quick tactical checks (*"Can I push?"*).
3. **Tier 3 (Async Cloud):** Deep strategy evaluations (Safety Car probability, clean-air pit windows, undercut vs overcut) paired with **< 30ms speculative audio acknowledgments** (*"Copy, standby"*), completely masking network delay.

---

## Architecture Overview

```
                      [ Driver Radio Input / PTT Wheel Button ]
                                         │
                             Intent Classifier (<3ms)
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          ▼                              ▼                              ▼
   Tier 1: Deterministic          Tier 2: Speculative           Tier 3: Asynchronous
       (< 0.5ms latency)          (80 - 150ms latency)          (500 - 1500ms latency)
   ──────────────────────        ─────────────────────          ──────────────────────
   • "Status check"              • "Can I push now?"            • "Safety car! Do we box?"
   • "Gap ahead / behind"        • "How is my pace?"            • "Plan B vs Plan C"
   • "Tyre temps and wear"       • Corner exit advice           • Traffic window simulation
   
   Direct memory ring-buffer     Local int4 SLM                 Cloud LLM Farm +
   slot-fill (Zero LLM)          (Qwen / Llama via llama.cpp)   Speculative Radio Ack Masking
```

---

## Multi-Sim Modularity

PitWallOS decouples strategy and voice logic from individual sim engines via a canonical `NormalizedTelemetryFrame`:

| Game / Platform | Protocol | Send Rate | Supported Features |
|---|---|---|---|
| **EA Sports F1 (23–25)** | UDP Sockets (`20777`) | 60Hz | Cross-platform (PC / PS5 / Xbox over LAN), ERS modes, tyre wear, FIA warnings |
| **Assetto Corsa & ACC** | Windows MMF (`acpmf_physics`) | 100Hz | Zero-lag shared memory, exact tyre pressures (PSI), brake disc heat, slip angles |
| **iRacing** | iRacing SDK Memory-Mapped File | 60Hz | Class position deltas, incident points, multi-class traffic gaps |
| **MoTeC i2 / McLaren ATLAS** | CSV Stream Reader | Up to 100Hz | Real motorsport data acquisition playback |

---

## 10 Trackside Engineer Personas

Each persona has strict token-budgeted system prompts, radio cadences, and signature taglines:
- **The Commander (Gianpiero Lambiase / Max Verstappen):** Blunt, disciplined (*"Mode push"*, *"Head down"*, *"Give the position back"*).
- **The Anchor (Peter 'Bono' Bonnington / Lewis Hamilton):** Ultra-calm (*"Hammer time"*, *"In in in!"*, *"Target plus 2"*).
- **The Shark (Fernando Alonso):** Opportunistic predator (*"All the time you have to leave a space!"*, *"Pass him with DRS"*).
- **The Professor of Strategy (Sebastian Vettel):** Obsessive rulebook & radar analyst (*"Black and white flag at Copse"*, *"Plan C delta is +4s"*).
- **The Surgical Minimalist (Alain Prost):** Minimum required effort to win, zero unneeded mechanical wear.
- **The Unfiltered Realist (Guenther Steiner):** Brutal honesty & banter (*"We look like rockstars!"*, *"Don't be an idiot!"*).
- **The Aerodynamicist (Adrian Newey / Telemetry Nerd):** Carcass vs. surface heat, brake bias %, differential offsets.
- **The Dramatic Pit Wall (Ferrari / Xavier Marcos):** Multiple conflicting plans, ends queries with *"Question?"*.
- **The Spotter (NASCAR / IndyCar):** High-energy, clears blind spots (*"Clear high, green green green!"*).
- **The Ice Man (Kimi Räikkönen):** Zero fluff ($\le 8$ words: *"P3. Gap 0.8. Push."*).

---

## Quick Start

### 1. Installation
We use [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management:

```bash
# Clone the repository
git clone https://github.com/lalit-rg/ApexAI-F1RaceEngineer.git
cd ApexAI-F1RaceEngineer

# Create virtual environment and install dependencies
uv venv
uv pip install -e .
```

### 2. Launch the Web Telemetry Dashboard
```bash
.venv\Scripts\python ui\server.py
```
Open **`http://127.0.0.1:5000`** in your browser.

- Click **🔌 CONNECT GAME / PS5** to inspect your auto-detected LAN IP and platform instructions.
- Click **🏁 POST-RACE DEBRIEF** to view the FastF1-style telemetry speed trace and listen to post-race radio feedback.

### 3. Launch CLI Assistant
```bash
.venv\Scripts\python main.py
```

---

## Project Structure

```
PitWallOS/
├── engine/
│   ├── assistant.py          # Unified race engineer orchestrator
│   └── tier1_engine.py       # Sub-millisecond deterministic slot-filling (<0.5ms)
├── telemetry/
│   ├── adapter_interface.py  # Canonical NormalizedTelemetryFrame schema
│   ├── sim_adapters.py       # Game-specific adapters (F1 UDP, ACC MMF, iRacing SDK)
│   ├── connection_bridge.py  # Universal LAN bridge for PS5/Xbox & pro software
│   ├── ring_buffer.py        # Circular buffer for 60Hz rolling telemetry window
│   └── udp_receiver.py       # Low-level socket parser for EA Sports F1
├── personas/
│   └── persona_catalog.py    # 10 F1 legends with token-budgeted prompts
├── racecraft_engine.py       # Traffic rejoin windows, SC probability, steward rules
├── telemetry_analytics.py    # Descriptive (facts) vs Prescriptive (directives) engine
├── post_session_engine.py    # Checkered flag cooldown radio & FastF1 trace debrief
├── ui/
│   ├── server.py             # Flask dashboard backend
│   └── templates/
│       └── dashboard.html    # F1 broadcast HUD with HTML5 Canvas trace charts
└── pyproject.toml            # uv / hatchling package configuration
```

---

## Contributing

We welcome contributions from motorsport telemetry engineers, sim-racers, and inference developers. See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Adding telemetry adapters for additional sims (rFactor 2, Automobilista 2).
- Implementing local low-latency TTS backends (Piper TTS, Sherpa-ONNX).
- Refining aerodynamic dirty air and tyre thermal mathematical models.

## License
MIT License. See [LICENSE](LICENSE) for details.
