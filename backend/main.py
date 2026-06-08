from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    category: str
    kind: str = "expense"
    amount: float
    date: str
    notes: str = ""


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target_amount: float
    saved_amount: float = 0
    deadline: str
    priority: str = "media"


class SuggestedCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    monthly_limit: float
    description: str


engine = create_engine("sqlite:///finup.db")


def create_db_and_seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing_transaction = session.exec(select(Transaction)).first()
        if existing_transaction:
            return

        session.add_all(
            [
                Transaction(
                    description="Salario",
                    category="Receita fixa",
                    kind="income",
                    amount=4200,
                    date="2026-06-05",
                ),
                Transaction(
                    description="Restaurantes e delivery",
                    category="Alimentacao",
                    kind="expense",
                    amount=620,
                    date="2026-06-08",
                    notes="Categoria com gasto acima do ideal na semana.",
                ),
                Transaction(
                    description="Compras do mercado",
                    category="Casa",
                    kind="expense",
                    amount=480,
                    date="2026-06-06",
                ),
            ]
        )
        session.add_all(
            [
                Goal(
                    name="Viagem para praia",
                    target_amount=2800,
                    saved_amount=1280,
                    deadline="2026-12-20",
                    priority="alta",
                ),
                Goal(
                    name="Reserva de emergencia",
                    target_amount=6000,
                    saved_amount=2100,
                    deadline="2027-03-01",
                    priority="alta",
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
        session.commit()


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/transactions")
def list_transactions():
    with Session(engine) as session:
        return session.exec(select(Transaction)).all()


@app.post("/transactions")
def create_transaction(transaction: Transaction):
    with Session(engine) as session:
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction


@app.get("/goals")
def list_goals():
    with Session(engine) as session:
        return session.exec(select(Goal)).all()


@app.post("/goals")
def create_goal(goal: Goal):
    with Session(engine) as session:
        session.add(goal)
        session.commit()
        session.refresh(goal)
        return goal


@app.get("/suggested-categories")
def list_suggested_categories():
    with Session(engine) as session:
        return session.exec(select(SuggestedCategory)).all()
