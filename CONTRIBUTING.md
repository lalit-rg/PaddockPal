# Contributing to ApexAI: Virtual F1 Racecraft Engineer 🏎️🏁

First off, thank you for considering contributing to **ApexAI**! 

ApexAI is built to solve one of the hardest problems in sim-racing AI: **delivering deep, tactical racecraft advice at 300+ km/h without latency bottlenecks.** Whether you are an inference engineer, motorsport telemetry analyst, sim-racer, or prompt engineer, your insights are welcome.

---

## 🎯 Guiding Engineering Principles

Before contributing code, please keep our core tenets in mind:

1. **The Latency Hierarchy is Sacred:**
   - **Tier 1 (< 1ms):** Pure deterministic slot-filling from the `TelemetryRingBuffer`. Never route simple telemetry queries (gaps, tyre temps, status checks) to an LLM.
   - **Tier 2 (50–150ms):** Quantized Small Language Models (SLMs) running locally with pre-warmed KV caches.
   - **Tier 3 (500–1500ms):** Complex cloud strategy farm. Always pair with a $<30\text{ms}$ speculative radio acknowledgment to mask network wait time.
2. **Minimalism First (`Ponytail` Philosophy):**
   - The best code is the code you never wrote.
   - Favor Python's standard library (`socket`, `struct`, `dataclasses`, `deque`, `math`) over bulky dependencies.
3. **Authentic Motorsport Racecraft:**
   - Heuristics must reflect real FIA regulations (track limits, illegal passes), vehicle dynamics (carcass vs. surface temperatures, trail-braking deceleration slopes), and strategic math (clean-air pit slots, Safety Car probability).

---

## 🛠️ Areas Where We Need Contributions

### 1. New Race Engineer Personas
Have an idea for a legendary race engineer or driver personality?
- Add your profile to `personas/persona_catalog.py`.
- Include:
  - `id` & `name`
  - `iconic_taglines`: 4–6 authentic radio calls.
  - `system_prompt`: Token-budgeted prompt ($\le 22$ words ceiling) with strict persona tone.
  - `sample_acknowledgments`: Instant $<30\text{ms}$ radio masking soundbites.

### 2. Telemetry Ingestion & Sim Support
- Currently, `telemetry/udp_receiver.py` is configured for **EA Sports F1 (2023, 2024, 2025)**.
- Contributions to add packet parsers for **Assetto Corsa / ACC (Shared Memory)**, **iRacing (SDK)**, and **rFactor 2** are highly encouraged!

### 3. Prescriptive Strategy Formulas
Help refine the decision matrices in `racecraft_engine.py` and `telemetry_analytics.py`:
- Tyre wear degradation curves per track layout (high-energy circuits like Silverstone vs low-energy like Monza).
- Dirty air aerodynamic wake decay formulas.
- Dynamic undercut/overcut pit loss calculations with tire warmup deltas.

### 4. Audio Post-Processing & TTS Integration
- Adding local ultra-low latency TTS providers (e.g. **Piper TTS**, **Sherpa-ONNX**).
- Realistic radio FX filters (300Hz–3400Hz bandpass filter, walkie-talkie chirp, background static).

---

## 🚀 Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/lalit-rg/ApexAI-F1RaceEngineer.git
cd ApexAI-F1RaceEngineer
```

### 2. Verify Your Environment
No heavy dependencies are required. Standard Python 3.10+ works out of the box:
```bash
python main.py
```

### 3. Run Test Suites
Always run the validation scripts before submitting a PR:
```bash
# 1. Multi-persona inference bench
python run_test.py

# 2. Racecraft & traffic slot evaluation
python run_advanced_strategy.py

# 3. Post-session cooldown & telemetry debrief
python run_post_session_demo.py
```

### 4. Commit Guidelines
We follow standard Conventional Commits:
- `feat: add Assetto Corsa Competizione shared memory receiver`
- `fix: adjust intermediate tyre crossover wetness threshold to 18%`
- `perf: optimize circular ring buffer wear slope computation`
- `docs: add track-specific safety car probability documentation`

---

## 💬 Community & Ideas
Feel free to open an **Issue** or start a **Discussion** to debate telemetry dynamics, share your own telemetry traces, or propose new strategy algorithms!
