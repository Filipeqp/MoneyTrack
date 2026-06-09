# FinUp - Controle Financeiro Pessoal

FinUp e uma aplicacao de controle financeiro pessoal para ajudar uma pessoa a entender quanto ganha, quanto gasta, onde o dinheiro esta indo e como transformar objetivos em metas reais.

## Ideia do Produto

O sistema permite cadastrar receitas, gastos, categorias, metas e objetivos financeiros. A pessoa pode acompanhar o saldo do mes, registrar gastos do dia a dia, definir limites por categoria e criar planos para guardar dinheiro.

Exemplos de objetivos:

- Fazer uma viagem.
- Montar uma reserva de emergencia.
- Comprar um notebook, celular, moto ou carro.
- Guardar dinheiro para curso, faculdade ou certificacao.
- Reduzir gastos com restaurante, delivery, compras e assinaturas.

## Diferencial

A aplicacao nao precisa ser apenas uma lista de gastos. Ela pode sugerir categorias, recomendar limites mensais e mostrar acoes praticas, como:

- "Seu gasto com restaurante esta alto esta semana."
- "Se guardar R$ 350 por mes, sua viagem fica pronta em 8 meses."
- "Voce pode reduzir assinaturas para acelerar sua reserva."
- "Sua meta principal deveria ser reserva de emergencia antes de compras grandes."

Mais para frente, o projeto pode integrar IA para entender o perfil da pessoa e montar recomendacoes personalizadas.

## Onde Pode Ser Usado

- Controle financeiro pessoal.
- Organizacao de salario, renda extra e gastos mensais.
- Planejamento de viagem e compras.
- Educacao financeira para jovens.
- Portfolio pessoal, mostrando frontend, backend, banco de dados e possibilidade de IA.

## Funcionalidades Planejadas

- Cadastro de receitas: salario, freelas, mesada, renda extra.
- Cadastro de despesas: restaurante, mercado, transporte, lazer, compras, contas e assinaturas.
- Categorias sugeridas para facilitar o uso.
- Limite mensal por categoria.
- Metas de guardar dinheiro.
- Objetivos com prazo e valor alvo.
- Dashboard com saldo, entradas, saidas e percentual da meta.
- Historico mensal.
- Alertas de gasto alto.
- Futuramente: recomendacoes com IA.

## Stack Recomendada

- Frontend: React + Vite.
- Backend: Python + FastAPI.
- Banco de dados: SQLite no inicio, PostgreSQL quando crescer.
- API: REST, com endpoints para transacoes, metas e categorias.

Python e uma boa escolha para este trabalho porque FastAPI e simples, moderno, rapido de aprender e gera documentacao automatica em `/docs`. C# tambem seria uma boa opcao com ASP.NET Core, mas Python tende a ser mais direto para comecar.

## Estrutura

```text
.
|-- src/                 # Frontend React
|-- backend/             # API FastAPI
|   |-- main.py
|   `-- requirements.txt
|-- package.json
`-- README.md
```

## Rodar o Frontend

```bash
npm install
npm run dev
```

O Vite normalmente abre em `http://localhost:5173`.

Dentro do app React, use a opcao `Dashboard` na sidebar para ver o painel financeiro integrado ao layout principal.

## Rodar o Backend

Instale o Python pelo site oficial ou pela Microsoft Store, depois rode:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

API:

- `GET /health`
- `GET /transactions`
- `POST /transactions`
- `DELETE /transactions/{id}`
- `GET /goals`
- `POST /goals`
- `POST /metas/{id}/foto`
- `GET /suggested-categories`
- `PUT /suggested-categories/{id}`
- `GET /indicadores`
- `GET /indicadores/dolar`
- `GET /indicadores/euro`
- `GET /indicadores/selic`
- `GET /indicadores/ipca`
- `GET /indicadores/cdi`
- Documentacao automatica: `http://localhost:8000/docs`

Painel administrativo:

- URL: `http://localhost:8000/admin`
- Usuario inicial: `admin@finup.local`
- Atalho de usuario: `admin`
- Senha inicial: `admin123`

Dashboard financeiro server-side:

- URL: `http://localhost:8000/financeiro/dashboard`
- Usa Bootstrap 5 e Chart.js via CDN.

Endpoints internos dos graficos:

- `GET /dashboard/resumo`
- `GET /dashboard/gastos-por-categoria`
- `GET /dashboard/receitas-despesas-mensais`
- `GET /dashboard/evolucao-saldo`
- `GET /dashboard/maiores-despesas`
- `GET /dashboard/metas`
- `GET /dashboard/score`
- `GET /dashboard/insights`

Os indicadores usam APIs publicas gratuitas:

- Banco Central do Brasil PTAX para dolar e euro.
- Banco Central do Brasil SGS para Selic, IPCA e CDI.

Cada consulta salva o resultado na tabela SQLite `indicadores_financeiros`, evitando duplicar o mesmo indicador na mesma data de referencia. Se a API publica estiver fora do ar, o backend tenta retornar o ultimo valor salvo com `stale: true`.

## Ideias Para Evoluir

- Conectar o React ao backend usando `fetch`.
- Criar formulario para adicionar gasto ou receita.
- Criar tela de metas com prazo e valor mensal recomendado.
- Criar graficos por categoria.
- Criar login para cada usuario ter seus proprios dados.
- Integrar IA para analisar perfil financeiro e sugerir planos.
- Gerar relatorio mensal em PDF.
