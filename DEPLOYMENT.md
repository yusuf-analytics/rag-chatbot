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

---

# G. Free Tier Deployment Strategies

Jika Anda ingin opsi **GRATIS**, berikut adalah rekomendasinya. Perhatikan bahwa layanan gratis memiliki batasan (seperti *sleep* saat tidak digunakan).

## 1. Render (Paling Mudah)
Render memiliki "Free Tier" untuk Web Service, tetapi **wip** (menghapus) data disk setiap kali restart.
- **Masalah**: Database ChromaDB (folder `chroma_db/`) akan hilang setiap kali aplikasi restart/deploy.
- **Solusi**: Biarkan hilang. Aplikasi Anda akan otomatis membuat ulang index dari `sample_data.json` saat startup karena kode kita sudah punya logic `try...except` di startup.
- **Caveat**: Server akan "tidur" setelah 15 menit tidak aktif. Request pertama akan lambat (50 detik+).

### Cara Deploy di Render:
1.  Buat akun di [Render.com](https://render.com).
2.  **New Web Service** -> Connect GitHub Repo.
3.  **Deploy Backend** (Folder `rag_chatbot/backend_fastapi`):
    -   **Root Directory**: `rag_chatbot/backend_fastapi`
    -   **Environment**: Python 3
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    -   **Env Vars**: Tambahkan `GROQ_API_KEY` dll.
4.  **Deploy Frontend** (Folder `rag_chatbot/frontend_django`):
    -   **Root Directory**: `rag_chatbot/frontend_django`
    -   **Environment**: Python 3
    -   **Build Command**: `pip install -r requirements.txt && python manage.py migrate`
    -   **Start Command**: `gunicorn chat_app.wsgi:application`
    -   **Env Vars**: `FASTAPI_URL` (URL Backend dari langkah 3), `SECRET_KEY`, `DEBUG=False`.

## 2. PythonAnywhere (Paling Stabil untuk Python)
- **Gratis**: 1 Web App.
- **Masalah**: Versi gratis tidak bisa melakukan request HTTP keluar ke situs selain yang di-whitelist (tapi OpenAI/Groq biasanya ok).
- **Setup**: Sedikit lebih manual (upload file zip atau git pull via console, lalu setup Virtualenv).
- **Storage**: Persistent (Data tidak akan hilang).

**Rekomendasi Utama**: Gunakan **Render** untuk kemudahan setup jika Anda oke dengan "cold start" (loading awal lambat).
