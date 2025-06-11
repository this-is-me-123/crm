# main.py
@app.get("/health")
def health():
    return {"status": "ok"}



from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from sqlmodel import Session, select

from models import Subscriber, MessageLog
from db import get_session, init_db
from auth import login_user, verify_jwt  # <-- updated import

# (Optional) if you’ve hooked up email/SMS utils:
# from email_utils import send_email
# from sms_utils import send_sms

app = FastAPI()
init_db()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Authentication Routes ---

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # calls the Supabase auth handler in auth.py
    return await login_user(request, email, password)


# --- Protected Admin Routes ---

@app.get("/")
def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    token=Depends(verify_jwt)        # <-- protect with JWT
):
    subs = session.exec(select(Subscriber)).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "subs": subs})


@app.get("/subscribers")
def list_subscribers(
    request: Request,
    session: Session = Depends(get_session),
    token=Depends(verify_jwt)
):
    subs = session.exec(select(Subscriber)).all()
    return templates.TemplateResponse("subscribers.html", {"request": request, "subs": subs})


@app.get("/subscriber/add")
def add_subscriber_form(
    request: Request,
    token=Depends(verify_jwt)
):
    return templates.TemplateResponse("add_subscriber.html", {"request": request})


@app.post("/subscriber/add")
def add_subscriber(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    tier: str = Form("free"),
    tags: str = Form(""),
    session: Session = Depends(get_session),
    token=Depends(verify_jwt)
):
    sub = Subscriber(username=username, email=email, tier=tier, tags=tags)
    session.add(sub)
    session.commit()
    return RedirectResponse("/subscribers", status_code=303)


@app.get("/subscriber/{sub_id}")
def subscriber_detail(
    sub_id: int,
    request: Request,
    session: Session = Depends(get_session),
    token=Depends(verify_jwt)
):
    sub = session.get(Subscriber, sub_id)
    logs = session.exec(select(MessageLog).where(MessageLog.subscriber_id == sub_id)).all()
    return templates.TemplateResponse("subscriber_detail.html", {"request": request, "sub": sub, "logs": logs})


@app.get("/subscriber/{sub_id}/message")
def send_message_form(
    sub_id: int,
    request: Request,
    token=Depends(verify_jwt)
):
    return templates.TemplateResponse("send_message.html", {"request": request, "sub_id": sub_id})


@app.post("/subscriber/{sub_id}/message")
def send_message(
    sub_id: int,
    message: str = Form(...),
    session: Session = Depends(get_session),
    token=Depends(verify_jwt)
):
    # log message
    log = MessageLog(subscriber_id=sub_id, message=message)
    session.add(log)
    session.commit()
    # -- Integrate real sending here, e.g.:
    # sub = session.get(Subscriber, sub_id)
    # send_email(sub.email, "New Message", message)
    # send_sms(sub.phone, message)
    return RedirectResponse(f"/subscriber/{sub_id}", status_code=303)


@app.get("/segments/{tag}")
def segment_by_tag(
    tag: str,
    request: Request,
    session: Session = Depends(get_session),
    token=Depends(verify_jwt)
):
    subs = session.exec(select(Subscriber).where(Subscriber.tags.contains(tag))).all()
    return templates.TemplateResponse("subscribers.html", {"request": request, "subs": subs})
