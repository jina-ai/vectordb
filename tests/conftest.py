import pytest


@pytest.fixture(autouse=True)
def test_log_level(monkeypatch):
    monkeypatch.setenv('JINA_LOG_LEVEL', 'DEBUG')


@pytest.fixture(autouse=True)
def test_disable_telemetry(monkeypatch):
    monkeypatch.setenv('JINA_OPTOUT_TELEMETRY', 'True')
