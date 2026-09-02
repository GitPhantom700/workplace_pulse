"""
Test Configuration and Fixtures for WorkplacePulse Test Suite.
Hermetic mocks for Google Cloud Firestore, Secret Manager, Google GenAI SDK, and Firebase Auth.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set hermetic default environment variables for testing
os.environ.setdefault("GEMINI_API_KEY", "test-mock-gemini-api-key-12345")
os.environ.setdefault("DEMO_MODE", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-pulse-project")
os.environ.setdefault("ENV", "test")

# ---------------------------------------------------------
# Mock Classes for Hermetic Testing
# ---------------------------------------------------------

class MockSecretPayload:
    def __init__(self, secret_text: str = "test-secret-value-from-sm"):
        self.data = secret_text.encode("utf-8")


class MockSecretVersionResponse:
    def __init__(self, secret_text: str = "test-secret-value-from-sm"):
        self.payload = MockSecretPayload(secret_text)


class MockSecretManagerClient:
    def __init__(self, default_secret: str = "test-secret-value-from-sm"):
        self.default_secret = default_secret
        self.access_secret_version_mock = MagicMock(
            side_effect=lambda request: MockSecretVersionResponse(self.default_secret)
        )

    def access_secret_version(self, request: Dict[str, Any]):
        return self.access_secret_version_mock(request)


class MockDocumentReference:
    def __init__(self, doc_id: str = "doc-test-12345"):
        self.id = doc_id
        self.saved_data = None
        self.set = MagicMock(side_effect=self._set)

    def _set(self, data: Dict[str, Any]):
        self.saved_data = data
        return True


class MockCollectionReference:
    def __init__(self, name: str):
        self.name = name
        self._docs = {}

    def document(self, doc_id: Optional[str] = None):
        if not doc_id:
            import uuid
            doc_id = f"doc-{uuid.uuid4().hex[:8]}"
        if doc_id not in self._docs:
            self._docs[doc_id] = MockDocumentReference(doc_id)
        return self._docs[doc_id]


class MockUserDocumentReference:
    def __init__(self, user_id: str):
        self.id = user_id
        self._collections = {}

    def collection(self, collection_name: str):
        if collection_name not in self._collections:
            self._collections[collection_name] = MockCollectionReference(collection_name)
        return self._collections[collection_name]


class MockFirestoreClient:
    SERVER_TIMESTAMP = "__SERVER_TIMESTAMP__"

    def __init__(self):
        self._users = {}

    def collection(self, name: str):
        if name == "users":
            mock_col = MagicMock()
            mock_col.document = lambda user_id: self._get_or_create_user(user_id)
            return mock_col
        return MockCollectionReference(name)

    def _get_or_create_user(self, user_id: str):
        if user_id not in self._users:
            self._users[user_id] = MockUserDocumentReference(user_id)
        return self._users[user_id]


class MockGenAIResponse:
    def __init__(self, text: str = "Synthetic AI forecast and analysis report."):
        self.text = text


class MockChatSession:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.send_message = MagicMock(
            return_value=MockGenAIResponse(f"Response from {model_name}")
        )


class MockGenerativeModel:
    def __init__(self, model_name: str, system_instruction: Optional[str] = None, generation_config: Any = None):
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.generation_config = generation_config
        self.chat_session = MockChatSession(model_name)

    def start_chat(self, history: Optional[List[Any]] = None):
        return self.chat_session


# ---------------------------------------------------------
# Test Client Harness
# ---------------------------------------------------------

class TestResponse:
    def __init__(self, status_code: int, json_data: Any = None, text: str = "", headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text if text else (json.dumps(json_data) if json_data is not None else "")
        self.headers = headers or {}

    def json(self):
        if self._json_data is not None:
            return self._json_data
        if self.text:
            return json.loads(self.text)
        return {}


# ---------------------------------------------------------
# Pytest Fixtures
# ---------------------------------------------------------

try:
    import pytest

    @pytest.fixture(autouse=True)
    def reset_environment(monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-mock-gemini-api-key-12345")
        monkeypatch.setenv("DEMO_MODE", "true")
        monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-pulse-project")
        monkeypatch.setenv("ENV", "test")

    @pytest.fixture
    def mock_secret_manager():
        client = MockSecretManagerClient()
        with patch("google.cloud.secretmanager.SecretManagerServiceClient", return_value=client):
            yield client

    @pytest.fixture
    def mock_firestore():
        client = MockFirestoreClient()
        with patch("google.cloud.firestore.Client", return_value=client):
            with patch("database.db", client):
                yield client

    @pytest.fixture
    def mock_genai():
        with patch("google.generativeai.GenerativeModel", side_effect=lambda model_name, **kwargs: MockGenerativeModel(model_name, **kwargs)) as m:
            yield m

    @pytest.fixture
    def demo_auth_headers():
        return {"Authorization": "Bearer demo-engineer-123"}

    @pytest.fixture
    def invalid_auth_headers():
        return {"Authorization": "Bearer invalid-token-999"}

    @pytest.fixture
    def client():
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

except ImportError:
    pass
