# FastAPI backend

See the project root `README.md` for the full Windows setup and API examples. Start from this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit the PostgreSQL credentials in .env.
python -m app.init_db
uvicorn app.main:app --reload
```

Interactive API documentation: http://127.0.0.1:8000/docs
