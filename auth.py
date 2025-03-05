from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Cognito Settings (Directly from .env)
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET")
COGNITO_REDIRECT_URI = os.getenv("COGNITO_REDIRECT_URI")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", os.urandom(24))  # Default to random key if not set

# Add OAuth
oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=COGNITO_CLIENT_ID,
    client_secret=COGNITO_CLIENT_SECRET,
    server_metadata_url=f"{COGNITO_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

def add_auth_middleware(app):
    """Add session middleware to FastAPI app"""
    app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

@router.get("/login")
async def login(request: Request):
    """Redirect user to Cognito login page"""
    return await oauth.oidc.authorize_redirect(request, COGNITO_REDIRECT_URI)

@router.get("/authorize")
async def authorize(request: Request):
    """Handle Cognito login callback"""
    token = await oauth.oidc.authorize_access_token(request)
    user = token.get("userinfo")
    request.session["user"] = user
    return RedirectResponse(url="/")

@router.get("/logout")
async def logout(request: Request):
    """Clear session and redirect to home"""
    request.session.pop("user", None)
    return RedirectResponse(url="/")
