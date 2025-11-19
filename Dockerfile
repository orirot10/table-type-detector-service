FROM python:3.11-slim

# Install gsutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# Required system packages for YOLO
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download model directly from GCS into the image
RUN mkdir -p model && \
    gsutil cp gs://table-detector-model-eu/table_type_identification.pt model/table_type_identification.pt

ENV MODEL_PATH="model/table_type_identification.pt"
ENV TABLE_LABELS="balance,activity"
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8080"]
