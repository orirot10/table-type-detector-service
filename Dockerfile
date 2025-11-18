FROM python:3.11-slim

# install dependent libraries for OpenCV + YOLO

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# install Google Cloud SDK and gsutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

#creat e app user 
RUN useradd -m appuser
WORKDIR /app

#  Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# copy app files to container without the model
COPY app ./app

# download the model from GCS when building the image
RUN mkdir -p model && \
    gsutil cp gs://table-detector-model-eu/table_type_identification.pt ./model/table_type_identification.pt

# give ownership of the app directory to appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]