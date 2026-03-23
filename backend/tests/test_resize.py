import io

from PIL import Image

from app.services.dalle import resize_image_bytes


def _make_png(width: int = 100, height: int = 100) -> bytes:
    img = Image.new("RGBA", (width, height), color=(255, 0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_resize_square():
    data = _make_png(1024, 1024)
    result = resize_image_bytes(data, 32, 32)
    img = Image.open(io.BytesIO(result))
    assert img.size == (32, 32)


def test_resize_non_square():
    data = _make_png(1024, 1024)
    result = resize_image_bytes(data, 192, 128)
    img = Image.open(io.BytesIO(result))
    assert img.size == (192, 128)


def test_resize_preserves_png():
    data = _make_png(64, 64)
    result = resize_image_bytes(data, 16, 16)
    img = Image.open(io.BytesIO(result))
    assert img.format == "PNG"


def test_generate_request_target_dims():
    """target_width/target_height are optional fields on GenerateRequest."""
    from app.routers.generate import GenerateRequest

    req = GenerateRequest(prompt="test", name="test", target_width=64, target_height=64)
    assert req.target_width == 64
    assert req.target_height == 64


def test_generate_request_no_target_dims():
    from app.routers.generate import GenerateRequest

    req = GenerateRequest(prompt="test", name="test")
    assert req.target_width is None
    assert req.target_height is None
