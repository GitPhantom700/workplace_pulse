#!/usr/bin/env python3
"""
WorkplacePulse Hermetic Test Runner
Executes the full 4-Tier test suite with zero external cloud dependencies.
Provides detailed test execution traces, fixture injection, and status reporting.
"""

import sys
import os
import time
import inspect
import asyncio
import traceback
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set test environment
os.environ["GEMINI_API_KEY"] = "test-mock-gemini-api-key-12345"
os.environ["DEMO_MODE"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-pulse-project"
os.environ["ENV"] = "test"

# Import conftest to initialize mocks and fixtures
import tests.conftest as conftest

# Test modules in execution order (Tiers 1 to 4 + Adversarial Suites + Standout Feature)
TEST_MODULES = [
    ("Tier 1: Data Engine Unit Tests", "tests.test_data_engine"),
    ("Tier 1: Schema & Models Validation Tests", "tests.test_models"),
    ("Tier 1 & 3: Security & Auth Unit Tests", "tests.test_security_unit"),
    ("Tier 1 & 4: AI Forecasting & Fallback Ladder Tests", "tests.test_ai_service"),
    ("Tier 2: Dynamic REST API Endpoints Tests", "tests.test_api_endpoints"),
    ("Standout Feature: Webhook & Runbook Engine Tests", "tests.test_runbooks_webhooks"),
    ("Tier 3: Security Compliance & Rules Tests", "tests.test_security_compliance"),
    ("Tier 4: Cloud Run Container & Resilience Tests", "tests.test_cloud_run_resilience"),
    ("Adversarial Dynamic & Auth Stress Tests", "tests.test_adversarial_dynamic"),
    ("Adversarial AI Service Resilience Tests", "tests.test_adversarial_ai_resilience"),
    ("Challenger 1: Adversarial Security & Webhook Verification", "tests.test_adversarial_security_and_webhooks"),
    ("Challenger 2: Multi-Tenant Isolation & Edge Cases", "tests.test_adversarial_multitenancy_and_edgecases"),
]


class MonkeyPatchHelper:
    """Helper mimicking pytest's monkeypatch fixture."""
    def __init__(self):
        self._orig_env = dict(os.environ)

    def setenv(self, key: str, value: str):
        os.environ[key] = value

    def delenv(self, key: str, raising: bool = False):
        if key in os.environ:
            del os.environ[key]
        elif raising:
            raise KeyError(key)

    def undo(self):
        os.environ.clear()
        os.environ.update(self._orig_env)


def run_single_test(test_fn, fn_name: str):
    """Executes a single test function with fixture resolution."""
    mp = MonkeyPatchHelper()
    sig = inspect.signature(test_fn)
    kwargs = {}

    for param in sig.parameters.values():
        if param.name == "monkeypatch":
            kwargs["monkeypatch"] = mp
        elif param.name == "client":
            from fastapi.testclient import TestClient
            from main import app
            kwargs["client"] = TestClient(app)
        elif param.name == "demo_auth_headers":
            kwargs["demo_auth_headers"] = {"Authorization": "Bearer demo-engineer-123"}
        elif param.name == "invalid_auth_headers":
            kwargs["invalid_auth_headers"] = {"Authorization": "Bearer invalid-token-999"}
        elif param.name == "mock_firestore":
            kwargs["mock_firestore"] = conftest.MockFirestoreClient()
        elif param.name == "mock_genai":
            kwargs["mock_genai"] = conftest.MockGenerativeModel
        elif param.name == "mock_secret_manager":
            kwargs["mock_secret_manager"] = conftest.MockSecretManagerClient()

    try:
        if inspect.iscoroutinefunction(test_fn):
            asyncio.run(test_fn(**kwargs))
        else:
            test_fn(**kwargs)
        return True, None
    except Exception as e:
        return False, traceback.format_exc()
    finally:
        mp.undo()


def run_all_tests():
    import unittest
    print("=" * 80)
    print("   WORKPLACEPULSE 4-TIER HERMETIC E2E TEST SUITE RUNNER")
    print("=" * 80)
    print(f"Project Directory: {PROJECT_ROOT}")
    print(f"Python Version   : {sys.version.split()[0]}")
    print(f"Timestamp        : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 80)
    print()

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    start_time = time.time()

    for tier_title, mod_name in TEST_MODULES:
        print(f"\n--- {tier_title} ({mod_name}) ---")
        try:
            mod = __import__(mod_name, fromlist=["*"])
        except Exception as e:
            print(f"  [ERROR] Failed to import module {mod_name}: {e}")
            traceback.print_exc()
            total_failed += 1
            continue

        # 1. Run top-level test functions
        test_functions = [
            (name, getattr(mod, name))
            for name in dir(mod)
            if name.startswith("test_") and callable(getattr(mod, name))
        ]

        for fn_name, fn in test_functions:
            t0 = time.time()
            passed, err_msg = run_single_test(fn, fn_name)
            elapsed_ms = (time.time() - t0) * 1000

            if passed:
                total_passed += 1
                print(f"  PASSED  {fn_name:<60} ({elapsed_ms:5.1f}ms)")
            else:
                total_failed += 1
                print(f"  FAILED  {fn_name:<60} ({elapsed_ms:5.1f}ms)")
                print("-" * 60)
                print(err_msg)
                print("-" * 60)

        # 2. Run unittest.TestCase classes if present
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, type) and issubclass(attr, unittest.TestCase) and attr is not unittest.TestCase:
                suite = unittest.TestLoader().loadTestsFromTestCase(attr)
                for test_case in suite:
                    t0 = time.time()
                    result = unittest.TestResult()
                    test_case.run(result)
                    elapsed_ms = (time.time() - t0) * 1000
                    test_name = f"{attr.__name__}.{test_case._testMethodName}"
                    if result.wasSuccessful():
                        total_passed += 1
                        print(f"  PASSED  {test_name:<60} ({elapsed_ms:5.1f}ms)")
                    else:
                        total_failed += 1
                        print(f"  FAILED  {test_name:<60} ({elapsed_ms:5.1f}ms)")
                        print("-" * 60)
                        for failure in result.failures + result.errors:
                            print(failure[1])
                        print("-" * 60)

    total_time = time.time() - start_time
    total_tests = total_passed + total_failed + total_skipped

    print()
    print("=" * 80)
    print(f"TEST RUN RESULTS: {total_passed} Passed | {total_failed} Failed | {total_skipped} Skipped ({total_tests} Total)")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print("=" * 80)

    if total_failed == 0:
        print("\n>>> ALL TESTS PASSED SUCCESSFULLY (100% PASS RATE) <<<\n")
        return 0
    else:
        print(f"\n>>> TEST SUITE FAILED WITH {total_failed} FAILURES <<<\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
