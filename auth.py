# auth.py
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import HTTPException, status, Request, Form
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from supabase import create_client, Client

# Environment variables
SUPABASE_URL        = os.environ["SUPABASE_URL"]
SUPABASE_KEY        = os.environ["SUPABASE_KEY"]
SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    """
    POST /login form handler.
    Signs in via Supabase, sets an HttpOnly cookie, and redirects to /dashboard.
    """
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    session = result.session
    if session and session.access_token:
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(
            "access_token",
            session.access_token,
            httponly=True,
            samesite="lax",
            max_age=session.expires_in
        )
        return response
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

def verify_jwt(request: Request):
    """
    Dependency to protect routes.
    Reads 'access_token' cookie, decodes JWT, or raises 401.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
