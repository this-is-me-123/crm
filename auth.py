# auth.py
import os
from fastapi import HTTPException, status, Request, Form
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from supabase import create_client, Client

# Load env vars
SUPABASE_URL       = os.environ["SUPABASE_URL"]
SUPABASE_KEY       = os.environ["SUPABASE_KEY"]
SUPABASE_JWT_SECRET= os.environ["SUPABASE_JWT_SECRET"]

# Init Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    """
    Called by POST /login: attempts email/password sign-in,
    sets a cookie with the access_token, then redirects.
    """
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    session = result.session
    if session and session.access_token:
        response = RedirectResponse("/dashboard", status_code=303)
        # HttpOnly cookie so JS can't read it, SameSite lax for cross-site redirects
        response.set_cookie(
            "access_token", session.access_token,
            httponly=True, samesite="lax", max_age=session.expires_in
        )
        return response
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

def verify_jwt_cookie(request: Request):
    """
    FastAPI dependency: reads the 'access_token' cookie,
    decodes it, and returns the payload or 401.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
