# auth.py
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import HTTPException, status, Request, Form
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from supabase import create_client, Client

# Environment
SUPABASE_URL        = os.environ["SUPABASE_URL"]
SUPABASE_KEY        = os.environ["SUPABASE_KEY"]
SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    """
    Handle POST /login: sign in via Supabase and set JWT cookie.
    """
    # 1) Attempt sign-in
    resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
    print("DEBUG: Supabase sign-in response:", resp)

    # 2) Extract data/error
    data  = resp.get("data")  if isinstance(resp, dict) else getattr(resp, "data", None)
    error = resp.get("error") if isinstance(resp, dict) else getattr(resp, "error", None)

    if error:
        print("ERROR: Supabase returned error:", error)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    session = data.get("session") if data else None
    token   = session.get("access_token") if session else None

    if token:
        # 3) Set cookie and redirect
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(
            "access_token", token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=session.get("expires_in", 3600)
        )
        print("DEBUG: Cookie set:", token[:10], "…")
        return response

    print("ERROR: No session/token in sign-in response")
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


def verify_jwt(request: Request):
    """
    Dependency for protected routes: read and verify JWT from cookie.
    """
    token = request.cookies.get("access_token")
    print("DEBUG: Incoming cookie token:", token)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        print("DEBUG: JWT payload:", payload)
        return payload
    except JWTError as e:
        print("ERROR: JWT decode error:", str(e))
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
