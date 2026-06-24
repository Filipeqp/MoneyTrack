from sqlmodel import Session

import main
from main import IndicadorFinanceiro, _category_totals, _get_latest_cached_indicator, _month_key
from services.public_finance_api import PublicFinanceApiError


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------

def test_month_key_extracts_year_and_month():
    assert _month_key("2026-06-05") == "2026-06"


def test_month_key_falls_back_when_date_is_empty():
    assert _month_key("") == "sem-data"


def test_category_totals_sums_only_expenses_and_sorts_descending():
    transactions = [
        main.Transaction(descricao="a", categoria="Casa", tipo="despesa", valor=100, data="2026-06-01"),
        main.Transaction(descricao="b", categoria="Lazer", tipo="despesa", valor=300, data="2026-06-02"),
        main.Transaction(descricao="c", categoria="Casa", tipo="despesa", valor=50, data="2026-06-03"),
        main.Transaction(descricao="salario", categoria="Receita fixa", tipo="receita", valor=4000, data="2026-06-01"),
    ]

    totals = _category_totals(transactions)

    assert list(totals.items()) == [("Lazer", 300), ("Casa", 150)]


def test_get_latest_cached_indicator_returns_none_when_empty(test_engine):
    with Session(test_engine) as session:
        assert _get_latest_cached_indicator(session, "dolar") is None


def test_get_latest_cached_indicator_returns_most_recent_by_reference_date(test_engine):
    with Session(test_engine) as session:
        session.add(IndicadorFinanceiro(nome="dolar", valor=5.0, data_referencia="2026-06-01", fonte="x"))
        session.add(IndicadorFinanceiro(nome="dolar", valor=5.5, data_referencia="2026-06-03", fonte="x"))
        session.add(IndicadorFinanceiro(nome="euro", valor=6.0, data_referencia="2026-06-05", fonte="x"))
        session.commit()

        latest = _get_latest_cached_indicator(session, "dolar")

        assert latest.valor == 5.5


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

def test_create_and_list_transaction(client):
    payload = {"data": "2026-06-10", "descricao": "Cinema", "valor": 50, "tipo": "despesa", "categoria": "Lazer"}

    created = client.post("/transactions", json=payload)
    assert created.status_code == 200

    listed = client.get("/transactions").json()
    assert len(listed) == 1
    assert listed[0]["description"] == "Cinema"
    assert listed[0]["kind"] == "expense"
    assert listed[0]["amount"] == 50


def test_update_transaction(client):
    created = client.post(
        "/transactions",
        json={"data": "2026-06-10", "descricao": "Cinema", "valor": 50, "tipo": "despesa", "categoria": "Lazer"},
    ).json()

    response = client.put(
        f"/transactions/{created['id']}",
        json={"data": "2026-06-11", "descricao": "Show", "valor": 80, "tipo": "despesa", "categoria": "Lazer"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Show"
    assert body["amount"] == 80


def test_update_transaction_404_when_missing(client):
    response = client.put(
        "/transactions/999",
        json={"data": "2026-06-11", "descricao": "Show", "valor": 80, "tipo": "despesa", "categoria": "Lazer"},
    )

    assert response.status_code == 404


def test_delete_transaction(client):
    created = client.post(
        "/transactions",
        json={"data": "2026-06-10", "descricao": "Cinema", "valor": 50, "tipo": "despesa", "categoria": "Lazer"},
    ).json()

    response = client.delete(f"/transactions/{created['id']}")
    assert response.status_code == 200
    assert response.json() == {"deleted": True, "id": created["id"]}

    second_attempt = client.delete(f"/transactions/{created['id']}")
    assert second_attempt.status_code == 404


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

def test_create_and_list_goal(client):
    payload = {"nome": "Viagem", "valor_objetivo": 1000, "valor_atual": 200, "prazo": "2027-01-01"}

    client.post("/goals", json=payload)

    goals = client.get("/goals").json()
    assert len(goals) == 1
    assert goals[0]["name"] == "Viagem"
    assert goals[0]["target_amount"] == 1000


def test_update_goal_404_when_missing(client):
    response = client.put(
        "/goals/999",
        json={"nome": "Viagem", "valor_objetivo": 1000, "valor_atual": 200, "prazo": "2027-01-01"},
    )

    assert response.status_code == 404


def test_delete_goal_404_when_missing(client):
    response = client.delete("/goals/999")

    assert response.status_code == 404


def test_upload_goal_photo_rejects_unsupported_extension(client, tmp_path, monkeypatch):
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    goal = client.post(
        "/goals", json={"nome": "Viagem", "valor_objetivo": 1000, "valor_atual": 200, "prazo": "2027-01-01"}
    ).json()

    response = client.post(
        f"/metas/{goal['id']}/foto",
        files={"foto": ("foto.txt", b"not-an-image", "text/plain")},
    )

    assert response.status_code == 400


def test_upload_goal_photo_404_when_goal_missing(client, tmp_path, monkeypatch):
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)

    response = client.post(
        "/metas/999/foto",
        files={"foto": ("foto.png", b"fake-bytes", "image/png")},
    )

    assert response.status_code == 404


def test_upload_goal_photo_stores_file_and_updates_goal(client, tmp_path, monkeypatch):
    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    goal = client.post(
        "/goals", json={"nome": "Viagem", "valor_objetivo": 1000, "valor_atual": 200, "prazo": "2027-01-01"}
    ).json()

    response = client.post(
        f"/metas/{goal['id']}/foto",
        files={"foto": ("foto.png", b"fake-bytes", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["foto_url"].startswith("/uploads/metas/meta-")
    assert any(tmp_path.iterdir())


# ---------------------------------------------------------------------------
# Suggested categories
# ---------------------------------------------------------------------------

def test_suggested_category_crud(client):
    created = client.post(
        "/suggested-categories",
        json={"name": "Transporte", "monthly_limit": 200, "description": "Uber e combustivel"},
    ).json()

    updated = client.put(
        f"/suggested-categories/{created['id']}",
        json={"name": "Transporte", "monthly_limit": 350, "description": "Uber e combustivel"},
    )
    assert updated.status_code == 200
    assert updated.json()["monthly_limit"] == 350

    deleted = client.delete(f"/suggested-categories/{created['id']}")
    assert deleted.status_code == 200

    assert client.delete(f"/suggested-categories/{created['id']}").status_code == 404


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def _add_transaction(client, **overrides):
    payload = {"data": "2026-06-01", "descricao": "item", "valor": 100, "tipo": "despesa", "categoria": "Casa"}
    payload.update(overrides)
    client.post("/transactions", json=payload)


def test_dashboard_resumo_computes_balance(client):
    _add_transaction(client, descricao="Salario", tipo="receita", categoria="Receita fixa", valor=1000, data="2026-06-01")
    _add_transaction(client, descricao="Aluguel", tipo="despesa", categoria="Casa", valor=400, data="2026-06-02")

    summary = client.get("/dashboard/resumo").json()

    assert summary["saldo_atual"] == 600
    assert summary["total_receitas_mes"] == 1000
    assert summary["total_despesas_mes"] == 400
    assert summary["quantidade_transacoes"] == 2


def test_dashboard_resumo_score_drops_when_balance_negative(client):
    _add_transaction(client, descricao="Salario", tipo="receita", categoria="Receita fixa", valor=1000, data="2026-06-01")
    _add_transaction(client, descricao="Compras", tipo="despesa", categoria="Casa", valor=1500, data="2026-06-02")

    summary = client.get("/dashboard/resumo").json()

    assert summary["saldo_atual"] == -500
    assert summary["score_financeiro"] == 40


def test_dashboard_gastos_por_categoria(client):
    _add_transaction(client, categoria="Casa", valor=100, data="2026-06-01")
    _add_transaction(client, categoria="Lazer", valor=300, data="2026-06-02")

    response = client.get("/dashboard/gastos-por-categoria").json()

    assert response == {"labels": ["Lazer", "Casa"], "values": [300, 100]}


def test_dashboard_receitas_despesas_mensais_groups_by_month(client):
    _add_transaction(client, tipo="receita", categoria="Receita fixa", valor=1000, data="2026-05-15")
    _add_transaction(client, tipo="despesa", categoria="Casa", valor=200, data="2026-06-01")

    response = client.get("/dashboard/receitas-despesas-mensais").json()

    assert response["labels"] == ["2026-05", "2026-06"]
    assert response["receitas"] == [1000, 0]
    assert response["despesas"] == [0, 200]


def test_dashboard_evolucao_saldo_orders_by_date(client):
    _add_transaction(client, tipo="receita", categoria="Receita fixa", valor=500, data="2026-06-02")
    _add_transaction(client, tipo="despesa", categoria="Casa", valor=100, data="2026-06-01")

    response = client.get("/dashboard/evolucao-saldo").json()

    assert response["labels"] == ["2026-06-01", "2026-06-02"]
    assert response["values"] == [-100, 400]


def test_dashboard_metas_calculates_percentual(client):
    client.post("/goals", json={"nome": "Viagem", "valor_objetivo": 1000, "valor_atual": 250, "prazo": "2027-01-01"})

    response = client.get("/dashboard/metas").json()

    assert response["items"][0]["percentual"] == 25.0


def test_dashboard_score_endpoint_matches_resumo(client):
    _add_transaction(client, tipo="receita", categoria="Receita fixa", valor=1000, data="2026-06-01")

    resumo = client.get("/dashboard/resumo").json()
    score = client.get("/dashboard/score").json()

    assert score == {"score": resumo["score_financeiro"]}


def test_dashboard_insights_mentions_top_category(client):
    _add_transaction(client, categoria="Lazer", valor=300, data="2026-06-01")

    insights = client.get("/dashboard/insights").json()["items"]

    assert any("Lazer" in item for item in insights)


# ---------------------------------------------------------------------------
# Indicadores (with mocked public-finance fetchers)
# ---------------------------------------------------------------------------

def test_get_indicador_fetches_and_stores(client, monkeypatch):
    monkeypatch.setitem(
        main.INDICATOR_FETCHERS,
        "dolar",
        lambda: {"nome": "dolar", "valor": 5.25, "data_referencia": "2026-06-01", "fonte": "teste"},
    )

    response = client.get("/indicadores/dolar")

    assert response.status_code == 200
    body = response.json()
    assert body["valor"] == 5.25
    assert body["stale"] is False


def test_get_indicador_returns_stale_cache_on_api_error(client, monkeypatch):
    def fetch_then_fail():
        raise PublicFinanceApiError("API fora do ar")

    monkeypatch.setitem(main.INDICATOR_FETCHERS, "dolar", fetch_then_fail)

    with Session(main.engine) as session:
        session.add(IndicadorFinanceiro(nome="dolar", valor=5.0, data_referencia="2026-05-30", fonte="cache"))
        session.commit()

    response = client.get("/indicadores/dolar")

    assert response.status_code == 200
    body = response.json()
    assert body["stale"] is True
    assert body["warning"] == "API fora do ar"


def test_get_indicador_returns_503_when_no_cache_and_api_fails(client, monkeypatch):
    def always_fail():
        raise PublicFinanceApiError("API fora do ar")

    monkeypatch.setitem(main.INDICATOR_FETCHERS, "dolar", always_fail)

    response = client.get("/indicadores/dolar")

    assert response.status_code == 503


def test_get_indicador_does_not_duplicate_existing_entry(client, monkeypatch):
    monkeypatch.setitem(
        main.INDICATOR_FETCHERS,
        "dolar",
        lambda: {"nome": "dolar", "valor": 5.25, "data_referencia": "2026-06-01", "fonte": "teste"},
    )

    client.get("/indicadores/dolar")
    client.get("/indicadores/dolar")

    indicadores = client.get("/indicadores").json()
    assert indicadores["total"] == 1
