FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# מכריחים התקנה של torch CPU לפני הכל
RUN pip install --no-cache-dir \
    torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu

# עכשיו מתקינים את שאר החבילות (בלי torch שוב)
COPY requirements.txt .
RUN sed '/torch/d' requirements.txt > requirements_no_torch.txt && \
    pip install --no-cache-dir -r requirements_no_torch.txt && \
    rm requirements_no_torch.txt

COPY app/ ./app
COPY model/ ./model

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV MODEL_PATH="model/table_type_identification.pt"
ENV TABLE_LABELS="balance,activity"
ENV PORT=8080

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]