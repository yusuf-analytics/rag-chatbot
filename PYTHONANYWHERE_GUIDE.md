# Panduan Deployment di PythonAnywhere (Gratis & Tanpa Kartu Kredit)

PythonAnywhere adalah pilihan terbaik jika Anda tidak memiliki kartu kredit. Limitation utamanya adalah Anda hanya bisa menjalankan **satu** aplikasi web di akun gratis.

## Strategi Deployment
Karena hanya boleh 1 aplikasi, kita akan mendeploy **Django Frontend** sebagai aplikasi utama. Backend logic (AI) sebaiknya dijalankan sebagai bagian dari Django atau kita jalankan FastAPI di background (tapi ini agak *tricky* di akun gratis).

Untuk saat ini, kita akan deploy **Django** dulu agar minimal website Anda bisa diakses online.

---

## Langkah 1: Persiapan Code
Pastikan Anda sudah melakukan push code terakhir ke GitHub:
```bash
git add .
git commit -m "Siap deploy ke PythonAnywhere"
git push
```

## Langkah 2: Buat Akun & Upload Code
1.  Buka [www.pythonanywhere.com](https://www.pythonanywhere.com/) dan buat akun "Beginner" (Gratis).
2.  Setelah login, klik tab **Consoles** -> **Bash**.
3.  Di terminal Bash, clone repository Anda:
    ```bash
    git clone https://github.com/yusuf-analytics/rag-chatbot.git
    ```
4.  Masuk ke folder project:
    ```bash
    cd rag-chatbot
    ```

## Langkah 3: Setup Virtual Environment
Kita perlu menginstal library Python (Django, dll).
1.  Buat virtual environment:
    ```bash
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    ```
    *(Terminal akan otomatis masuk ke `(myenv)`)*.

2.  Install dependencies Frontend:
    ```bash
    pip install -r rag_chatbot/frontend_django/requirements.txt
    ```

3.  (Optional) Install dependencies Backend jika ingin menjalankan logic AI di server yang sama:
    ```bash
    pip install -r rag_chatbot/backend_fastapi/requirements.txt
    ```

## Langkah 4: Setup Database & Static Files
1.  Pindah ke folder frontend:
    ```bash
    cd rag_chatbot/frontend_django
    ```
2.  Jalankan migrasi database:
    ```bash
    python manage.py migrate
    ```
3.  Kumpulkan file statik (CSS/Gambar):
    ```bash
    python manage.py collectstatic
    ```
    *(Jawab `yes` jika ditanya)*.

## Langkah 5: Konfigurasi Web App
1.  Buka tab **Web** (di bagian atas dashboard PythonAnywhere).
2.  Klik **Add a new web app**.
3.  Pilih **Manual configuration** (NOTE: Jangan pilih "Django" otomatis, kita manual saja agar lebih fleksibel).
4.  Pilih **Python 3.10**.
5.  Setelah web app terbuat, scroll ke bawah ke bagian **Virtualenv**:
    -   Masukkan path: `/home/yusufanalytics/.virtualenvs/myenv` (Ganti `yusufanalytics` dengan username PythonAnywhere Anda).
6.  Scroll ke bagian **Code**:
    -   **Source code**: `/home/yusufanalytics/rag-chatbot/rag_chatbot/frontend_django`
    -   **Working directory**: `/home/yusufanalytics/rag-chatbot/rag_chatbot/frontend_django`

## Langkah 6: Konfigurasi WSGI
Di tab **Web**, klik link di sebelah **WSGI configuration file** (biasanya bernama `/var/www/yusufanalytics_pythonanywhere_com_wsgi.py`).

Hapus SEMUA isinya, dan ganti dengan kode berikut:

```python
import os
import sys

# Tambahkan path project ke system path
path = '/home/yusufanalytics/rag-chatbot/rag_chatbot/frontend_django'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable untuk settings Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'chatbot_project.settings'

# Aktifkan aplikasi WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*(Jangan lupa ganti `yusufanalytics` dengan username asli Anda jika berbeda)*.

Klik **Save**.

## Langkah 7: Reload & Cek
1.  Kembali ke tab **Web**.
2.  Klik tombol hijau **Reload <username>.pythonanywhere.com**.
3.  Klik link website Anda (misal `https://yusufanalytics.pythonanywhere.com`).

Website Anda sekarang seharusnya sudah online! 🎉

---
### Catatan Penting
-   Fitur Chatbot (AI) mungkin belum jalan sempurna karena Backend FastAPI-nya belum kita konfigurasi di sini.
-   Jika Anda ingin AI jalan, kita perlu trik khusus (menjalankan logic AI langsung di dalam view Django) karena akun gratis tidak bisa menjalankan 2 server (Django + Uvicorn) secara bersamaan di port berbeda.
