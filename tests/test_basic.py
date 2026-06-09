"""UltraQuant tests."""

from ultraquant.strategies.event_detector import EventDetector


def test_event_detector_no_crash():
    det = EventDetector()
    for i in range(50):
        det.update(price=50000 + i * 10, volume=100000 + i * 1000)
    assert True


def test_event_detector_volume_surge():
    det = EventDetector()
    for _ in range(25):
        det.update(price=50000, volume=100000)
    result = det.update(price=50100, volume=500000)
    assert result is not None
    assert result["type"] == "volume_surge"


def test_event_detector_no_event():
    det = EventDetector()
    for _ in range(25):
        result = det.update(price=50000, volume=100000)
    assert result is None
