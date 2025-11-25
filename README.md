

# 📌 Table Type Detector Service

A micro-service that receives an image of a financial statement table and predicts the table type — **balance** or **activity** — using a pre-trained **YOLO object detection model**.

The service exposes a clean FastAPI-based REST API, including:

* File upload endpoint for prediction
* Health-check endpoint
* Auto-generated Swagger docs
* Web-based demo UI for manual testing

The model is loaded once at application startup and kept in memory for optimal low-latency inference.

---
## link to service:
https://table-type-detector-541653278614.me-west1.run.app/
## 🗂️ Project Structure

```
project-root/
│
├── app/
│   ├── main.py          # FastAPI routers and endpoints
│   ├── model.py         # YOLO loading + prediction logic
│   ├── config.py        # Settings via Pydantic
│   ├── schemas.py       # Pydantic response models
│   └── utils/           # (optional helpers)
│
├── model/               # YOLO .pt weights (not tracked in repo)
│   └── table_type_identification.pt
│
├── tests/               # Unit tests
│   ├──test_validation.py
│   └──test_predict.py
├── run_tests.ps1        # Run automated tests  
├── run_local.ps1        # Run API locally 
├── Dockerfile          
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration

All configuration is controlled through environment variables.
Create a `.env` file in project root:

```
MODEL_PATH=./model/table_type_identification.pt
TABLE_LABELS=balance,activity
# API_KEY=your_api_key_here (optional, if you want to enforce it)
```

The application reads them using `pydantic-settings`.

---

## 🧪 Local Development

### 1️⃣ Install & activate virtual environment

```bash
python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the API

```powershell
.\run_local.ps1
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## 📍 Endpoints

| Method | Endpoint   | Description                      |
| ------ | ---------- | -------------------------------- |
| GET    | `/`        | Web-based demo UI                |
| GET    | `/docs`    | Swagger UI                       |
| GET    | `/health`  | Model & service health check     |
| POST   | `/predict` | Upload image → return prediction |

Example response from `/predict`:

```json
{
  "predicted_label": "balance",
  "confidence": 0.92,
  "boxes": null
}
```

---

## 🔐 Security (optional)

The `/predict` endpoint can require an API key via header:

```
x-api-key: YOUR_KEY_HERE
```

Enable by setting `API_KEY` in `.env`.

---

## 🧫 Testing

To run unit tests:

```powershell
.\run_tests.ps1
```

Example result:

```
6 passed in 4.03s
```

---

## 🐳 Docker Deployment

Build image:

```bash
docker build -t table-type-detector .
```

Run container:

```bash
docker run -p 8000:8000 table-type-detector
```

Cloud Run / Artifact Registry deployment supported out of the box.

---

## 🧠 Tech Stack

| Category        | Tools              |
| --------------- | ------------------ |
| Language        | Python 3.12        |
| Framework       | FastAPI            |
| Model Runtime   | YOLO (Ultralytics) |
| Infra-ready for | Google Cloud Run   |
| Testing         | pytest             |
| Config          | Pydantic Settings  |
| Packaging       | Docker             |

---

## 📜 License

This project is licensed for the interview and demonstration purposes only.
Not intended for commercial deployment without permission.

---

## 👤 Author

Developed by **Ori Roth**
Machine Learning & Software Engineer

