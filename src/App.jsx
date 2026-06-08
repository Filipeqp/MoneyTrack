import './App.css'

const transactions = [
  {
    name: 'Salario',
    category: 'Receita fixa',
    progress: 100,
    amount: '+ R$ 4.200',
    date: '05 jun',
    status: 'Recebido',
  },
  {
    name: 'Restaurantes e delivery',
    category: 'Alimentacao',
    progress: 78,
    amount: '- R$ 620',
    date: 'mes atual',
    status: 'Atenção',
  },
  {
    name: 'Compras do mercado',
    category: 'Casa',
    progress: 52,
    amount: '- R$ 480',
    date: 'mes atual',
    status: 'No limite',
  },
]

const habits = [
  ['Cadastrar gastos do dia', 'Hoje', 'Rotina'],
  ['Separar dinheiro da meta', 'Amanha', 'Reserva'],
  ['Revisar restaurantes da semana', 'Sexta', 'Analise'],
  ['Planejar gasto da viagem', 'Domingo', 'Objetivo'],
]

const goals = [
  { label: 'Viagem para praia', value: 'R$ 2.800' },
  { label: 'Reserva de emergencia', value: 'R$ 6.000' },
  { label: 'Notebook novo', value: 'R$ 4.500' },
]

function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">F</span>
          <div>
            <strong>FinUp</strong>
            <small>personal money</small>
          </div>
        </div>

        <nav className="nav-list" aria-label="Principal">
          <a className="active" href="#dashboard">Dashboard</a>
          <a href="#wallet">Carteira</a>
          <a href="#habits">Rotina</a>
          <a href="#budget">Orcamento</a>
          <a href="#goals">Metas</a>
        </nav>

        <div className="profile-box">
          <span>Plano do trabalho</span>
          <strong>React + FastAPI + SQLite</strong>
          <small>Base pronta para evoluir com IA financeira depois.</small>
        </div>
      </aside>

      <section className="workspace" id="dashboard">
        <header className="topbar">
          <div>
            <span className="eyebrow">Controle financeiro pessoal</span>
            <h1>Entenda seu dinheiro e transforme planos em metas reais.</h1>
          </div>
          <button type="button">Novo gasto</button>
        </header>

        <section className="hero-panel" aria-label="Resumo financeiro">
          <div>
            <p className="hero-kicker">Produto proposto</p>
            <h2>Um app para controlar entradas, saidas, sonhos e habitos.</h2>
            <p>
              O FinUp registra quanto a pessoa ganha, onde ela gasta, quanto
              consegue guardar e quais objetivos quer realizar, como viagem,
              reserva de emergencia, curso, carro ou compra importante.
            </p>
          </div>
          <div className="hero-metrics">
            <div>
              <span>Saldo do mes</span>
              <strong>R$ 1.340</strong>
            </div>
            <div>
              <span>Meta guardada</span>
              <strong>64%</strong>
            </div>
            <div>
              <span>Gastos variaveis</span>
              <strong>R$ 1.870</strong>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel wide" id="wallet">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Carteira</span>
                <h3>Movimentacoes do mes</h3>
              </div>
              <button className="ghost" type="button">Filtrar</button>
            </div>

            <div className="project-list">
              {transactions.map((transaction) => (
                <article className="project-row" key={transaction.name}>
                  <div>
                    <strong>{transaction.name}</strong>
                    <span>{transaction.category} - {transaction.date}</span>
                  </div>
                  <div className="progress-track" aria-label={`${transaction.progress}% do limite`}>
                    <span style={{ width: `${transaction.progress}%` }} />
                  </div>
                  <span className={`budget ${transaction.amount.startsWith('+') ? 'income' : ''}`}>
                    {transaction.amount}
                  </span>
                  <span className={`status ${transaction.status === 'Atenção' ? 'warning' : ''}`}>
                    {transaction.status}
                  </span>
                </article>
              ))}
            </div>
          </div>

          <div className="panel" id="habits">
            <span className="eyebrow">Rotina inteligente</span>
            <h3>Acoes sugeridas</h3>
            <div className="task-list">
              {habits.map(([title, date, area]) => (
                <label className="task-item" key={title}>
                  <input type="checkbox" />
                  <span>
                    <strong>{title}</strong>
                    <small>{area} - {date}</small>
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="panel" id="budget">
            <span className="eyebrow">Orcamento</span>
            <h3>Meta de guardar</h3>
            <div className="donut" aria-label="64% da meta mensal guardada">
              <strong>64%</strong>
              <span>guardado</span>
            </div>
            <p className="panel-note">
              O sistema pode sugerir limites por categoria: restaurante,
              transporte, mercado, lazer, assinaturas, estudos e compras.
            </p>
          </div>

          <div className="panel wide" id="goals">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Objetivos</span>
                <h3>Metas financeiras</h3>
              </div>
              <button className="ghost" type="button">Criar meta</button>
            </div>
            <div className="risk-grid">
              {goals.map((goal) => (
                <div className="risk-card" key={goal.label}>
                  <span>{goal.label}</span>
                  <strong>{goal.value}</strong>
                </div>
              ))}
            </div>
          </div>
        </section>
      </section>
    </main>
  )
}

export default App
