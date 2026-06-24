import requests

from services import public_finance_api as api


class FakeResponse:
    def __init__(self, json_data=None, json_error=None, status_error=None):
        self._json_data = json_data
        self._json_error = json_error
        self._status_error = status_error

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        if self._json_error:
            raise self._json_error
        return self._json_data


def test_parse_decimal_handles_comma_separator():
    assert api._parse_decimal("3,75") == 3.75


def test_parse_decimal_handles_numeric_input():
    assert api._parse_decimal(10.5) == 10.5


def test_request_json_raises_public_finance_api_error_on_connection_failure(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(requests, "get", fake_get)

    try:
        api._request_json("http://example.com")
        assert False, "expected PublicFinanceApiError"
    except api.PublicFinanceApiError:
        pass


def test_request_json_raises_public_finance_api_error_on_invalid_json(monkeypatch):
    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **k: FakeResponse(json_error=ValueError("invalid json")),
    )

    try:
        api._request_json("http://example.com")
        assert False, "expected PublicFinanceApiError"
    except api.PublicFinanceApiError:
        pass


def test_request_json_returns_parsed_payload_on_success(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(json_data={"value": [1, 2]}))

    assert api._request_json("http://example.com") == {"value": [1, 2]}


def test_fetch_currency_returns_latest_quote_by_date(monkeypatch):
    monkeypatch.setattr(
        api,
        "_request_json",
        lambda *a, **k: {
            "value": [
                {"cotacaoVenda": "5,10", "dataHoraCotacao": "2026-06-01 13:00:00.000"},
                {"cotacaoVenda": "5,25", "dataHoraCotacao": "2026-06-03 13:00:00.000"},
            ]
        },
    )

    result = api._fetch_currency("USD")

    assert result == {
        "valor": 5.25,
        "data_referencia": "2026-06-03",
        "fonte": "Banco Central do Brasil - PTAX",
    }


def test_fetch_currency_raises_when_no_quotes_available(monkeypatch):
    monkeypatch.setattr(api, "_request_json", lambda *a, **k: {"value": []})

    try:
        api._fetch_currency("USD")
        assert False, "expected PublicFinanceApiError"
    except api.PublicFinanceApiError:
        pass


def test_fetch_sgs_indicator_returns_last_row(monkeypatch):
    monkeypatch.setattr(
        api,
        "_request_json",
        lambda *a, **k: [
            {"data": "01/06/2026", "valor": "13,25"},
            {"data": "02/06/2026", "valor": "13,75"},
        ],
    )

    result = api._fetch_sgs_indicator("Selic", 432)

    assert result == {
        "valor": 13.75,
        "data_referencia": "02/06/2026",
        "fonte": "Banco Central do Brasil - SGS 432",
    }


def test_fetch_sgs_indicator_raises_when_empty(monkeypatch):
    monkeypatch.setattr(api, "_request_json", lambda *a, **k: [])

    try:
        api._fetch_sgs_indicator("Selic", 432)
        assert False, "expected PublicFinanceApiError"
    except api.PublicFinanceApiError:
        pass


def test_fetch_dolar_atual_adds_nome_field(monkeypatch):
    monkeypatch.setattr(
        api,
        "_fetch_currency",
        lambda symbol: {"valor": 5.0, "data_referencia": "2026-06-01", "fonte": "x"},
    )

    assert api.fetch_dolar_atual()["nome"] == "dolar"


def test_fetch_selic_atual_uses_expected_sgs_code(monkeypatch):
    captured = {}

    def fake_fetch_sgs_indicator(name, code):
        captured["name"] = name
        captured["code"] = code
        return {"valor": 1, "data_referencia": "2026-06-01", "fonte": "x"}

    monkeypatch.setattr(api, "_fetch_sgs_indicator", fake_fetch_sgs_indicator)

    api.fetch_selic_atual()

    assert captured == {"name": "Selic", "code": 432}
