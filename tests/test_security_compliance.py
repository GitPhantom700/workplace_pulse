"""
Tier 3 Security & Compliance Audits
Performs static analysis and verification for zero hardcoded secrets, Firestore security rules enforcement, and frontend DOM XSS sanitization.
"""

import os
import re
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_zero_hardcoded_secrets_across_repository():
    """
    Forensic Integrity Audit: Scans repository files for committed API keys, tokens, or credentials.
    Ensures zero hardcoded secrets exist.
    """
    # Patterns for real secrets (Google API keys, private keys, JWTs)
    secret_patterns = [
        re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),  # Google API Key format
        re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP)?\s?PRIVATE KEY-----"),
        re.compile(r"(?i)(?:api[_-]?key|secret[_-]?key|auth[_-]?token)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]")
    ]

    scanned_files = 0
    violations = []

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Exclude git, agent metadata, pycache, and virtualenv folders
        dirs[:] = [d for d in dirs if d not in [".git", ".agents", "__pycache__", ".venv", "venv", "node_modules"]]
        if any(ignored in root for ignored in [".git", ".agents", "__pycache__", ".venv", "venv"]):
            continue

        for file_name in files:
            if file_name.endswith((".py", ".md", ".html", ".js", ".json", ".rules", ".txt", "Dockerfile")):
                file_path = os.path.join(root, file_name)
                scanned_files += 1

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        for match in pattern.finditer(content):
                            match_str = match.group(0)
                            # Filter out mock strings and public Firebase Web Client config in frontend HTML
                            if "test" not in match_str.lower() and "dummy" not in match_str.lower() and "mock" not in match_str.lower():
                                if file_name.endswith(".html") and "firebaseConfig" in content:
                                    continue
                                violations.append(f"Secret detected in {file_name}: {match_str}")

    assert scanned_files > 5, "Fewer files scanned than expected in repository."
    assert len(violations) == 0, f"Hardcoded secrets detected: {violations}"


def test_firestore_rules_enforce_zero_trust_and_isolation():
    """
    Verify firestore.rules enforces zero-trust default deny and strict multi-tenant isolation.
    """
    rules_path = os.path.join(PROJECT_ROOT, "firestore.rules")
    assert os.path.exists(rules_path), "firestore.rules file missing from project root."

    with open(rules_path, "r", encoding="utf-8") as f:
        rules_content = f.read()

    # 1. Verify Rules Version 2
    assert "rules_version = '2'" in rules_content or 'rules_version = "2"' in rules_content

    # 2. Verify Root Default-Deny
    assert "match /{document=**}" in rules_content
    assert "allow read, write: if false;" in rules_content

    # 3. Verify Multi-Tenant User Isolation
    assert "match /users/{userId}" in rules_content
    assert "request.auth != null" in rules_content
    assert "request.auth.uid == userId" in rules_content

    # 4. Verify Immutable Audit Logs (no updates or deletes allowed)
    assert "allow update, delete: if false;" in rules_content


def test_dompurify_sanitization_in_frontend():
    """
    Verify frontend static/index.html includes DOMPurify and uses it to sanitize rendered content.
    """
    index_path = os.path.join(PROJECT_ROOT, "static", "index.html")
    assert os.path.exists(index_path), "static/index.html missing from static directory."

    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Verify DOMPurify library is loaded
    assert "purify" in html_content.lower() or "dompurify" in html_content.lower(), \
        "DOMPurify library script not imported in index.html"

    # Verify DOMPurify.sanitize is called
    assert "DOMPurify.sanitize" in html_content, \
        "DOMPurify.sanitize(...) is not invoked for rendering dynamic output in index.html"
