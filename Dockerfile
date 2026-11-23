# Kitakaró AI – konténer a Google Cloud Run-hoz (bármilyen Docker hoston fut)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/hf-cache \
    PORT=8080

WORKDIR /app

# CPU-s torch és torchvision együtt, ugyanonnan (különben verzióütközés lesz a timm miatt)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# A két modell letöltése build közben, hogy induláskor ne kelljen
COPY detector.py .
RUN python -c "import detector"

COPY . .

# 1 worker: a modellek egyszer töltődnek be; a szálak párhuzamos kéréseket szolgálnak ki
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app
