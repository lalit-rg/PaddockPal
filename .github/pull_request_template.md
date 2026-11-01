## Pull Request Guidelines

Thank you for contributing to **PaddockPal**! Please ensure your PR satisfies the following checks before submitting.

---

### Description of Changes
*Provide a concise summary of what this PR introduces (feature, bug fix, telemetry adapter, or persona).*

### Type of Change
- [ ] 🏎️ New Sim Telemetry Adapter (e.g. Assetto Corsa, iRacing, rFactor 2)
- [ ] ⏱️ Latency Optimization / Ingestion Pipeline improvement
- [ ] 🧠 Strategic Formula / Racecraft Decision logic refinement
- [ ] 🎙️ New Race Engineer Persona profile
- [ ] 🐛 Bug fix / Regression test

### Performance & Latency Checklist
- [ ] **Tier 1 (< 1ms):** Does not introduce any LLM calls into deterministic metric lookups.
- [ ] **Minimal Dependencies:** Adheres to Python standard library primitives where possible.
- [ ] **Tests Passing:** `pytest tests/` executed and passing.
- [ ] **Linted & Formatted:** Passed `ruff check .` and `ruff format .`

### Connected Issues
Closes #
