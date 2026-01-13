# F. Deployment Guide

## 1. Django Frontend Deployment
**Recommended Platform**: Render, Railway, or VPS (DigitalOcean/Hetzner).

### Steps (e.g., Render/Railway):
1.  **Repository**: Push your code to GitHub.
2.  **Environment Variables**:
    -   `django_SECRET_KEY`: Your production secret key.
    -   `DEBUG`: `False`.
    -   `ALLOWED_HOSTS`: Your domain name.
    -   `FASTAPI_URL`: The URL of your deployed FastAPI backend (e.g., `https://my-fastapi.railway.app`).
3.  **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4.  **Start Command**: `gunicorn chatbot_project.wsgi:application`

## 2. FastAPI Backend Deployment
**Recommended Platform**: Railway, Fly.io, or VPS.

### Steps:
1.  **Repository**: Push code (can be same repo, different folder, or separate repo).
2.  **Environment Variables**:
    -   `OPENAI_API_KEY`: Your LLM API key.
    -   `CHROMA_DB_PATH`: If using persistent local storage (only works on VPS with persistent disk). For serverless, use a managed Vector DB or a persistent volume.
3.  **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`

## 3. Vector Database Deployment

### Option A: Managed Service (Recommended for Production)
-   **Supabase (pgvector)**: Enable `pgvector` extension on a Supabase Postgres instance.
-   **Pinecone / Weaviate Cloud**: Fully managed vector databases.

### Option B: Self-Hosted (ChromaDB)
-   **On VPS**: ChromaDB can run embedded within the FastAPI container. If you deploy FastAPI to a stateless container (like standard Render/Heroku), you lose the indices on restart.
-   **Solution for Stateless**: Mount a **Persistent Volume** (available on Railway, Fly.io, Render) to the path where Chroma saves its data.

---

# Environment Variables (`.env`)

## Django `.env`
```ini
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
FASTAPI_BACKEND_URL=http://localhost:8000
```

## FastAPI `.env`
```ini
OPENAI_API_KEY=sk-proj-....
# If using ChromaDB locally
CHROMA_PERSIST_DIRECTORY=./chroma_db
# If using Groq
GROQ_API_KEY=gsk_...
```
