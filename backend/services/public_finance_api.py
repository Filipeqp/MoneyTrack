from datetime import date, timedelta

import requests


BCB_SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/1"
BCB_PTAX_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
)

TIMEOUT_SECONDS = 10


class PublicFinanceApiError(RuntimeError):
    pass


def _request_json(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
      raise PublicFinanceApiError("A API publica financeira esta indisponivel.") from exc
    except ValueError as exc:
      raise PublicFinanceApiError("A API publica retornou um JSON invalido.") from exc


def _parse_decimal(value):
    return float(str(value).replace(",", "."))


def _fetch_currency(symbol):
    end = date.today()
    start = end - timedelta(days=10)
    params = {
        "@moeda": f"'{symbol}'",
        "@dataInicial": f"'{start.strftime('%m-%d-%Y')}'",
        "@dataFinalCotacao": f"'{end.strftime('%m-%d-%Y')}'",
        "$format": "json",
    }
    data = _request_json(BCB_PTAX_URL, params=params)
    quotes = data.get("value", [])
    if not quotes:
        raise PublicFinanceApiError(f"Nenhuma cotacao encontrada para {symbol}.")

    quote = sorted(quotes, key=lambda item: item["dataHoraCotacao"])[-1]
    return {
        "valor": _parse_decimal(quote["cotacaoVenda"]),
        "data_referencia": quote["dataHoraCotacao"][:10],
        "fonte": "Banco Central do Brasil - PTAX",
    }


def _fetch_sgs_indicator(name, code):
    data = _request_json(BCB_SGS_URL.format(code=code), params={"formato": "json"})
    if not data:
        raise PublicFinanceApiError(f"Nenhum dado encontrado para {name}.")

    row = data[-1]
    return {
        "valor": _parse_decimal(row["valor"]),
        "data_referencia": row["data"],
        "fonte": f"Banco Central do Brasil - SGS {code}",
    }


def fetch_dolar_atual():
    return {"nome": "dolar", **_fetch_currency("USD")}


def fetch_euro_atual():
    return {"nome": "euro", **_fetch_currency("EUR")}


def fetch_selic_atual():
    return {"nome": "selic", **_fetch_sgs_indicator("Selic", 432)}


def fetch_ipca_atual():
    return {"nome": "ipca", **_fetch_sgs_indicator("IPCA", 13522)}


def fetch_cdi_atual():
    return {"nome": "cdi", **_fetch_sgs_indicator("CDI", 4389)}
