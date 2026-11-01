# Contributing to PaddockPal 🏎️🏁

> **"Choose your pal before you go flying."**  
> We treat PaddockPal as an engineering case study on **real-time low-latency inference systems**. Contributions are welcome from motorsport engineers, telemetry analysts, and AI developers.

To keep the codebase reliable, maintainable, and free of bloat, we enforce strict PR gates and engineering standards.

---

## 🚫 Hard Rule: Nobody Pushes Directly to `main`

- **Branch Protection:** The `main` branch is locked. All updates must arrive via a dedicated feature branch and an approved Pull Request.
- **Passing CI Required:** The GitHub Actions Quality Gate must pass all linting, formatting, and unit tests before any PR can be merged.

### Branch Naming Conventions
- `feat/add-acc-pitstop-adapter`
- `fix/tyre-thermal-crossover-threshold`
- `perf/ring-buffer-lock-free-optimization`
- `docs/add-motec-integration-guide`

---

## 🛠️ Developer Setup & Pre-Commit Hooks

### 1. Clone & Set Up Isolated Environment (`uv`)
```bash
git clone https://github.com/lalit-rg/PaddockPal.git
cd PaddockPal

# Set up virtual environment and install dev dependencies
uv venv
uv pip install -e .
uv pip install pytest ruff pre-commit
```

### 2. Install Git Pre-Commit Hooks
Run this once so pre-commit hooks check your code automatically before every git commit:
```bash
pre-commit install
```
This automatically runs:
- `ruff check . --fix` (linting standards)
- `ruff format .` (PEP 8 code style)
- File hygiene (trailing whitespace, YAML/JSON validation)

---

## ⏱️ The Latency SLA (Strict Engineering Rules)

When contributing code, you must respect our **3-Tier Latency Hierarchy**:

1. **Tier 1 (< 1.0ms SLA):**
   - Telemetry queries (*"Gap ahead"*, *"Tyre temps"*, *"Status check"*) **MUST NEVER** make network calls or query LLMs.
   - They must read directly from the in-memory circular `TelemetryRingBuffer` via deterministic slot-filling.
   - Any PR that introduces an LLM call into a Tier-1 code path will be rejected.
2. **Tier 2 (50–150ms):**
   - Local quantized Small Language Models (e.g. Qwen2.5 / SmolLM2 via `llama.cpp` or ONNX).
   - Prompt context is limited to $<256$ tokens with pre-warmed KV caches.
3. **Tier 3 (500–1500ms):**
   - Cloud LLM strategy farm (Gemini / OpenAI).
   - **Must always be paired with a $<30\text{ms}$ speculative radio acknowledgment** (*"Copy, stand by"*, *"Checking with pit wall"*) so the driver never experiences dead silence on track.

---

## 🧪 Testing Before Submitting a PR

Always run the full test suite and linter before pushing your branch:

```bash
# 1. Run unit tests & sub-millisecond SLA latency benchmarks
.venv\Scripts\pytest tests/ -v

# 2. Run Ruff linter & formatter
.venv\Scripts\ruff check .
.venv\Scripts\ruff format --check .
```

All 7 core test suites (deterministic lookups, illegal overtake yield orders, track limits strike 3, traffic rejoin calculations, weather crossover, and persona integrity) must pass.

---

## 🏎️ Areas Where Contributions Are Encouraged

1. **Multi-Sim Ingestion Adapters:**
   - Real implementations for `IRacingAdapter` via `pyirsdk`.
   - Assetto Corsa Competizione shared memory parser via `ctypes`.
   - Le Mans Ultimate (LMU) / rFactor 2 shared memory pipes.
2. **Local TTS Voice Generation:**
   - Local Piper TTS / Sherpa-ONNX runner with authentic team radio bandpass filtering (300Hz–3400Hz).
3. **Vehicle Dynamics Telemetry:**
   - Corner-by-corner trail-braking deceleration slopes ($G_x$).
   - Slip-angle estimations from steer angle and lateral $G_y$.

---

## 🤝 Questions & Discussion

Project lead: **Lalit** ([LinkedIn: @lalit-rg](https://www.linkedin.com/in/lalit-rg/)).  
Feel free to open an issue or connect on LinkedIn to discuss real-time systems, racecraft telemetry, or sim racing setups!
