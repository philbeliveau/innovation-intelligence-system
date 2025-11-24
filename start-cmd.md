  # 1. Start Backend (Terminal 1)

  Or simpler (without --reload to avoid restarts):
   lsof -ti:8000 | xargs kill -9
  cd backend
  uvicorn app.main:app --host 0.0.0.0 --port 8000

  (The backend will automatically load variables from .env file)

  2. Start Gradio (Terminal 2)
lsof -ti:7860 | xargs kill -9
 cd backend/experimentation 
 python gradio_lab.py

  Access URLs:
  - Backend API: http://localhost:8000
  - Gradio UI: http://localhost:7860