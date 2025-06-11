from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://YOUR-PROJECT.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "YOUR_SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def login(email: str, password: str):
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if response.user is None:
        raise Exception("Login failed")
    jwt_token = response.session.access_token  # This is the JWT for future requests
    return jwt_token, response.user
