# Custom CRM Module – FastAPI + Supabase/Postgres

## Overview
A minimal, scalable CRM backend and web admin UI built on FastAPI and SQLModel, designed for integration with OnlyFans/AI management tools. Uses Postgres (Supabase) for persistence and can run locally or on cloud.

## Directory Structure
- `main.py` - FastAPI application and web routes
- `models.py` - Database models (Subscriber, MessageLog)
- `db.py` - DB connection setup (set `DATABASE_URL` for Supabase/Postgres)
- `templates/` - HTML templates (Jinja2)
- `static/` - CSS (optional)
- `README.md` - This file

## Setup Instructions

### 1. Requirements
- Python 3.10+
- [Supabase account](https://supabase.com/) (for production/Postgres) or SQLite for local dev
- `pip install fastapi uvicorn sqlmodel jinja2`

### 2. Database Configuration
- For **local dev:** (default) uses `crm.db` SQLite file.
- For **Supabase/Postgres:**  
  1. In Supabase, create a new project and find your DB credentials.
  2. Set the `DATABASE_URL` env variable in the format:
     ```
     postgresql://username:password@host:port/database
     ```
     Example (don't use these exact credentials!):
     ```
     export DATABASE_URL="postgresql://postgres:password@db.abcd.supabase.co:5432/postgres"
     ```

### 3. Running the App (Locally or Cloud)
- Make sure you are in the project directory (`crm/`).
- Install dependencies:
  ```
  pip install fastapi uvicorn sqlmodel jinja2
  ```
- Start the server:
  ```
  uvicorn main:app --reload
  ```
- Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) for the dashboard.

### 4. Deploying Online (Supabase + Cloud VM)
- Recommended: Deploy FastAPI app on [Railway](https://railway.app/), [Render](https://render.com/), [Fly.io](https://fly.io/), or your own VPS.
- Set your environment variables (`DATABASE_URL`) in the platform's dashboard.
- If using Supabase, ensure your IP is allowed (or use Supabase's pooler).

### 5. Customization
- Extend the DB model, routes, and templates as needed.
- Add authentication (Supabase auth, OAuth) for production.
- Integrate actual message sending via email API, SMS, or OF DMs.

## Tips
- For rapid local dev, SQLite is fine; migrate to Postgres/Supabase for team/cloud.
- You can add features (batch import, analytics, tier automations) as desired.
- Templates are basic for fast start—apply your own styles or Bootstrap.

---

**Questions? Want feature examples or advanced integrations?**  
Ask your AI assistant for any extension!
