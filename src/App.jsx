import './App.css'

const projects = [
  {
    name: 'App de controle financeiro',
    client: 'Equipe Alfa',
    progress: 72,
    budget: 'R$ 3.450',
    due: '18 jun',
    status: 'Em execucao',
  },
  {
    name: 'Portal de eventos academicos',
    client: 'Faculdade',
    progress: 48,
    budget: 'R$ 1.920',
    due: '25 jun',
    status: 'Atencao',
  },
  {
    name: 'Dashboard comercial',
    client: 'Freela',
    progress: 91,
    budget: 'R$ 5.700',
    due: '10 jun',
    status: 'Finalizando',
  },
]

const tasks = [
  ['Integrar login com API', 'Hoje', 'Backend'],
  ['Validar regras do banco', 'Amanha', 'Banco'],
  ['Preparar demo para professor', '14 jun', 'Entrega'],
  ['Revisar custos planejados', '16 jun', 'Gestao'],
]

const risks = [
  { label: 'Atraso de escopo', value: 'medio' },
  { label: 'Custo acima do planejado', value: 'baixo' },
  { label: 'Dependencia externa', value: 'alto' },
]

function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">F</span>
          <div>
            <strong>FlowUp</strong>
            <small>project hub</small>
          </div>
        </div>

        <nav className="nav-list" aria-label="Principal">
          <a className="active" href="#dashboard">Dashboard</a>
          <a href="#projects">Projetos</a>
          <a href="#tasks">Tarefas</a>
          <a href="#finance">Custos</a>
          <a href="#risks">Riscos</a>
        </nav>

        <div className="profile-box">
          <span>Plano do trabalho</span>
          <strong>React + FastAPI + SQLite</strong>
          <small>Simples para apresentar, forte para evoluir.</small>
        </div>
      </aside>

      <section className="workspace" id="dashboard">
        <header className="topbar">
          <div>
            <span className="eyebrow">Gerencia de projetos</span>
            <h1>Controle projetos, custos e entregas em um so lugar.</h1>
          </div>
          <button type="button">Novo projeto</button>
        </header>

        <section className="hero-panel" aria-label="Resumo executivo">
          <div>
            <p className="hero-kicker">Produto proposto</p>
            <h2>Um sistema util para faculdade, freelas e pequenas equipes.</h2>
            <p>
              O FlowUp organiza escopo, prazos, responsaveis, custos e riscos.
              No backend, cada acao vira dado salvo no banco para gerar historico,
              relatorios e indicadores do projeto.
            </p>
          </div>
          <div className="hero-metrics">
            <div>
              <span>Projetos ativos</span>
              <strong>12</strong>
            </div>
            <div>
              <span>Entrega media</span>
              <strong>84%</strong>
            </div>
            <div>
              <span>Orcamento usado</span>
              <strong>R$ 11k</strong>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel wide" id="projects">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Portfolio</span>
                <h3>Projetos em andamento</h3>
              </div>
              <button className="ghost" type="button">Filtrar</button>
            </div>

            <div className="project-list">
              {projects.map((project) => (
                <article className="project-row" key={project.name}>
                  <div>
                    <strong>{project.name}</strong>
                    <span>{project.client} - prazo {project.due}</span>
                  </div>
                  <div className="progress-track" aria-label={`${project.progress}% concluido`}>
                    <span style={{ width: `${project.progress}%` }} />
                  </div>
                  <span className="budget">{project.budget}</span>
                  <span className={`status ${project.status === 'Atencao' ? 'warning' : ''}`}>
                    {project.status}
                  </span>
                </article>
              ))}
            </div>
          </div>

          <div className="panel" id="tasks">
            <span className="eyebrow">Proximas acoes</span>
            <h3>Tarefas</h3>
            <div className="task-list">
              {tasks.map(([title, date, area]) => (
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

          <div className="panel" id="finance">
            <span className="eyebrow">Financeiro</span>
            <h3>Custos planejados</h3>
            <div className="donut" aria-label="67% do orcamento utilizado">
              <strong>67%</strong>
              <span>utilizado</span>
            </div>
            <p className="panel-note">
              No banco, os lancamentos podem guardar categoria, valor, data,
              projeto e comprovante.
            </p>
          </div>

          <div className="panel wide" id="risks">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">Matriz</span>
                <h3>Riscos monitorados</h3>
              </div>
              <button className="ghost" type="button">Adicionar risco</button>
            </div>
            <div className="risk-grid">
              {risks.map((risk) => (
                <div className="risk-card" key={risk.label}>
                  <span>{risk.label}</span>
                  <strong>{risk.value}</strong>
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
