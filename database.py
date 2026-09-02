"""
WorkplacePulse - Firestore Database Integration
Handles secure persistence of AI transactions, webhooks, and incident runbooks with strict multi-tenant isolation.
"""

import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from google.cloud import firestore

logger = logging.getLogger("WorkplacePulse.Database")

# Task 31: Integrate google-cloud-firestore SDK
try:
    # Initialize Firestore client using Application Default Credentials (ADC)
    db = firestore.Client()
except Exception as e:
    logger.warning(f"Firestore initialization deferred (Running in Demo/Offline Mode): {e}")
    db = None

# In-memory storage for offline / sandbox / demo evaluation ensuring 100% tenant isolation
_DEMO_STORE: Dict[str, Dict[str, Dict[str, Any]]] = {
    "webhooks": {},       # {user_id: {webhook_id: doc}}
    "webhook_logs": {     # {user_id: {delivery_id: doc}}
        "demo_engineer_chandraprakash": {
            "del_init_01": {
                "delivery_id": "del_init_01",
                "webhook_id": "wh_discord_secops",
                "webhook_name": "Discord SecOps Bot",
                "service_type": "discord",
                "event_type": "runbook.executed",
                "status_code": 200,
                "status": "delivered",
                "duration_ms": 14.8,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "del_init_02": {
                "delivery_id": "del_init_02",
                "webhook_id": "wh_slack_ops",
                "webhook_name": "Slack IT Operations",
                "service_type": "slack",
                "event_type": "alert.critical",
                "status_code": 200,
                "status": "delivered",
                "duration_ms": 12.2,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    },
    "runbook_logs": {},   # {user_id: {execution_id: doc}}
    "forecast_logs": {}   # {user_id: {log_id: doc}}
}


# ---------------------------------------------------------
# 1. Forecast Logs (Task 32)
# ---------------------------------------------------------

def save_forecast_log(user_id: str, user_email: str, scenario_id: str, user_prompt: str, ai_response: str) -> bool:
    """
    Task 32: Persists the AI transaction to Firestore for auditing and runbook history.
    Enforces strict data placement under /users/{user_id}/ to align with firestore.rules.
    """
    if not db:
        if user_id not in _DEMO_STORE["forecast_logs"]:
            _DEMO_STORE["forecast_logs"][user_id] = {}
        log_id = f"log_{datetime.now(timezone.utc).timestamp()}"
        _DEMO_STORE["forecast_logs"][user_id][log_id] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_email": user_email,
            "scenario_id": scenario_id,
            "prompt_snippet": user_prompt[:1000],
            "ai_response": ai_response,
            "environment": "demo_sandbox"
        }
        logger.info(f"Demo Mode: Simulated saving AI forecast for user {user_id} to Firestore.")
        return False
        
    try:
        doc_ref = db.collection('users').document(user_id).collection('forecast_logs').document()
        payload = {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "user_email": user_email,
            "scenario_id": scenario_id,
            "prompt_snippet": user_prompt[:1000], 
            "ai_response": ai_response,
            "environment": "production"
        }
        doc_ref.set(payload)
        logger.info(f"Successfully persisted isolated transaction {doc_ref.id} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Firestore Persistence Error in save_forecast_log: {e}")
        return False


# ---------------------------------------------------------
# 2. Webhook Configurations (/users/{userId}/webhooks/{id})
# ---------------------------------------------------------

def save_webhook_config(user_id: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves or updates a webhook destination in the user's isolated sandbox:
    /users/{user_id}/webhooks/{webhook_id}
    """
    webhook_id = webhook_data.get("webhook_id")
    if not webhook_id:
        import uuid
        webhook_id = f"wh_{uuid.uuid4().hex[:12]}"
        webhook_data["webhook_id"] = webhook_id

    webhook_data["user_id"] = user_id
    if "created_at" not in webhook_data:
        webhook_data["created_at"] = datetime.now(timezone.utc).isoformat()

    if not db:
        if user_id not in _DEMO_STORE["webhooks"]:
            _DEMO_STORE["webhooks"][user_id] = {}
        _DEMO_STORE["webhooks"][user_id][webhook_id] = dict(webhook_data)
        logger.info(f"Demo Mode: Saved webhook {webhook_id} for user {user_id}")
        return webhook_data

    try:
        doc_ref = db.collection('users').document(user_id).collection('webhooks').document(webhook_id)
        doc_ref.set(webhook_data)
        logger.info(f"Firestore: Saved webhook {webhook_id} for user {user_id}")
        return webhook_data
    except Exception as e:
        logger.error(f"Firestore save_webhook_config error: {e}")
        # Fallback to demo store so caller does not crash
        if user_id not in _DEMO_STORE["webhooks"]:
            _DEMO_STORE["webhooks"][user_id] = {}
        _DEMO_STORE["webhooks"][user_id][webhook_id] = dict(webhook_data)
        return webhook_data


def get_user_webhooks(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all configured webhooks belonging exclusively to the authenticated user.
    """
    if not db:
        user_hooks = _DEMO_STORE["webhooks"].get(user_id, {})
        return list(user_hooks.values())

    try:
        col_ref = db.collection('users').document(user_id).collection('webhooks')
        docs = col_ref.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            data["webhook_id"] = doc.id
            results.append(data)
        return results
    except Exception as e:
        logger.error(f"Firestore get_user_webhooks error: {e}")
        user_hooks = _DEMO_STORE["webhooks"].get(user_id, {})
        return list(user_hooks.values())


def get_webhook_by_id(user_id: str, webhook_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single webhook configuration ensuring tenant isolation.
    """
    if not db:
        return _DEMO_STORE["webhooks"].get(user_id, {}).get(webhook_id)

    try:
        doc_ref = db.collection('users').document(user_id).collection('webhooks').document(webhook_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["webhook_id"] = doc.id
            return data
        return None
    except Exception as e:
        logger.error(f"Firestore get_webhook_by_id error: {e}")
        return _DEMO_STORE["webhooks"].get(user_id, {}).get(webhook_id)


def delete_user_webhook(user_id: str, webhook_id: str) -> bool:
    """
    Deletes a webhook configuration from the user's isolated sandbox.
    """
    deleted = False
    if not db:
        if user_id in _DEMO_STORE["webhooks"] and webhook_id in _DEMO_STORE["webhooks"][user_id]:
            del _DEMO_STORE["webhooks"][user_id][webhook_id]
            deleted = True
            logger.info(f"Demo Mode: Deleted webhook {webhook_id} for user {user_id}")
        return deleted

    try:
        doc_ref = db.collection('users').document(user_id).collection('webhooks').document(webhook_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            deleted = True
            logger.info(f"Firestore: Deleted webhook {webhook_id} for user {user_id}")
        return deleted
    except Exception as e:
        logger.error(f"Firestore delete_user_webhook error: {e}")
        if user_id in _DEMO_STORE["webhooks"] and webhook_id in _DEMO_STORE["webhooks"][user_id]:
            del _DEMO_STORE["webhooks"][user_id][webhook_id]
            return True
        return False


# ---------------------------------------------------------
# 3. Webhook Delivery Logs (/users/{userId}/webhook_logs/{id})
# ---------------------------------------------------------

def save_webhook_delivery_log(user_id: str, log_data: Dict[str, Any]) -> bool:
    """
    Saves an immutable webhook delivery audit log under /users/{user_id}/webhook_logs/{delivery_id}
    """
    delivery_id = log_data.get("delivery_id")
    if not delivery_id:
        import uuid
        delivery_id = str(uuid.uuid4())
        log_data["delivery_id"] = delivery_id

    log_data["user_id"] = user_id
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.now(timezone.utc).isoformat()

    if not db:
        if user_id not in _DEMO_STORE["webhook_logs"]:
            _DEMO_STORE["webhook_logs"][user_id] = {}
        _DEMO_STORE["webhook_logs"][user_id][delivery_id] = dict(log_data)
        logger.info(f"Demo Mode: Saved delivery log {delivery_id} for user {user_id}")
        return True

    try:
        doc_ref = db.collection('users').document(user_id).collection('webhook_logs').document(delivery_id)
        doc_ref.set(log_data)
        logger.info(f"Firestore: Saved delivery log {delivery_id} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Firestore save_webhook_delivery_log error: {e}")
        if user_id not in _DEMO_STORE["webhook_logs"]:
            _DEMO_STORE["webhook_logs"][user_id] = {}
        _DEMO_STORE["webhook_logs"][user_id][delivery_id] = dict(log_data)
        return True


def get_user_webhook_logs(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetches the delivery logs for a user ordered by timestamp descending.
    """
    if not db:
        user_logs = list(_DEMO_STORE["webhook_logs"].get(user_id, {}).values())
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_logs[:limit]

    try:
        col_ref = db.collection('users').document(user_id).collection('webhook_logs')
        query = col_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        results = [doc.to_dict() for doc in docs]
        return results
    except Exception as e:
        logger.error(f"Firestore get_user_webhook_logs error: {e}")
        user_logs = list(_DEMO_STORE["webhook_logs"].get(user_id, {}).values())
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_logs[:limit]


# ---------------------------------------------------------
# 4. Runbook Execution Logs (/users/{userId}/runbook_logs/{id})
# ---------------------------------------------------------

def save_runbook_execution_log(user_id: str, log_data: Dict[str, Any]) -> bool:
    """
    Saves an immutable incident runbook execution log under /users/{user_id}/runbook_logs/{execution_id}
    """
    execution_id = log_data.get("execution_id")
    if not execution_id:
        import uuid
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        log_data["execution_id"] = execution_id

    log_data["user_id"] = user_id
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.now(timezone.utc).isoformat()

    if not db:
        if user_id not in _DEMO_STORE["runbook_logs"]:
            _DEMO_STORE["runbook_logs"][user_id] = {}
        _DEMO_STORE["runbook_logs"][user_id][execution_id] = dict(log_data)
        logger.info(f"Demo Mode: Saved runbook execution log {execution_id} for user {user_id}")
        return True

    try:
        doc_ref = db.collection('users').document(user_id).collection('runbook_logs').document(execution_id)
        doc_ref.set(log_data)
        logger.info(f"Firestore: Saved runbook log {execution_id} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Firestore save_runbook_execution_log error: {e}")
        if user_id not in _DEMO_STORE["runbook_logs"]:
            _DEMO_STORE["runbook_logs"][user_id] = {}
        _DEMO_STORE["runbook_logs"][user_id][execution_id] = dict(log_data)
        return True


def get_user_runbook_logs(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieves runbook execution logs for the authenticated user.
    """
    if not db:
        user_logs = list(_DEMO_STORE["runbook_logs"].get(user_id, {}).values())
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_logs[:limit]

    try:
        col_ref = db.collection('users').document(user_id).collection('runbook_logs')
        query = col_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        docs = query.stream()
        results = [doc.to_dict() for doc in docs]
        return results
    except Exception as e:
        logger.error(f"Firestore get_user_runbook_logs error: {e}")
        user_logs = list(_DEMO_STORE["runbook_logs"].get(user_id, {}).values())
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_logs[:limit]
