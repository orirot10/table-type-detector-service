FROM python:3.11-slim

RUN useradd -m appuser
WORKDIR /app

# Pillow/YOLO/Opencv 
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app ./app
COPY model ./model

EXPOSE 8080
ENV PORT=8080

ENV PYTHONUNBUFFERED=1

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
