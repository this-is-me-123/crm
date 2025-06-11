from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from sqlmodel import Session, select
from models import Subscriber, MessageLog
from db import get_session, init_db
from datetime import datetime
from auth import login
from email_utils import send_email
from sms_utils import send_sms  # Only if using SMS, else remove
from jose import jwt, JWTError

import os

app = FastAPI()
init_db()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "YOUR_SUPABASE_JWT_SECRET")

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def process_login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        jwt_token, user = login(email, password)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("access_token", jwt_token, httponly=True)
        return response
    except Exception:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid login"})

@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response

@app.get("/")
def dashboard(request: Request, session: Session = Depends(get_session), user=Depends(get_current_user)):
    subs = session.exec(select(Subscriber)).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "subs": subs})

@app.get("/subscribers")
def list_subscribers(request: Request, session: Session = Depends(get_session), user=Depends(get_current_user)):
    subs = session.exec(select(Subscriber)).all()
    return templates.TemplateResponse("subscribers.html", {"request": request, "subs": subs})

@app.get("/subscriber/add")
def add_subscriber_form(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("add_subscriber.html", {"request": request})

@app.post("/subscriber/add")
def add_subscriber(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    tier: str = Form("free"),
    tags: str = Form(""),
    phone: str = Form(None),
    session: Session = Depends(get_session),
    user=Depends(get_current_user)
):
    sub = Subscriber(username=username, email=email, tier=tier, tags=tags)
    if phone:
        sub.phone = phone
    session.add(sub)
    session.commit()
    return RedirectResponse("/subscribers", status_code=303)

@app.get("/subscriber/{sub_id}")
def subscriber_detail(sub_id: int, request: Request, session: Session = Depends(get_session), user=Depends(get_current_user)):
    sub = session.get(Subscriber, sub_id)
    logs = session.exec(select(MessageLog).where(MessageLog.subscriber_id == sub_id)).all()
    return templates.TemplateResponse("subscriber_detail.html", {"request": request, "sub": sub, "logs": logs})

@app.get("/subscriber/{sub_id}/message")
def send_message_form(sub_id: int, request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("send_message.html", {"request": request, "sub_id": sub_id})

@app.post("/subscriber/{sub_id}/message")
def send_message(
    sub_id: int,
    message: str = Form(...),
    session: Session = Depends(get_session),
    user=Depends(get_current_user)
):
    log = MessageLog(subscriber_id=sub_id, message=message)
    session.add(log)
    session.commit()
    sub = session.get(Subscriber, sub_id)
    if sub and sub.email:
        try:
            send_email(sub.email, "Message from CRM", message)
        except Exception as e:
            print("Email send failed:", e)
    if sub and hasattr(sub, "phone") and sub.phone:
        try:
            send_sms(sub.phone, message)
        except Exception as e:
            print("SMS send failed:", e)
    return RedirectResponse(f"/subscriber/{sub_id}", status_code=303)

@app.get("/segments/{tag}")
def segment_by_tag(tag: str, request: Request, session: Session = Depends(get_session), user=Depends(get_current_user)):
    subs = session.exec(select(Subscriber).where(Subscriber.tags.contains(tag))).all()
    return templates.TemplateResponse("subscribers.html", {"request": request, "subs": subs})
