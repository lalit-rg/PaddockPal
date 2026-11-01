# PitwallKing: Low-Latency Virtual Multi-Sim Racecraft Engineer 🏎️👑

An on-prem, multi-tiered inference and racecraft strategy engine designed for EA Sports F1, Assetto Corsa / ACC, and iRacing. Built from a **Senior Inference Engineering** perspective to conquer real-time latency bottlenecks at 300+ km/h.

📖 **Complete User Flow & Setup Guide:** See [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

---

## ⚡ The Latency Problem & Multi-Tier Architecture

In racing, human reaction time is ~200ms. Routing every simple telemetry inquiry (*"What's my gap?"*, *"Tyre check"*) to a cloud LLM with 1.5–3.0s latency is useless and dangerous. 

ApexAI implements a **3-Tier Hierarchical Inference Pipeline**:

```
                       [ Driver Voice / Steering Wheel PTT ]
                                         │
                             Intent Classifier (<3ms)
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          ▼                              ▼                              ▼
   Tier 1: Deterministic          Tier 2: Speculative           Tier 3: Asynchronous
       (< 1ms latency)            (80 - 150ms latency)          (500 - 1500ms latency)
   ──────────────────────        ─────────────────────          ──────────────────────
   • "Radio / System check"      • "Can I push now?"            • "Safety car! Do we box?"
   • "Gap ahead / behind"        • "How is my pace?"            • "Plan B vs Plan C"
   • "Tyre temps and wear"       • Corner exit advice           • Full stint re-simulation
   
   Direct memory ring-buffer     Local int4 SLM                 Cloud LLM Farm +
   slot-fill (Zero LLM)          (Qwen / Llama via llama.cpp)   Speculative Radio Ack Masking
```

---

## 🏁 Key Features

### 1. Ten Real-World F1 Personas (with Iconic Catchphrases)
Each persona has a KV-cache warm system prompt, authentic delivery cadence, and signature taglines:
- **The Commander (Gianpiero Lambiase / Max Verstappen):** Blunt, disciplined (*"Mode push"*, *"Head down"*, *"Give the position back"*).
- **The Anchor (Peter 'Bono' Bonnington / Lewis Hamilton):** Ultra-calm, reassuring (*"It's Hammer time"*, *"In in in in in!"*, *"Target plus 2"*).
- **The Shark (Fernando Alonso):** Opportunistic predator (*"All the time you have to leave a space!"*, *"Pass him with DRS"*).
- **The Professor of Strategy (Sebastian Vettel):** Obsessive rulebook & radar analyst (*"Ring-ding-ding!"*, *"Black and white flag Copse"*).
- **The Surgical Minimalist (Alain Prost):** Minimum required effort to win, zero unnecessary risk.
- **The Unfiltered Realist (Guenther Steiner):** Dry wit & roasts (*"We look like rockstars!"*, *"Don't be an idiot!"*).
- **The Aerodynamicist (Adrian Newey / Telemetry Nerd):** Carcass vs. surface temps, brake bias %, differential offsets.
- **The Dramatic Pit Wall (Ferrari / Xavier Marcos):** Plan A through F, ends choices with *"Question?"*.
- **The Spotter (NASCAR / IndyCar):** High-energy, clears blind spots (*"Clear high, green green green!"*).
- **The Ice Man (Kimi Räikkönen):** Absolute zero fluff ($\le 8$ words: *"P3. Gap 0.8. Push."*).

---

### 2. Advanced Racecraft & Decision Dynamics
- **Regulatory Enforcements:** Illegal off-track overtakes detect positions that must be yielded before the next turn to prevent 5-second penalties; tracks 3-strike track limits and issues **Black and White Flags**.
- **Traffic Rejoin & Clean Air Window:** Computes circuit-specific pit deltas (e.g. Monza 24.0s green, 13.5s SC) and evaluates grid vectors. If pitting rejoins within $<2.0\text{s}$ behind a slow car in dirty air, the engine directs the driver to **`EXTEND_AVOID_TRAFFIC`**.
- **Weather & Track Evolution:** Tracks water saturation and triggers **Intermediate crossover** at $>20\%$ track wetness.
- **Circuit-Specific Safety Car Probability:** Incorporates historical track baselines (e.g., Singapore 89%, Monaco 82% vs. Barcelona 28%).
- **Post-Session Cooldown & FastF1 Telemetry Debrief:** Celebratory / recovery radio calls and structured telemetry summaries (apex consistency, trail-braking slope, dirty air time lost).

---

## 🚀 Quick Start

### Run Main Assistant Interactive Demo
```bash
python main.py
```

### Run Multi-Persona Inference Test Bench
```bash
python run_test.py
```

### Run Advanced Racecraft & Traffic Window Engine
```bash
python run_advanced_strategy.py
```

### Run Post-Session Telemetry & Radio Debrief
```bash
python run_post_session_demo.py
```
