from app.utils.errors import ServiceError


def test_service_error_message():
    err = ServiceError("dalle", "quota exceeded", 429)
    assert str(err) == "quota exceeded"


def test_service_error_to_dict():
    err = ServiceError("elevenlabs", "invalid key", 401)
    d = err.to_dict()
    assert d["service"] == "elevenlabs"
    assert d["detail"] == "invalid key"
    assert d["status_code"] == 401


def test_service_error_default_status():
    err = ServiceError("openrouter", "unknown")
    assert err.status_code == 500
