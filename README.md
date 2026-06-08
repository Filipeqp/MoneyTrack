# FlowUp - Sistema de Gerencia de Projetos

FlowUp e uma aplicacao para organizar projetos, tarefas, custos, prazos e riscos em um painel unico. A ideia e atender alunos, freelancers e pequenas equipes que precisam acompanhar entregas sem usar ferramentas grandes demais.

## Ideia do Produto

O sistema permite cadastrar projetos, definir responsaveis, controlar tarefas, acompanhar percentual de conclusao, registrar custos e visualizar riscos. Para uma apresentacao academica, ele mostra bem os conceitos de escopo, cronograma, custo, risco e acompanhamento.

## Onde Pode Ser Usado

- Trabalhos de faculdade com equipes e entregas por etapa.
- Pequenos projetos de software, design ou consultoria.
- Controle de freelas, clientes, prazos e orcamentos.
- Base para portfolio pessoal, mostrando frontend, backend e banco de dados.

## Stack Recomendada

- Frontend: React + Vite.
- Backend: Python + FastAPI.
- Banco de dados: SQLite no inicio, PostgreSQL quando o projeto crescer.
- API: REST, com endpoints para projetos, tarefas, custos e riscos.

Python faz sentido para este trabalho porque FastAPI e simples, moderno, tem documentacao automatica em `/docs` e combina bem com banco via SQLModel. C# tambem e excelente, principalmente com ASP.NET Core, mas exige mais estrutura inicial.

## Estrutura

```text
.
├── src/                 # Frontend React
├── backend/             # API FastAPI
│   ├── main.py
│   └── requirements.txt
├── package.json
└── README.md
```

## Rodar o Frontend

```bash
npm install
npm run dev
```

O Vite normalmente abre em `http://localhost:5173`.

## Rodar o Backend

Instale o Python pelo site oficial ou pela Microsoft Store, depois rode:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API:

- `GET /health`
- `GET /projects`
- `POST /projects`
- `GET /tasks`
- `POST /tasks`
- Documentacao automatica: `http://localhost:8000/docs`

## Proximos Passos

- Conectar o React ao backend usando `fetch`.
- Criar telas de cadastro e edicao de projetos.
- Criar tabela de custos por categoria.
- Criar matriz de riscos com impacto e probabilidade.
- Adicionar login simples para usuario e equipe.
- Gerar relatorio PDF do projeto para entrega final.
