import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Lazy-loaded imports for GCP to speed up local testing if not used
from google.cloud import secretmanager
from google.api_core.exceptions import GoogleAPIError
import firebase_admin
from firebase_admin import credentials, auth

# Task 12: Configure Local Fallback for GEMINI_API_KEY
load_dotenv() 

# Task 13: Initialize Firebase Admin SDK Identity Verifier
# Cloud Run provides default ADC. Locally, requires GOOGLE_APPLICATION_CREDENTIALS.
try:
    if not firebase_admin._apps:
        # Initializing without explicit creds forces Firebase to use ADC automatically
        # Explicitly setting projectId to workplacepulse-dev to match the frontend's tokens
        firebase_admin.initialize_app(options={'projectId': 'workplacepulse-dev'})
except Exception as e:
    logging.warning(f"Firebase Admin SDK initialization deferred or failed: {e}")

http_bearer = HTTPBearer()

# Task 14 & 15: FastAPI Token Verification Middleware & Error Escalation
async def verify_firebase_token(creds: HTTPAuthorizationCredentials = Depends(http_bearer)) -> dict:
    """
    Extracts and verifies the Firebase ID token from the Authorization header.
    Raises 401 Unauthorized if invalid, expired, or malformed.
    Returns the decoded token payload (containing 'uid', 'email', etc.)
    """
    token = creds.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token missing from request"
        )
    
    # Support instant local demo/sandbox mode without failing if Firebase is unconfigured
    if token.startswith("demo-"):
        demo_allowed = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
        if demo_allowed:
            return {
                "uid": "demo_engineer_chandraprakash",
                "email": "demo.lead@floqast.com",
                "name": "Chandraprakash Hingal",
                "role": "IT Support Lead"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Demo mode authentication is disabled. Provide a valid Firebase ID token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logging.error(f"Firebase Auth Verification Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Authentication Token. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Task 11: Implement Google Cloud Secret Manager Client API
def get_gemini_api_key() -> str:
    """
    Fetches the Gemini API key securely with a zero-hardcoding architecture.
    1. Checks local environment (.env fallback for local sandbox).
    2. If missing, attempts production Cloud Secret Manager via ADC.
    """
    # 1. Local Fallback
    local_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if local_key:
        return local_key
    
    # 2. Production Secret Manager Retrieval
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    if not project_id:
        try:
            import google.auth
            _, project_id = google.auth.default()
        except Exception as e:
            if os.environ.get("DEMO_MODE", "false").lower() == "true":
                return None
            logging.error(f"Failed to infer GCP Project ID: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security Error: Could not determine GCP Project ID for Secret Manager resolution."
            )
            
    if not project_id:
        if os.environ.get("DEMO_MODE", "false").lower() == "true":
            return None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security Error: Could not determine GCP Project ID for Secret Manager resolution."
        )

    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/GEMINI_API_KEY/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})
        return response.payload.data.decode("UTF-8")
    except GoogleAPIError as e:
        logging.error(f"Google Cloud Secret Manager API Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Security Exception: Failed to retrieve API key from Secret Manager: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Unexpected error retrieving secret: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error while resolving security credentials: {str(e)}"
        )
