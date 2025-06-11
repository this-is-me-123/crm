from fastapi import Depends, HTTPException, status, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from starlette.responses import RedirectResponse
import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bearer_scheme = HTTPBearer()

def verify_jwt(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token.credentials, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    session = result.session
    if session and session.access_token:
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("access_token", session.access_token)
        return response
    else:
        return {"error": "Invalid login"}
