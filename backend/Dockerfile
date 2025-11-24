FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for WeasyPrint (official docs)
# https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#debian-11-ubuntu-20-04
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libffi-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (includes templates/ directory)
COPY backend/ .

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
# Railway sets $PORT dynamically, default to 8000 for local development
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
