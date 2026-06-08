from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    client: str
    status: str = "Em execucao"
    progress: int = 0
    budget: float = 0
    due_date: str


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    area: str
    due_date: str
    done: bool = False
    project_id: int = Field(foreign_key="project.id")


engine = create_engine("sqlite:///flowup.db")


def create_db_and_seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        existing_project = session.exec(select(Project)).first()
        if existing_project:
            return

        project = Project(
            name="App de controle financeiro",
            client="Equipe Alfa",
            status="Em execucao",
            progress=72,
            budget=3450,
            due_date="2026-06-18",
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        session.add_all(
            [
                Task(
                    title="Integrar login com API",
                    area="Backend",
                    due_date="2026-06-08",
                    project_id=project.id,
                ),
                Task(
                    title="Preparar demo para professor",
                    area="Entrega",
                    due_date="2026-06-14",
                    project_id=project.id,
                ),
            ]
        )
        session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_seed()
    yield


app = FastAPI(title="FlowUp API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/projects")
def list_projects():
    with Session(engine) as session:
        return session.exec(select(Project)).all()


@app.post("/projects")
def create_project(project: Project):
    with Session(engine) as session:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project


@app.get("/tasks")
def list_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()


@app.post("/tasks")
def create_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
