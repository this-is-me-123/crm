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
    Handle POST /login: sign in with Supabase and set JWT cookie.
    """
    resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
    # Extract the session object
    data = getattr(resp, "data", resp.get("data", {}))
    session = data.get("session")
    if session and session.get("access_token"):
        token = session["access_token"]
        # Build response
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=session.get("expires_in", 3600)
        )
        print("Cookie set:", token[:10], "...")  # debug
        return response

    # Failed login
    print("Login failed response:", resp)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

def verify_jwt(request: Request):
    """
    Dependency: reads JWT from cookie and validates it.
    """
    token = request.cookies.get("access_token")
    print("Incoming cookie token:", token)  # debug
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        print("JWT payload:", payload)  # debug
        return payload
    except JWTError as e:
        print("JWT decode error:", str(e))  # debug
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
