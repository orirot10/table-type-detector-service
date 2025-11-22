import io
from PIL import Image
import pytest

from app.main import validate_image_bytes, MAX_FILE_SIZE_BYTES, raise_http_error
from fastapi import HTTPException


def make_image_bytes(size=(500, 500), fmt="JPEG") -> bytes:
    img = Image.new("RGB", size, color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_validate_image_ok():
    img_bytes = make_image_bytes()
   # No exception should be raised
    validate_image_bytes(img_bytes)


def test_validate_image_empty():
    with pytest.raises(HTTPException) as exc:
        validate_image_bytes(b"")
    assert exc.value.status_code == 400
    assert exc.value.detail["error_code"] == "EMPTY_FILE"


def test_validate_image_too_large():
    # MAX_FILE_SIZE_BYTES
    big_bytes = b"x" * (MAX_FILE_SIZE_BYTES + 1)
    with pytest.raises(HTTPException) as exc:
        validate_image_bytes(big_bytes)
    assert exc.value.detail["error_code"] == "FILE_TOO_LARGE"


def test_validate_image_too_small():
    # TOO SMALL: less than 50*50 pixels
    small_bytes = make_image_bytes(size=(50, 50))
    with pytest.raises(HTTPException) as exc:
        validate_image_bytes(small_bytes)
    assert exc.value.detail["error_code"] == "IMAGE_TOO_SMALL"
