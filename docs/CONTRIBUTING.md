# Contributing to WorkplacePulse

Thank you for your interest in contributing to **WorkplacePulse**! We welcome bug fixes, documentation improvements, and feature extensions.

## 🛠️ Development Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/GitPhantom700/workplace_pulse.git
   cd workplace_pulse
   ```

2. **Run Quickstart:**
   ```bash
   ./setup.sh
   ```

3. **Execute Automated Tests:**
   ```bash
   pytest -v tests/
   ```

## 📜 Coding Guidelines

* **Python 3.9+ (3.11 in production):** Adhere to Google Python Style Guide with strict type hints. The production container runs `python:3.11-slim` and CI targets 3.11; the bundled local virtualenv is 3.9.
* **Zero Hardcoded Secrets:** Always utilize Cloud Secret Manager or environment variables. Never commit credentials.
* **Hermetic Tests:** Ensure all new features have unit and contract tests in `tests/`.

## 🤝 Code of Conduct

All contributors must adhere to our [Code of Conduct](../CODE_OF_CONDUCT.md).
