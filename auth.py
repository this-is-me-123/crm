# auth.py
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import HTTPException, status, Request, Form
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from supabase import create_client, Client

# Env vars
SUPABASE_URL        = os.environ["SUPABASE_URL"]
SUPABASE_KEY        = os.environ["SUPABASE_KEY"]
SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    session = result.session
    if session and session.access_token:
        response = RedirectResponse("/dashboard", status_code=303)
        # Secure, HttpOnly cookie
        response.set_cookie(
            "access_token",
            session.access_token,
            httponly=True,
            secure=True,       # only over HTTPS
            samesite="lax",
            max_age=session.expires_in
        )
        print("Cookie set:", session.access_token[:10], "...")  # debug
        return response
    else:
        print("Login failed for:", email, result)  # debug
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

def verify_jwt(request: Request):
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
