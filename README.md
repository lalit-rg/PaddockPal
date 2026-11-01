# PaddockPal: High-Frequency Multi-Sim Telemetry & Low-Latency Racecraft Engine

> **"Choose your pal before you go flying."**  
> An open-source, local-first virtual race engineer and telemetry testbed built to explore **ultra-low-latency LLM inference systems** in real-time environments at 300+ km/h.

[![CI Quality Gate](https://github.com/lalit-rg/PaddockPal/actions/workflows/ci.yml/badge.svg)](https://github.com/lalit-rg/PaddockPal/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tier-1 Latency](https://img.shields.io/badge/Tier--1%20Lookup-%3C0.5ms-brightgreen.svg)](#inference-architecture)
[![Author](https://img.shields.io/badge/Maintainer-lalit--rg-red.svg)](https://www.linkedin.com/in/lalit-rg/)

---

## 🎯 Not Just a Weekend AI Project: A Live Inference Systems Testbed

Most LLM applications operate in async or chat contexts where a 1.5–3.0 second response time is acceptable. **Motorsport simulation breaks this assumption.**

At 300+ km/h, human driver reaction time is ~200ms. If your AI takes 2 seconds to answer *"What's my gap behind?"*, the driver has already covered 160 meters and missed their braking marker.

**PaddockPal is built as a systems engineering case study** for solving latency bottlenecks under strict real-time telemetry streaming constraints:
- **Zero-Copy Ingestion:** Lock-free circular state buffers processing 60Hz UDP & 100Hz Windows Shared Memory packets.
- **Hierarchical Inference Tiers:** Decoupling deterministic lookups from speculative reasoning and heavy cloud LLMs.
- **Speculative Latency Masking:** Pre-rendered radio telemetry acknowledgments (< 30ms) masking async network calls.
- **Token-Budgeted KV Cache Optimization:** Pre-warmed persona prompts with strict output ceilings ($\le 20$ words).

---

## ⚡ The 3-Tier Inference Architecture

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

## 🏎️ Choose Your Pal: 10 Iconic Personalities

Each pal brings distinct tactical behavior, prompt token budgets, and authentic radio cadences:

| Pal | Real-World Persona | Archetype | Signature Callouts |
|---|---|---|---|
| **The Commander** | Gianpiero Lambiase (GP) | Aggressive / Direct | *"Mode push"*, *"Head down"*, *"Give position back"* |
| **The Anchor** | Peter 'Bono' Bonnington | Calm / Composed | *"It's Hammer time"*, *"In in in!"*, *"Target plus 2"* |
| **The Shark** | Fernando Alonso | Opportunistic Predator | *"All the time you have to leave a space!"*, *"Pass with DRS"* |
| **The Professor of Strategy**| Sebastian Vettel | Mathematical Precision | *"Black and white flag at Copse"*, *"Plan C delta is +4s"* |
| **The Surgical Minimalist** | Alain Prost | Pure Efficiency | Minimum required effort to win, zero excess mechanical wear |
| **The Unfiltered Realist** | Guenther Steiner | Raw Banter / Honesty | *"We look like rockstars!"*, *"Don't be an idiot!"* |
| **The Aerodynamicist** | Adrian Newey / Trackside | Vehicle Dynamics | Carcass vs. surface heat, brake bias %, differential offsets |
| **The Dramatic Pit Wall** | Ferrari / Xavier Marcos | Chaotic / Quirky | Multiple plans, ends strategic choices with *"Question?"* |
| **The Spotter** | NASCAR / IndyCar Spotter | High-Energy Coach | *"Clear high, hammer down buddy!"*, *"Green green green!"* |
| **The Ice Man** | Kimi Räikkönen | Minimalist ($\le 8$ words) | *"P3. Gap 0.8. Push."*, *"Leave me alone."* |

---

## 🎮 Multi-Sim Telemetry Standardization

PaddockPal decouples game-specific protocols into a canonical `NormalizedTelemetryFrame`:

| Game / Platform | Ingestion Protocol | Update Rate | Special Features |
|---|---|---|---|
| **EA Sports F1 (23–25)** | UDP Sockets (`20777`) | 60Hz | Cross-platform (PC / PS5 / Xbox over LAN), ERS modes, FIA penalties |
| **Assetto Corsa & ACC** | Windows MMF (`acpmf_physics`) | 100Hz | Zero-lag shared memory, exact tyre pressures (PSI), disc temps |
| **iRacing** | iRacing SDK Memory-Mapped File | 60Hz | Class position deltas, incident points, multi-class traffic gaps |
| **MoTeC i2 / McLaren ATLAS**| CSV Stream Reader | Up to 100Hz | Professional motorsport telemetry playback |

---

## 🚀 Quick Start

### 1. Installation via `uv`
We use [uv](https://github.com/astral-sh/uv) for fast, deterministic dependency locking:

```bash
git clone https://github.com/lalit-rg/PaddockPal.git
cd PaddockPal

# Create virtual environment and install with uv
uv venv
uv pip install -e .
```

### 2. Launch the F1 Broadcast Web Dashboard
```bash
.venv\Scripts\python ui\server.py
```
Open **`http://127.0.0.1:5000`** in your browser.
- **🔌 CONNECT GAME / PS5:** Auto-detects your local LAN IP and guides console setup.
- **🏁 POST-RACE DEBRIEF:** Displays interactive FastF1-style speed traces overlaying your laps against session references.

### 3. Run the CLI Race Engineer
```bash
.venv\Scripts\python main.py
```

---

## 🛡️ Engineering Rigor & Contributing

To maintain production standards, we enforce strict PR gates:
- **No Direct Commits to `main`:** All changes require a feature branch and an approved Pull Request.
- **Automated CI Quality Gate:** Every PR runs `ruff` linting and `pytest` test suites.
- **Deterministic Latency Benchmarks:** Tier 1 lookups must execute in $<1.0\text{ms}$.

Read our [CONTRIBUTING.md](CONTRIBUTING.md) for pre-commit hooks, branch naming conventions, and setup instructions.

---

## 👨‍💻 Maintainer & Contact

Maintained by **Lalit** ([LinkedIn: @lalit-rg](https://www.linkedin.com/in/lalit-rg/)).  
Feel free to open an issue or connect on LinkedIn to discuss real-time inference systems, motorsport telemetry, or sim-racing setups!

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
