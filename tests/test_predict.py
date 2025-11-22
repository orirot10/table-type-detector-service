import io
from PIL import Image
from fastapi.testclient import TestClient
import pytest

from app.main import app, MAX_FILE_SIZE_BYTES


class FakeModel:
    def predict(self, image_bytes: bytes):
        # נניח שהמודל תמיד מחזיר balance עם confidence 0.9
        return "balance", 0.9


def make_image_bytes(size=(500, 500), fmt="JPEG") -> bytes:
    img = Image.new("RGB", size, color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture
def client(monkeypatch):
    #   Mock get_model to return our FakeModel  
    from app import main as main_module

    def fake_get_model():
        return FakeModel()

    monkeypatch.setattr(main_module, "get_model", fake_get_model)
    return TestClient(main_module.app)


def test_predict_success(client):
    img_bytes = make_image_bytes()
    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}

    response = client.post("/predict", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["predicted_label"] == "balance"
    assert data["confidence"] == pytest.approx(0.9, rel=1e-3)


def test_predict_rejects_large_file(client):
    big_bytes = b"x" * (MAX_FILE_SIZE_BYTES + 1)
    files = {"file": ("big.jpg", big_bytes, "image/jpeg")}

    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["error_code"] == "FILE_TOO_LARGE"
