# MoneyTrack - Controle Financeiro Pessoal

Aplicação para controlar suas finanças pessoais, acompanhar gastos, criar metas e entender para onde seu dinheiro está indo.

## ⚡ Quick Start - Rodar o programa

### Pré-requisitos

- **Node.js** (v18+): [https://nodejs.org/](https://nodejs.org/)
- **Python** (v3.9+): [https://www.python.org/](https://www.python.org/)

### 1. Clone ou baixe o projeto

```bash
cd "caminho/para/MoneyTrack"
```

### 2. Inicie o Backend (Python)

Abra um terminal na pasta `backend`:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

✅ Backend rodando em: `http://127.0.0.1:8000`

### 3. Inicie o Frontend (React)

Abra outro terminal na raiz do projeto:

```bash
npm install
npm run dev
```

✅ Frontend rodando em: `http://localhost:5173` (ou `http://localhost:5174` se a porta estiver ocupada)

### 4. Pronto! Acesse a aplicação

Abra o navegador em: **`http://localhost:5173`** (ou `5174`)

---

## 📱 O que você pode fazer

- **Adicionar gastos**: Registre tudo que você gasta no mês (alimentação, transporte, lazer, etc.)
- **Criar metas**: Defina objetivos (viagem, reserva de emergência, compra de notebook, etc.)
- **Ver resumo financeiro**: Dashboard mostrando saldo, receitas, despesas e progresso das metas
- **Gerenciar categorias**: Customize as categorias de gastos
- **Acompanhar indicadores**: Consulte cotações de dólar, euro, Selic, IPCA e CDI direto do Banco Central

---

## 📚 Funcionalidades

### Abas principais

- **Início**: Resumo rápido do seu dinheiro
- **Meu Histórico**: Lista de todos os gastos registrados (editar ou deletar)
- **Gastos Fixos**: Gastos comuns do dia a dia para adicionar rapidamente
- **Metas**: Criar e acompanhar metas financeiras com fotos
- **Dashboard**: Gráficos e análise de gastos por categoria
- **Indicadores**: Cotações econômicas (dólar, euro, Selic, IPCA, CDI)

### Dados

Todos os dados são salvos em um banco de dados SQLite local. Nenhuma informação é enviada para servidores externos (exceto consulta de cotações ao Banco Central).

---

## 🛠️ Tecnologias

- **Frontend**: React 19 + Vite + Chart.js
- **Backend**: Python + FastAPI + SQLModel
- **Banco de dados**: SQLite
- **APIs externas**: Banco Central do Brasil (cotações)

---

## 📖 Documentação da API

Quando o backend está rodando, acesse a documentação interativa em:

**`http://127.0.0.1:8000/docs`**

Lá você pode testar todos os endpoints (transações, metas, categorias, indicadores, etc.)

---

## 👨‍💻 Desenvolvimento

## 📊 Endpoints da API

Lista completa de endpoints disponíveis:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status do backend |
| GET | `/transactions` | Listar gastos |
| POST | `/transactions` | Criar gasto |
| PUT | `/transactions/{id}` | Editar gasto |
| DELETE | `/transactions/{id}` | Deletar gasto |
| GET | `/goals` | Listar metas |
| POST | `/goals` | Criar meta |
| PUT | `/goals/{id}` | Editar meta |
| DELETE | `/goals/{id}` | Deletar meta |
| POST | `/metas/{id}/foto` | Upload de foto para meta |
| GET | `/suggested-categories` | Listar categorias sugeridas |
| POST | `/suggested-categories` | Criar categoria |
| GET | `/indicadores` | Listar indicadores salvos |
| GET | `/indicadores/dolar` | Cotação do dólar atual |
| GET | `/indicadores/euro` | Cotação do euro atual |
| GET | `/indicadores/selic` | Taxa Selic atual |
| GET | `/indicadores/ipca` | Inflação (IPCA) atual |
| GET | `/indicadores/cdi` | Taxa CDI atual |
| GET | `/dashboard/resumo` | Resumo financeiro |
| GET | `/dashboard/gastos-por-categoria` | Gastos agrupados por categoria |
| GET | `/dashboard/receitas-despesas-mensais` | Comparativo mensal |
| GET | `/dashboard/evolucao-saldo` | Evolução do saldo |
| GET | `/dashboard/maiores-despesas` | Top 5 maiores gastos |
| GET | `/dashboard/metas` | Progresso das metas |
| GET | `/dashboard/score` | Score financeiro |

---

## 🚀 Desenvolvendo

### Estrutura do projeto

```
MoneyTrack/
├── src/                      # Frontend React
│   ├── App.jsx
│   ├── FinanceDashboard.jsx
│   ├── App.css
│   └── assets/
├── backend/                  # API Python/FastAPI
│   ├── main.py
│   ├── requirements.txt
│   └── services/
│       └── public_finance_api.py
├── public/                   # Arquivos estáticos
├── package.json              # Dependências do frontend
├── vite.config.js            # Configuração do Vite
└── eslint.config.js          # Linter do JS
```

### Variáveis de ambiente

Não são necessárias para o desenvolvimento local. O banco de dados SQLite é criado automaticamente.

### Como contribuir

1. Clone o repositório
2. Crie uma branch para sua feature: `git checkout -b minha-feature`
3. Faça suas alterações
4. Teste localmente rodando frontend e backend
5. Commit e push: `git push origin minha-feature`
6. Abra um Pull Request

---

## 📝 Licença

Este projeto é de código aberto e pode ser usado livremente.

---

## 💡 Ideias futuras

- Autenticação de usuários (login/senha ou Google)
- Gráficos mais avançados e exportação de relatórios
- Integração com contas bancárias
- Recomendações com IA
- App mobile (React Native)
