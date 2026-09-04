#!/usr/bin/env bash
# ==============================================================================
# WorkplacePulse — Automated Zero-Friction Setup Script
# Google Cloud Run AI Challenge ()
# Compatible with macOS, Linux, and Google Cloud Shell
# ==============================================================================

set -euo pipefail

# ANSI Color Codes for Rich Terminal Output
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m" # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

banner() {
    echo -e "${CYAN}"
    echo "======================================================================"
    echo "         🚀 WorkplacePulse — Predictive Ops Command Center            "
    echo "      Google Cloud Run AI Challenge () Setup Automation        "
    echo "======================================================================"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ------------------------------------------------------------------------------
# 1. Verify Python 3.10+ Runtime
# ------------------------------------------------------------------------------
check_python() {
    log_info "Verifying Python runtime environment..."
    PYTHON_BIN=""

    # Check for available python binaries in order of preference
    for candidate in python3 python python3.12 python3.11 python3.10; do
        if command -v "$candidate" &>/dev/null; then
            # Verify it is Python 3.10+
            if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
                PYTHON_BIN="$candidate"
                break
            fi
        fi
    done

    # If no system Python 3.10+ found, check if existing .venv has Python 3.10+
    if [ -z "$PYTHON_BIN" ] && [ -f ".venv/bin/python" ]; then
        if .venv/bin/python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
            PYTHON_BIN=".venv/bin/python"
        fi
    fi

    if [ -z "$PYTHON_BIN" ]; then
        log_error "Python 3.10 or higher is required but was not found on PATH."
        log_error "Please install Python 3.10+ (e.g., via brew install python@3.11 or apt install python3) and re-run."
        exit 1
    fi

    PY_VERSION=$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    log_success "Found Python version: ${PY_VERSION} (using ${PYTHON_BIN})"
}

# ------------------------------------------------------------------------------
# 2. Configure Python Virtual Environment (.venv) & Install Dependencies
# ------------------------------------------------------------------------------
setup_venv() {
    log_info "Configuring Python virtual environment in .venv..."
    if [ ! -d ".venv" ]; then
        log_info "Creating new virtual environment..."
        "$PYTHON_BIN" -m venv .venv
        log_success "Created .venv directory."
    else
        log_info "Existing .venv directory detected."
    fi

    # Activate virtual environment
    if [ -f ".venv/bin/activate" ]; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
    elif [ -f ".venv/Scripts/activate" ]; then
        # shellcheck disable=SC1091
        source .venv/Scripts/activate
    else
        log_error "Could not find virtualenv activation script at .venv/bin/activate."
        exit 1
    fi
    log_success "Virtual environment activated: $(which python)"

    # Upgrade pip and install pinned requirements
    log_info "Installing dependencies from requirements.txt..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    log_success "All dependencies successfully installed."
}

# ------------------------------------------------------------------------------
# 3. Provision Environment Configuration (.env)
# ------------------------------------------------------------------------------
setup_env() {
    log_info "Checking environment configuration file (.env)..."
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env from .env.example template."
        else
            echo "ENV=development" > .env
            echo "PORT=8080" >> .env
            echo "DEMO_MODE=true" >> .env
            echo "GEMINI_API_KEY=" >> .env
            echo "GOOGLE_CLOUD_PROJECT=your-gcp-project-id" >> .env
            echo "ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080" >> .env
            echo "WEBHOOK_SIGNING_SECRET=pulse_dev_webhook_signing_secret" >> .env
            log_success "Generated default .env file."
        fi
        log_warning "Sandbox Demo Mode is enabled by default (DEMO_MODE=true)."
        log_warning "To enable live Gemini API inference locally, set GEMINI_API_KEY in .env."
    else
        log_success "Existing .env configuration detected."
    fi
}

# ------------------------------------------------------------------------------
# 4. Pre-Flight Verification & Test Execution
# ------------------------------------------------------------------------------
run_tests() {
    log_info "Executing 4-tier hermetic test suite verification..."
    if [ -f "run_tests.py" ]; then
        python run_tests.py
    else
        pytest -v tests/
    fi
    log_success "All pre-flight test suites completed."
}

# ------------------------------------------------------------------------------
# 5. Launch FastAPI Application Server
# ------------------------------------------------------------------------------
start_server() {
    local PORT_TO_USE="${PORT:-8080}"
    echo ""
    echo -e "${GREEN}======================================================================${NC}"
    echo -e "${BOLD}🎉 WorkplacePulse is ready! Launching Uvicorn server...${NC}"
    echo -e "   - ${CYAN}Command Center Dashboard:${NC} http://localhost:${PORT_TO_USE}"
    echo -e "   - ${CYAN}Interactive OpenAPI Docs:${NC}  http://localhost:${PORT_TO_USE}/docs"
    echo -e "   - ${CYAN}Liveness Health Check:${NC}     http://localhost:${PORT_TO_USE}/api/health"
    echo -e "${GREEN}======================================================================${NC}"
    echo ""
    
    exec uvicorn main:app --host 0.0.0.0 --port "${PORT_TO_USE}" --reload
}

# ------------------------------------------------------------------------------
# Main Entrypoint & Command-Line Option Dispatcher
# ------------------------------------------------------------------------------
main() {
    banner

    # CLI flag handling
    case "${1:-}" in
        --test|-t)
            check_python
            setup_venv
            setup_env
            run_tests
            log_success "Test verification passed. Exiting (--test flag specified)."
            exit 0
            ;;
        --docker|-d)
            setup_env
            log_info "Spinning up services using Docker Compose..."
            docker compose up --build
            exit 0
            ;;
        --dev)
            check_python
            setup_venv
            setup_env
            start_server
            exit 0
            ;;
        --help|-h)
            echo "WorkplacePulse Automated Setup & Runner"
            echo ""
            echo "Usage: ./setup.sh [OPTION]"
            echo ""
            echo "Options:"
            echo "  (no args)     Full automated setup: check python, venv, dependencies, .env, run pre-flight tests, and start server"
            echo "  --dev         Start the development server without re-running tests"
            echo "  --test, -t    Setup environment, run full 4-tier hermetic test suite, and exit"
            echo "  --docker, -d  Provision .env and launch with Docker Compose"
            echo "  --help, -h    Display this help message"
            echo ""
            echo "Environment Overrides:"
            echo "  PORT=8081 ./setup.sh        Bind to custom port"
            echo "  DEMO_MODE=false ./setup.sh  Run in production auth mode"
            exit 0
            ;;
        "")
            # Default automated setup flow
            check_python
            setup_venv
            setup_env
            run_tests
            start_server
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Run './setup.sh --help' for available options."
            exit 1
            ;;
    esac
}

main "$@"
