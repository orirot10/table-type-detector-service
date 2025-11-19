# Table Type Detector Service

## Overview

The **Table Type Detector Service** is a lightweight Python-based web service designed to automatically classify the type of tables in structured data, such as those extracted from documents (e.g., PDFs, images, or spreadsheets). This tool is particularly useful for data processing pipelines, ETL (Extract, Transform, Load) workflows, and AI-driven document analysis systems.

Built as a technical task for an AI Engineer position, this service leverages machine learning techniques (e.g., rule-based heuristics or simple neural networks) to detect table types like:
- **Relational tables** (e.g., database-like with headers and rows)
- **Summary tables** (e.g., aggregated statistics)
- **Hierarchical tables** (e.g., with nested structures)
- **Key-value pairs** (e.g., simple mappings)

The service exposes a RESTful API for easy integration into larger applications.

## Features

- **Fast Inference**: Low-latency classification using optimized models.
- **Flexible Input**: Accepts JSON payloads with table representations (e.g., lists of lists or pandas DataFrames serialized as JSON).
- **Extensible**: Modular design allows easy addition of new table types or detection algorithms.
- **Docker Support**: Containerized deployment for scalability.
- **Logging & Monitoring**: Built-in logging for debugging and performance tracking.

## Prerequisites

- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- pip or conda for dependency management

## Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/orirot10/table-type-detector-service.git
   cd table-type-detector-service
   ```

2. **Install Dependencies**:
   Create a virtual environment (recommended) and install the required packages:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Key dependencies include:
   - `flask` or `fastapi` for the web server
   - `pandas` for data handling
   - `scikit-learn` or `torch` for ML models (if applicable)
   - `gunicorn` for production serving

3. **Docker Installation (Alternative)**:
   Build and run the container:
   ```
   docker build -t table-type-detector .
   docker run -p 5000:5000 table-type-detector
   ```

## Usage

### Running the Service

Start the development server:
```
python app.py  # or uvicorn main:app --reload if using FastAPI
```

The service will be available at `http://localhost:5000`.

### API Endpoints

- **POST /detect**  
  Classify a table's type.  
  **Request Body** (JSON):
  ```json
  {
    "table": [
      ["Header1", "Header2"],
      ["Row1-Col1", "Row1-Col2"],
      ["Row2-Col1", "Row2-Col2"]
    ],
    "options": {
      "confidence_threshold": 0.8
    }
  }
  ```  
  **Response** (JSON):
  ```json
  {
    "table_type": "relational",
    "confidence": 0.95,
    "explanation": "Detected headers and uniform rows."
  }
  ```

- **GET /health**  
  Health check endpoint. Returns `{"status": "healthy"}`.

Example using `curl`:
```
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -d '{"table": [["A", "B"], ["1", "2"]]}'
```

### Example Code Snippet

Integrate into your Python script:
```python
import requests

url = "http://localhost:5000/detect"
data = {
    "table": [
        ["Product", "Price"],
        ["Apple", "1.50"],
        ["Banana", "0.75"]
    ]
}

response = requests.post(url, json=data)
print(response.json())
# Output: {'table_type': 'key-value', 'confidence': 0.92, ...}
```

## Project Structure

```
table-type-detector-service/
├── app.py                # Main application entry point (Flask/FastAPI)
├── detector.py           # Core table type detection logic
├── models/               # ML models or rule sets
│   └── table_classifier.pkl
├── tests/                # Unit and integration tests
│   └── test_detector.py
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Optional: For multi-service setups
└── README.md             # This file
```

## Testing

Run tests with:
```
pytest tests/
```

Ensure 100% coverage for detection accuracy.

## Deployment

- **Heroku/Vercel**: Use the `Procfile` (create if needed) with `web: gunicorn app:app`.
- **Kubernetes**: Scale with replicas based on traffic.
- **Environment Variables**:
  - `PORT`: Server port (default: 5000)
  - `MODEL_PATH`: Path to the detection model

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

Feedback and pull requests are welcome! For major changes, please open an issue first.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (If no LICENSE file exists, feel free to add one.)

## Acknowledgments

- Developed as part of an AI Engineer position task.
- Thanks to open-source libraries like Pandas and Scikit-learn.

---

For questions or issues, open a GitHub issue or contact [orirot10](https://github.com/orirot10).
