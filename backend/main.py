from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import text
from sqlmodel import Field, Session, SQLModel, create_engine, select

from services.public_finance_api import (
    PublicFinanceApiError,
    fetch_cdi_atual,
    fetch_dolar_atual,
    fetch_euro_atual,
    fetch_ipca_atual,
    fetch_selic_atual,
)


class Transaction(SQLModel, table=True):
    __tablename__ = "transacoes"

    id: Optional[int] = Field(default=None, primary_key=True)
    data: str = Field(index=True)
    descricao: str
    valor: float
    tipo: str = Field(default="despesa", index=True)
    categoria: str = Field(index=True)
    origem_arquivo: str = ""
    hash_unico: str = Field(default="", index=True)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Goal(SQLModel, table=True):
    __tablename__ = "metas"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    valor_objetivo: float
    valor_atual: float = 0
    prazo: str
    foto_url: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SuggestedCategory(SQLModel, table=True):
    __tablename__ = "categorias_sugeridas"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    monthly_limit: float
    description: str


class User(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(index=True, unique=True)
    senha: str
    is_admin: bool = True
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class IndicadorFinanceiro(SQLModel, table=True):
    __tablename__ = "indicadores_financeiros"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    valor: float
    data_referencia: str = Field(index=True)
    fonte: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


engine = create_engine("sqlite:///finup.db")
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = Path("uploads/metas")
ADMIN_EMAIL = "admin@finup.local"
ADMIN_PASSWORD = "admin123"

INDICATOR_FETCHERS = {
    "dolar": fetch_dolar_atual,
    "euro": fetch_euro_atual,
    "selic": fetch_selic_atual,
    "ipca": fetch_ipca_atual,
    "cdi": fetch_cdi_atual,
}


def create_db_and_seed():
    SQLModel.metadata.create_all(engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with Session(engine) as session:
        session.exec(text("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome VARCHAR NOT NULL, email VARCHAR NOT NULL, senha VARCHAR NOT NULL, is_admin BOOLEAN NOT NULL, created_at VARCHAR NOT NULL)"))
        session.exec(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_usuarios_email ON usuarios (email)"))
        try:
            session.exec(text("ALTER TABLE metas ADD COLUMN foto_url VARCHAR DEFAULT ''"))
            session.commit()
        except Exception:
            session.rollback()

        admin_user = session.exec(select(User).where(User.email == ADMIN_EMAIL)).first()
        if admin_user:
            admin_user.senha = ADMIN_PASSWORD
            admin_user.is_admin = True
            admin_user.nome = admin_user.nome or "Administrador"
        else:
            session.add(
                User(
                    nome="Administrador",
                    email=ADMIN_EMAIL,
                    senha=ADMIN_PASSWORD,
                    is_admin=True,
                )
            )
        session.commit()

        existing_transaction = session.exec(select(Transaction)).first()
        if existing_transaction:
            return

        session.add_all(
            [
                Transaction(
                    descricao="Salario",
                    categoria="Receita fixa",
                    tipo="receita",
                    valor=4200,
                    data="2026-06-05",
                ),
                Transaction(
                    descricao="Restaurantes e delivery",
                    categoria="Alimentacao",
                    tipo="despesa",
                    valor=620,
                    data="2026-06-08",
                ),
                Transaction(
                    descricao="Compras do mercado",
                    categoria="Casa",
                    tipo="despesa",
                    valor=480,
                    data="2026-06-06",
                ),
            ]
        )
        session.add_all(
            [
                Goal(
                    nome="Viagem para praia",
                    valor_objetivo=2800,
                    valor_atual=1280,
                    prazo="2026-12-20",
                ),
                Goal(
                    nome="Reserva de emergencia",
                    valor_objetivo=6000,
                    valor_atual=2100,
                    prazo="2027-03-01",
                ),
            ]
        )
        session.add_all(
            [
                SuggestedCategory(
                    name="Restaurantes",
                    monthly_limit=450,
                    description="Delivery, lanches, almoco fora e cafes.",
                ),
                SuggestedCategory(
                    name="Transporte",
                    monthly_limit=300,
                    description="Combustivel, app, onibus, metro e estacionamento.",
                ),
                SuggestedCategory(
                    name="Assinaturas",
                    monthly_limit=120,
                    description="Streaming, apps, cursos e servicos recorrentes.",
                ),
            ]
        )
        session.add(
            Goal(
                nome="Notebook novo",
                valor_objetivo=4500,
                valor_atual=900,
                prazo="2027-01-10",
            )
        )
        session.commit()


def _indicator_payload(indicator: IndicadorFinanceiro, stale: bool = False):
    return {
        "id": indicator.id,
        "nome": indicator.nome,
        "valor": indicator.valor,
        "data_referencia": indicator.data_referencia,
        "fonte": indicator.fonte,
        "created_at": indicator.created_at,
        "stale": stale,
    }


def _get_latest_cached_indicator(session: Session, name: str):
    indicators = session.exec(
        select(IndicadorFinanceiro).where(IndicadorFinanceiro.nome == name)
    ).all()
    if not indicators:
        return None

    return sorted(
        indicators,
        key=lambda indicator: (indicator.data_referencia, indicator.created_at),
    )[-1]


def fetch_and_store_indicator(name: str):
    fetcher = INDICATOR_FETCHERS[name]
    with Session(engine) as session:
        try:
            data = fetcher()
        except PublicFinanceApiError as exc:
            cached = _get_latest_cached_indicator(session, name)
            if cached:
                payload = _indicator_payload(cached, stale=True)
                payload["warning"] = str(exc)
                return payload

            raise HTTPException(status_code=503, detail=str(exc)) from exc

        existing = session.exec(
            select(IndicadorFinanceiro).where(
                IndicadorFinanceiro.nome == data["nome"],
                IndicadorFinanceiro.data_referencia == data["data_referencia"],
            )
        ).first()
        if existing:
            return _indicator_payload(existing)

        indicator = IndicadorFinanceiro(**data)
        session.add(indicator)
        session.commit()
        session.refresh(indicator)
        return _indicator_payload(indicator)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if email == "admin" and password == ADMIN_PASSWORD:
            request.session.update({"admin_user": ADMIN_EMAIL})
            return True

        if email == "admin":
            email = ADMIN_EMAIL

        with Session(engine) as session:
            user = session.exec(
                select(User).where(
                    User.email == email,
                    User.senha == password,
                    User.is_admin == True,  # noqa: E712
                )
            ).first()

        if not user:
            return False

        request.session.update({"admin_user": email})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin_user"))


class TransactionAdmin(ModelView, model=Transaction):
    name = "transaction"
    name_plural = "transactions"
    icon = "fa-solid fa-wallet"
    column_list = [Transaction.id, Transaction.data, Transaction.descricao, Transaction.valor, Transaction.tipo, Transaction.categoria]
    column_searchable_list = [Transaction.descricao, Transaction.categoria, Transaction.tipo]
    column_sortable_list = [Transaction.id, Transaction.data, Transaction.valor, Transaction.categoria]
    page_size = 25
    can_export = True


class TransacaoAdmin(ModelView, model=Transaction):
    name = "transacao"
    name_plural = "transacoes"
    icon = "fa-solid fa-wallet"
    column_list = [Transaction.id, Transaction.data, Transaction.descricao, Transaction.valor, Transaction.tipo, Transaction.categoria]
    column_searchable_list = [Transaction.descricao, Transaction.categoria, Transaction.tipo]
    column_sortable_list = [Transaction.id, Transaction.data, Transaction.valor, Transaction.categoria]
    page_size = 25
    can_export = True


class GoalAdmin(ModelView, model=Goal):
    name = "goal"
    name_plural = "goals"
    icon = "fa-solid fa-bullseye"
    column_list = [Goal.id, Goal.nome, Goal.valor_objetivo, Goal.valor_atual, Goal.prazo, Goal.foto_url]
    column_searchable_list = [Goal.nome]
    column_sortable_list = [Goal.id, Goal.prazo, Goal.valor_objetivo]
    page_size = 25
    can_export = True


class MetaAdmin(ModelView, model=Goal):
    name = "meta"
    name_plural = "metas"
    icon = "fa-solid fa-bullseye"
    column_list = [Goal.id, Goal.nome, Goal.valor_objetivo, Goal.valor_atual, Goal.prazo, Goal.foto_url]
    column_searchable_list = [Goal.nome]
    column_sortable_list = [Goal.id, Goal.prazo, Goal.valor_objetivo]
    page_size = 25
    can_export = True


class UserAdmin(ModelView, model=User):
    name = "Usuario"
    name_plural = "Usuarios"
    icon = "fa-solid fa-users"
    column_list = [User.id, User.nome, User.email, User.is_admin, User.created_at]
    column_searchable_list = [User.nome, User.email]
    column_sortable_list = [User.id, User.email, User.created_at]
    page_size = 25


class IndicadorAdmin(ModelView, model=IndicadorFinanceiro):
    name = "Indicador financeiro"
    name_plural = "Indicadores financeiros"
    icon = "fa-solid fa-chart-line"
    column_list = [IndicadorFinanceiro.id, IndicadorFinanceiro.nome, IndicadorFinanceiro.valor, IndicadorFinanceiro.data_referencia, IndicadorFinanceiro.fonte]
    column_searchable_list = [IndicadorFinanceiro.nome, IndicadorFinanceiro.fonte]
    column_sortable_list = [IndicadorFinanceiro.id, IndicadorFinanceiro.nome, IndicadorFinanceiro.data_referencia, IndicadorFinanceiro.valor]
    page_size = 25
    can_export = True


class SuggestedCategoryAdmin(ModelView, model=SuggestedCategory):
    name = "Categoria sugerida"
    name_plural = "Categorias sugeridas"
    icon = "fa-solid fa-tags"
    column_list = [SuggestedCategory.id, SuggestedCategory.name, SuggestedCategory.monthly_limit, SuggestedCategory.description]
    column_searchable_list = [SuggestedCategory.name, SuggestedCategory.description]
    page_size = 25


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_seed()
    yield


app = FastAPI(title="FinUp API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

admin = Admin(
    app,
    engine,
    authentication_backend=AdminAuth(secret_key="finup-admin-dev-secret"),
    title="FinUp Admin",
)
admin.add_view(TransactionAdmin)
admin.add_view(TransacaoAdmin)
admin.add_view(GoalAdmin)
admin.add_view(MetaAdmin)
admin.add_view(UserAdmin)
admin.add_view(IndicadorAdmin)
admin.add_view(SuggestedCategoryAdmin)


@app.get("/health")
def health():
    return {"status": "ok"}


def _month_key(date_text: str):
    return date_text[:7] if date_text else "sem-data"


def _latest_indicators_by_name(session: Session):
    indicators = session.exec(select(IndicadorFinanceiro)).all()
    latest = {}
    for indicator in sorted(indicators, key=lambda item: (item.data_referencia, item.created_at)):
        latest[indicator.nome] = _indicator_payload(indicator)
    return latest


def _dashboard_data():
    with Session(engine) as session:
        transactions = session.exec(select(Transaction)).all()
        goals = session.exec(select(Goal)).all()
        indicators = _latest_indicators_by_name(session)

    receitas = [item for item in transactions if item.tipo == "receita"]
    despesas = [item for item in transactions if item.tipo == "despesa"]
    total_receitas = sum(item.valor for item in receitas)
    total_despesas = sum(item.valor for item in despesas)
    saldo = total_receitas - total_despesas
    economia = max(saldo, 0)
    score = max(0, min(100, int(50 + (economia / total_receitas * 50 if total_receitas else 0) - (10 if saldo < 0 else 0))))

    return {
        "transactions": transactions,
        "goals": goals,
        "indicators": indicators,
        "summary": {
            "saldo_atual": saldo,
            "total_receitas_mes": total_receitas,
            "total_despesas_mes": total_despesas,
            "economia_mes": economia,
            "quantidade_transacoes": len(transactions),
            "score_financeiro": score,
        },
    }


def _category_totals(transactions):
    totals = {}
    for item in transactions:
        if item.tipo != "despesa":
            continue
        totals[item.categoria] = totals.get(item.categoria, 0) + item.valor
    return dict(sorted(totals.items(), key=lambda pair: pair[1], reverse=True))


@app.get("/transactions")
def list_transactions():
    with Session(engine) as session:
        transactions = session.exec(select(Transaction)).all()
        return [
            {
                "id": item.id,
                "description": item.descricao,
                "category": item.categoria,
                "kind": "income" if item.tipo == "receita" else "expense",
                "amount": item.valor,
                "date": item.data,
                "created_at": item.created_at,
            }
            for item in transactions
        ]


@app.post("/transactions")
def create_transaction(transaction: Transaction):
    with Session(engine) as session:
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction


@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction: Transaction):
    with Session(engine) as session:
        existing = session.get(Transaction, transaction_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Transacao nao encontrada.")
        existing.data = transaction.data
        existing.descricao = transaction.descricao
        existing.categoria = transaction.categoria
        existing.tipo = transaction.tipo
        existing.valor = transaction.valor
        existing.origem_arquivo = transaction.origem_arquivo
        existing.hash_unico = transaction.hash_unico
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return {
            "id": existing.id,
            "description": existing.descricao,
            "category": existing.categoria,
            "kind": "income" if existing.tipo == "receita" else "expense",
            "amount": existing.valor,
            "date": existing.data,
            "created_at": existing.created_at,
        }


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    with Session(engine) as session:
        transaction = session.get(Transaction, transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacao nao encontrada.")
        session.delete(transaction)
        session.commit()
        return {"deleted": True, "id": transaction_id}


@app.get("/goals")
def list_goals():
    with Session(engine) as session:
        goals = session.exec(select(Goal)).all()
        return [
            {
                "id": item.id,
                "name": item.nome,
                "target_amount": item.valor_objetivo,
                "saved_amount": item.valor_atual,
                "deadline": item.prazo,
                "foto_url": item.foto_url,
                "created_at": item.created_at,
            }
            for item in goals
        ]


@app.post("/goals")
def create_goal(goal: Goal):
    with Session(engine) as session:
        session.add(goal)
        session.commit()
        session.refresh(goal)
        return {
            "id": goal.id,
            "name": goal.nome,
            "target_amount": goal.valor_objetivo,
            "saved_amount": goal.valor_atual,
            "deadline": goal.prazo,
            "foto_url": goal.foto_url,
            "created_at": goal.created_at,
        }


@app.put("/goals/{goal_id}")
def update_goal(goal_id: int, goal: Goal):
    with Session(engine) as session:
        existing = session.get(Goal, goal_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Meta nao encontrada.")
        existing.nome = goal.nome
        existing.valor_objetivo = goal.valor_objetivo
        existing.valor_atual = goal.valor_atual
        existing.prazo = goal.prazo
        existing.foto_url = goal.foto_url
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return {
            "id": existing.id,
            "name": existing.nome,
            "target_amount": existing.valor_objetivo,
            "saved_amount": existing.valor_atual,
            "deadline": existing.prazo,
            "foto_url": existing.foto_url,
            "created_at": existing.created_at,
        }


@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int):
    with Session(engine) as session:
        goal = session.get(Goal, goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Meta nao encontrada.")
        session.delete(goal)
        session.commit()
        return {"deleted": True, "id": goal_id}


@app.post("/metas/{goal_id}/foto")
async def upload_goal_photo(goal_id: int, foto: UploadFile = File(...)):
    extension = Path(foto.filename or "").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="Envie uma imagem jpg, jpeg, png ou webp.")

    with Session(engine) as session:
        goal = session.get(Goal, goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Meta nao encontrada.")

        file_name = f"meta-{goal_id}-{int(datetime.utcnow().timestamp())}{extension}"
        file_path = UPLOAD_DIR / file_name
        file_path.write_bytes(await foto.read())
        goal.foto_url = f"/uploads/metas/{file_name}"
        session.add(goal)
        session.commit()
        session.refresh(goal)
        return {
            "id": goal.id,
            "name": goal.nome,
            "target_amount": goal.valor_objetivo,
            "saved_amount": goal.valor_atual,
            "deadline": goal.prazo,
            "foto_url": goal.foto_url,
        }


@app.get("/suggested-categories")
def list_suggested_categories():
    with Session(engine) as session:
        return session.exec(select(SuggestedCategory)).all()


@app.post("/suggested-categories")
def create_suggested_category(category: SuggestedCategory):
    with Session(engine) as session:
        session.add(category)
        session.commit()
        session.refresh(category)
        return category


@app.put("/suggested-categories/{category_id}")
def update_suggested_category(category_id: int, category: SuggestedCategory):
    with Session(engine) as session:
        existing = session.get(SuggestedCategory, category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Categoria sugerida nao encontrada.")
        existing.name = category.name
        existing.monthly_limit = category.monthly_limit
        existing.description = category.description
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing


@app.delete("/suggested-categories/{category_id}")
def delete_suggested_category(category_id: int):
    with Session(engine) as session:
        existing = session.get(SuggestedCategory, category_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Categoria sugerida nao encontrada.")
        session.delete(existing)
        session.commit()
        return {"deleted": True, "id": category_id}


@app.get("/financeiro/dashboard", response_class=HTMLResponse)
def financial_dashboard(request: Request):
    return templates.TemplateResponse("financial_dashboard.html", {"request": request})


@app.get("/dashboard/resumo")
def dashboard_resumo():
    data = _dashboard_data()
    return {
        **data["summary"],
        "indicadores": data["indicators"],
    }


@app.get("/dashboard/gastos-por-categoria")
def dashboard_gastos_por_categoria():
    data = _dashboard_data()
    totals = _category_totals(data["transactions"])
    return {
        "labels": list(totals.keys()),
        "values": list(totals.values()),
    }


@app.get("/dashboard/receitas-despesas-mensais")
def dashboard_receitas_despesas_mensais():
    data = _dashboard_data()
    months = {}
    for item in data["transactions"]:
        month = _month_key(item.data)
        months.setdefault(month, {"receitas": 0, "despesas": 0})
        if item.tipo == "receita":
            months[month]["receitas"] += item.valor
        else:
            months[month]["despesas"] += item.valor

    ordered = dict(sorted(months.items()))
    return {
        "labels": list(ordered.keys()),
        "receitas": [value["receitas"] for value in ordered.values()],
        "despesas": [value["despesas"] for value in ordered.values()],
    }


@app.get("/dashboard/evolucao-saldo")
def dashboard_evolucao_saldo():
    data = _dashboard_data()
    balance = 0
    labels = []
    values = []
    for item in sorted(data["transactions"], key=lambda transaction: transaction.data):
        balance += item.valor if item.tipo == "receita" else -item.valor
        labels.append(item.data)
        values.append(balance)
    return {"labels": labels, "values": values}


@app.get("/dashboard/maiores-despesas")
def dashboard_maiores_despesas():
    data = _dashboard_data()
    totals = _category_totals(data["transactions"])
    top_items = list(totals.items())[:5]
    return {
        "labels": [item[0] for item in top_items],
        "values": [item[1] for item in top_items],
    }


@app.get("/dashboard/metas")
def dashboard_metas():
    data = _dashboard_data()
    return {
        "items": [
            {
                "nome": goal.nome,
                "valor_objetivo": goal.valor_objetivo,
                "valor_atual": goal.valor_atual,
                "percentual": round((goal.valor_atual / goal.valor_objetivo) * 100, 2) if goal.valor_objetivo else 0,
                "prazo": goal.prazo,
                "foto_url": goal.foto_url,
            }
            for goal in data["goals"]
        ]
    }


@app.get("/dashboard/score")
def dashboard_score():
    data = _dashboard_data()
    return {"score": data["summary"]["score_financeiro"]}


@app.get("/dashboard/insights")
def dashboard_insights():
    data = _dashboard_data()
    totals = _category_totals(data["transactions"])
    top_category = next(iter(totals.keys()), None)
    insights = []

    if top_category:
        insights.append(f"Sua maior categoria de gasto foi {top_category}.")
        insights.append(f"Voce gastou mais com {top_category.lower()} este mes.")
    if data["summary"]["saldo_atual"] >= 0:
        insights.append("Seu saldo mensal esta positivo.")
    else:
        insights.append("Seu saldo mensal esta negativo; revise despesas variaveis.")
    insights.append(f"Seu score financeiro atual e {data['summary']['score_financeiro']}/100.")

    if "selic" in data["indicators"]:
        insights.append("Com a Selic atual, investimentos de renda fixa podem estar mais atrativos.")
    if "ipca" in data["indicators"]:
        insights.append("A inflacao medida pelo IPCA impacta seu poder de compra.")

    return {"items": insights}


@app.get("/indicadores")
def list_indicadores():
    with Session(engine) as session:
        indicators = session.exec(select(IndicadorFinanceiro)).all()
        ordered_indicators = sorted(
            indicators,
            key=lambda indicator: (
                indicator.nome,
                indicator.data_referencia,
                indicator.created_at,
            ),
            reverse=True,
        )
        return {
            "total": len(ordered_indicators),
            "items": [_indicator_payload(indicator) for indicator in ordered_indicators],
        }


@app.get("/indicadores/dolar")
def get_dolar():
    return fetch_and_store_indicator("dolar")


@app.get("/indicadores/euro")
def get_euro():
    return fetch_and_store_indicator("euro")


@app.get("/indicadores/selic")
def get_selic():
    return fetch_and_store_indicator("selic")


@app.get("/indicadores/ipca")
def get_ipca():
    return fetch_and_store_indicator("ipca")


@app.get("/indicadores/cdi")
def get_cdi():
    return fetch_and_store_indicator("cdi")
