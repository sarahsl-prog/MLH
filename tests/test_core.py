import types

import pytest

from apisec_tester import core


class DummyResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text


def test_check_injection_reflection(monkeypatch):
    # simulate a reflected payload in the response
    def fake_get(url, params=None, timeout=0):
        payload = params.get('q', '')
        return DummyResponse(status_code=200, text=f"hello {payload}")

    monkeypatch.setattr(core.requests, 'get', fake_get)
    r = core.check_injection('http://example.test')
    assert r['status'] == 'warn'
    assert any(e['type'] == 'reflection' for e in r['evidence'])


def test_check_rate_limit_detects_no_429(monkeypatch):
    # return 200 every time
    def fake_get(url, timeout=0):
        return DummyResponse(status_code=200, text="ok")

    monkeypatch.setattr(core.requests, 'get', fake_get)
    r = core.check_rate_limit('http://example.test', attempts=3, pause=0)
    assert r['status'] == 'warn'


def test_check_auth_401(monkeypatch):
    def fake_get(url, headers=None, timeout=0, allow_redirects=True):
        return DummyResponse(status_code=401, text='Unauthorized')

    monkeypatch.setattr(core.requests, 'get', fake_get)
    r = core.check_auth('http://example.test')
    assert r['status'] == 'pass'
