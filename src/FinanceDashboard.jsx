import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  Doughnut,
  Line,
} from 'react-chartjs-2'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
  ArcElement,
} from 'chart.js'

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
)

const API_BASE_URL = 'http://127.0.0.1:8000'
const chartColors = ['#bdf234', '#11130f', '#7f8f68', '#d9ff59', '#98b91e', '#d5ddcb']

const money = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

const percent = new Intl.NumberFormat('pt-BR', {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
})

async function getJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) throw new Error('Nao foi possivel carregar o dashboard.')
  return response.json()
}

export default function FinanceDashboard({ refreshKey = 0 }) {
  const [data, setData] = useState(null)
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          resumo,
          categorias,
          mensal,
          saldo,
          maiores,
          metas,
          insights,
        ] = await Promise.all([
          getJson('/dashboard/resumo'),
          getJson('/dashboard/gastos-por-categoria'),
          getJson('/dashboard/receitas-despesas-mensais'),
          getJson('/dashboard/evolucao-saldo'),
          getJson('/dashboard/maiores-despesas'),
          getJson('/dashboard/metas'),
          getJson('/dashboard/insights'),
        ])
        setData({ resumo, categorias, mensal, saldo, maiores, metas, insights })
        setStatus('ready')
      } catch {
        setStatus('error')
      }
    }

    loadDashboard()
  }, [refreshKey])

  if (status === 'loading') {
    return <div className="panel wide">Carregando dashboard financeiro...</div>
  }

  if (status === 'error') {
    return (
      <div className="panel wide">
        <span className="eyebrow">Backend offline</span>
        <h3>Nao foi possivel carregar os graficos</h3>
        <p className="panel-note">Verifique se o FastAPI esta rodando em http://127.0.0.1:8000.</p>
      </div>
    )
  }

  const summaryCards = [
    ['Saldo atual', money.format(data.resumo.saldo_atual)],
    ['Receitas do mes', money.format(data.resumo.total_receitas_mes)],
    ['Despesas do mes', money.format(data.resumo.total_despesas_mes)],
    ['Economia do mes', money.format(data.resumo.economia_mes)],
    ['Transacoes', data.resumo.quantidade_transacoes],
    ['Score', `${data.resumo.score_financeiro}/100`],
  ]

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  }

  return (
    <section className="dashboard-page">
      <div className="metric-grid">
        {summaryCards.map(([label, value]) => (
          <article className="metric-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>

      {/* Indicadores públicos removidos daqui — agora disponíveis apenas na aba Indicadores */}

      <div className="chart-grid">
        <div className="panel">
          <span className="eyebrow">Categorias</span>
          <h3>Gastos por categoria</h3>
          <div className="chart-frame">
            <Doughnut
              data={{
                labels: data.categorias.labels,
                datasets: [{ data: data.categorias.values, backgroundColor: chartColors }],
              }}
              options={chartOptions}
            />
          </div>
        </div>

        <div className="panel">
          <span className="eyebrow">Mensal</span>
          <h3>Receitas x despesas</h3>
          <div className="chart-frame">
            <Bar
              data={{
                labels: data.mensal.labels,
                datasets: [
                  { label: 'Receitas', data: data.mensal.receitas, backgroundColor: '#bdf234' },
                  { label: 'Despesas', data: data.mensal.despesas, backgroundColor: '#11130f' },
                ],
              }}
              options={chartOptions}
            />
          </div>
        </div>

        <div className="panel">
          <span className="eyebrow">Saldo</span>
          <h3>Evolucao do saldo</h3>
          <div className="chart-frame">
            <Line
              data={{
                labels: data.saldo.labels,
                datasets: [{
                  label: 'Saldo',
                  data: data.saldo.values,
                  borderColor: '#11130f',
                  backgroundColor: 'rgba(189, 242, 52, 0.25)',
                  fill: true,
                  tension: 0.35,
                }],
              }}
              options={chartOptions}
            />
          </div>
        </div>

        <div className="panel">
          <span className="eyebrow">Despesas</span>
          <h3>Maiores categorias</h3>
          <div className="chart-frame">
            <Bar
              data={{
                labels: data.maiores.labels,
                datasets: [{ label: 'Valor', data: data.maiores.values, backgroundColor: '#bdf234' }],
              }}
              options={{ ...chartOptions, indexAxis: 'y' }}
            />
          </div>
        </div>
      </div>

      <div className="content-grid">
        <div className="panel">
          <span className="eyebrow">Metas</span>
          <h3>Progresso financeiro</h3>
          <div className="goal-progress-list">
            {data.metas.items.map((goal) => (
              <div className="goal-progress" key={goal.nome}>
                <div>
                  <strong>{goal.nome}</strong>
                  <span>{percent.format(goal.percentual)}%</span>
                </div>
                <div className="progress-track">
                  <span style={{ width: `${Math.min(goal.percentual, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <span className="eyebrow">Carteira inteligente</span>
          <h3>Insights</h3>
          <div className="insight-list vertical">
            {data.insights.items.map((item) => <p key={item}>{item}</p>)}
          </div>
        </div>
      </div>
    </section>
  )
}
