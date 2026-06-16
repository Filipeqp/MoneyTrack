import { useEffect, useMemo, useState } from 'react'
import FinanceDashboard from './FinanceDashboard.jsx'
import './App.css'

const money = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

const number = new Intl.NumberFormat('pt-BR', {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
})

const indicatorLabels = {
  dolar: 'Dolar atual',
  euro: 'Euro atual',
  selic: 'Selic',
  ipca: 'IPCA',
  cdi: 'CDI / juros',
}

const API_BASE_URL = 'http://127.0.0.1:8000'
const INDICATOR_KEYS = ['dolar', 'euro', 'selic', 'ipca', 'cdi']

const initialExpenses = [
  { id: 1, name: 'Restaurantes e delivery', category: 'Alimentacao', amount: 620, date: '2026-06-08' },
  { id: 2, name: 'Compras do mercado', category: 'Casa', amount: 480, date: '2026-06-06' },
  { id: 3, name: 'Transporte por app', category: 'Transporte', amount: 210, date: '2026-06-04' },
  { id: 4, name: 'Streaming e apps', category: 'Assinaturas', amount: 96, date: '2026-06-02' },
]

const defaultSuggestedExpenses = [
  { id: 1, name: 'Mercado', category: 'Casa', amount: 80 },
  { id: 2, name: 'Restaurante', category: 'Alimentacao', amount: 35 },
  { id: 3, name: 'Uber / transporte', category: 'Transporte', amount: 20 },
  { id: 4, name: 'Farmacia', category: 'Saude', amount: 60 },
  { id: 5, name: 'Cinema / lazer', category: 'Lazer', amount: 70 },
  { id: 6, name: 'Curso ou livro', category: 'Estudos', amount: 120 },
]

const initialGoals = [
  { id: 1, name: 'Viagem para praia', target: 2800, saved: 1280, monthly: 350, photoUrl: '' },
  { id: 2, name: 'Reserva de emergencia', target: 6000, saved: 2100, monthly: 500, photoUrl: '' },
  { id: 3, name: 'Notebook novo', target: 4500, saved: 900, monthly: 300, photoUrl: '' },
]

const screens = {
  home: 'Inicio',
  wallet: 'Meu Histórico',
  habits: 'Gastos Fixos',
  goals: 'Metas',
  financeDashboard: 'Dashboard',
  indicators: 'Indicadores',
}

const defaultCategories = ['Alimentacao', 'Casa', 'Transporte', 'Lazer', 'Saude', 'Estudos', 'Assinaturas']

function monthsToGoal(goal, extraExpense = 0) {
  const remaining = Math.max(goal.target - goal.saved, 0)
  const monthlyPower = Math.max(goal.monthly, 1)
  const baseMonths = Math.ceil(remaining / monthlyPower)
  const impactedMonths = Math.ceil((remaining + extraExpense) / monthlyPower)
  return { baseMonths, delay: Math.max(impactedMonths - baseMonths, 0) }
}

function App() {
  const [activeScreen, setActiveScreen] = useState('home')
  const [salary, setSalary] = useState(4200)
  const [salaryTransactionId, setSalaryTransactionId] = useState(null)
  const [expenses, setExpenses] = useState(initialExpenses)
  const [goals, setGoals] = useState(initialGoals)
  const [suggestions, setSuggestions] = useState(() => {
    const saved = localStorage.getItem('finup-suggestions')
    return saved ? JSON.parse(saved) : defaultSuggestedExpenses
  })
  const [categories, setCategories] = useState(() => {
    try {
      const saved = localStorage.getItem('finup-categories')
      return saved ? JSON.parse(saved) : defaultCategories
    } catch {
      return defaultCategories
    }
  })
  const [editingExpenseId, setEditingExpenseId] = useState(null)
  const [editingExpenseForm, setEditingExpenseForm] = useState({ name: '', category: '', amount: '' })
  const [editingSuggestionId, setEditingSuggestionId] = useState(null)
  const [editingGoalId, setEditingGoalId] = useState(null)
  const [toast, setToast] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [expenseForm, setExpenseForm] = useState({
    name: '',
    category: 'Alimentacao',
    amount: '',
    date: '2026-06-08',
  })
  const [suggestionForm, setSuggestionForm] = useState({
    name: '',
    category: 'Geral',
    amount: '',
  })
  const [goalForm, setGoalForm] = useState({
    name: '',
    target: '',
    saved: '',
    monthly: '',
  })
  const [lastExpense, setLastExpense] = useState(null)
  const [indicators, setIndicators] = useState({})
  const [indicatorStatus, setIndicatorStatus] = useState('loading')

  async function loadFinanceData() {
    try {
      const [transactionsResponse, goalsResponse, suggestionsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/transactions`),
        fetch(`${API_BASE_URL}/goals`),
        fetch(`${API_BASE_URL}/suggested-categories`),
      ])
      if (!transactionsResponse.ok || !goalsResponse.ok || !suggestionsResponse.ok) return

      const transactionData = await transactionsResponse.json()
      const incomeTransactions = transactionData.filter((transaction) => transaction.kind === 'income')
      const salaryTransaction = incomeTransactions.find((transaction) => transaction.category === 'Receita fixa') || incomeTransactions[0]
      if (salaryTransaction) {
        setSalary(salaryTransaction.amount)
        setSalaryTransactionId(salaryTransaction.id)
      }
      setExpenses(transactionData
        .filter((transaction) => transaction.kind === 'expense')
        .map((transaction) => ({
          id: transaction.id,
          name: transaction.description,
          category: transaction.category,
          amount: transaction.amount,
          date: transaction.date,
        })))

      const goalData = await goalsResponse.json()
      setGoals(goalData.map((goal) => ({
        id: goal.id,
        name: goal.name,
        target: goal.target_amount,
        saved: goal.saved_amount,
        monthly: Math.max(Math.ceil((goal.target_amount - goal.saved_amount) / 12), 1),
        photoUrl: goal.foto_url ? `${API_BASE_URL}${goal.foto_url}` : '',
        deadline: goal.deadline,
      })))

      const suggestionData = await suggestionsResponse.json()
      setSuggestions(suggestionData.map((suggestion) => ({
        id: suggestion.id,
        name: suggestion.name,
        category: suggestion.description || 'Geral',
        amount: suggestion.monthly_limit,
      })))
    } catch {
      showToast('Backend offline: usando dados temporarios na tela.')
    }
  }

  useEffect(() => {
    loadFinanceData()
  }, [])

  function bumpDashboard() {
    setRefreshKey((current) => current + 1)
  }

  const totalExpenses = useMemo(
    () => expenses.reduce((sum, expense) => sum + expense.amount, 0),
    [expenses],
  )
  const balance = salary - totalExpenses
  const savingPower = Math.max(balance, 0)
  const savingRate = salary > 0 ? Math.round((savingPower / salary) * 100) : 0
  const mainGoal = goals[0]
  const mainGoalMath = mainGoal ? monthsToGoal(mainGoal, lastExpense?.amount ?? 0) : null
  const indicatorList = INDICATOR_KEYS.map((key) => ({
    key,
    ...indicators[key],
  }))

  useEffect(() => {
    localStorage.setItem('finup-suggestions', JSON.stringify(suggestions))
  }, [suggestions])

  useEffect(() => {
    try {
      localStorage.setItem('finup-categories', JSON.stringify(categories))
    } catch {}
  }, [categories])

  useEffect(() => {
    setSuggestionForm((current) => {
      if (categories.includes(current.category)) return current
      return { ...current, category: categories[0] }
    })
  }, [categories])

  function showToast(message) {
    setToast(message)
    window.setTimeout(() => setToast(''), 2800)
  }

  useEffect(() => {
    let ignore = false

    async function loadIndicators() {
      setIndicatorStatus('loading')
      try {
        const responses = await Promise.all(
          INDICATOR_KEYS.map(async (key) => {
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 4000)
            const response = await fetch(`${API_BASE_URL}/indicadores/${key}`, {
              signal: controller.signal,
            })
            clearTimeout(timeoutId)
            if (!response.ok) {
              throw new Error('Nao foi possivel buscar indicadores publicos.')
            }
            return [key, await response.json()]
          }),
        )
        if (!ignore) {
          setIndicators(Object.fromEntries(responses))
          setIndicatorStatus('ready')
        }
      } catch {
        if (!ignore) {
          setIndicatorStatus('error')
        }
      }
    }

    loadIndicators()
    return () => {
      ignore = true
    }
  }, [])

  function formatIndicator(indicator) {
    if (!indicator?.valor) return 'Aguardando'
    if (indicator.key === 'dolar' || indicator.key === 'euro') {
      return money.format(indicator.valor)
    }
    return `${number.format(indicator.valor)}%`
  }

  async function saveSalary() {
    const payload = {
      data: '2026-06-05',
      descricao: 'Salario',
      categoria: 'Receita fixa',
      tipo: 'receita',
      valor: Number(salary),
      origem_arquivo: '',
      hash_unico: '',
    }
    try {
      const response = await fetch(
        salaryTransactionId
          ? `${API_BASE_URL}/transactions/${salaryTransactionId}`
          : `${API_BASE_URL}/transactions`,
        {
          method: salaryTransactionId ? 'PUT' : 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        },
      )
      if (response.ok) {
        const saved = await response.json()
        setSalaryTransactionId(saved.id)
        bumpDashboard()
        showToast('Salario atualizado no banco.')
      }
    } catch {
      showToast('Nao foi possivel salvar o salario no SQLite.')
    }
  }

  async function addExpense(event) {
    event.preventDefault()
    const amount = Number(expenseForm.amount)
    if (!expenseForm.name.trim() || !amount) return

    try {
      const response = await fetch(`${API_BASE_URL}/transactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: expenseForm.date,
          descricao: expenseForm.name,
          categoria: expenseForm.category,
          tipo: 'despesa',
          valor: amount,
          origem_arquivo: '',
          hash_unico: '',
        }),
      })
      if (!response.ok) throw new Error()
      const saved = await response.json()
      const newExpense = {
        id: saved.id,
        name: saved.descricao,
        category: saved.categoria,
        amount: saved.valor,
        date: saved.data,
      }
      setExpenses((current) => [newExpense, ...current])
      setLastExpense(newExpense)
      setExpenseForm({ name: '', category: 'Alimentacao', amount: '', date: '2026-06-08' })
      bumpDashboard()
      showToast('Gasto salvo no SQLite.')
      setActiveScreen('wallet')
    } catch {
      showToast('Nao foi possivel salvar o gasto no SQLite.')
    }
  }

  async function deleteExpense(expenseId) {
    if (!window.confirm('Tem certeza que deseja remover este gasto?')) return
    setExpenses((current) => current.filter((expense) => expense.id !== expenseId))
    try {
      const response = await fetch(`${API_BASE_URL}/transactions/${expenseId}`, { method: 'DELETE' })
      if (!response.ok) throw new Error()
      bumpDashboard()
    } catch {
      showToast('Nao foi possivel excluir no SQLite.')
      await loadFinanceData()
      return
    }
    showToast('Gasto removido com sucesso.')
  }

  function startEditExpense(expense) {
    setEditingExpenseId(expense.id)
    setEditingExpenseForm({ name: expense.name, category: expense.category, amount: expense.amount })
  }

  function cancelEditExpense() {
    setEditingExpenseId(null)
    setEditingExpenseForm({ name: '', category: '', amount: '' })
  }

  async function updateExpense(expenseId) {
    const expense = expenses.find((e) => e.id === expenseId)
    if (!expense) return
    const payload = {
      data: expense.date,
      descricao: editingExpenseForm.name,
      categoria: editingExpenseForm.category,
      tipo: 'despesa',
      valor: Number(editingExpenseForm.amount) || 0,
      origem_arquivo: '',
      hash_unico: '',
    }
    try {
      const response = await fetch(`${API_BASE_URL}/transactions/${expenseId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) throw new Error()
      const updated = await response.json()
      setExpenses((current) => current.map((e) => (e.id === expenseId ? {
        id: updated.id,
        name: updated.descricao,
        category: updated.categoria,
        amount: updated.valor,
        date: updated.data,
      } : e)))
      cancelEditExpense()
      bumpDashboard()
      showToast('Gasto atualizado com sucesso.')
    } catch {
      showToast('Nao foi possivel atualizar o gasto no SQLite.')
    }
  }

  function addCategory(newCategory) {
    const name = (newCategory || '').trim()
    if (!name) return
    if (categories.includes(name)) return
    setCategories((c) => [...c, name])
    showToast(`Categoria ${name} adicionada.`)
  }

  async function addSuggestedExpense(suggestion) {
    const date = new Date().toISOString().slice(0, 10)
    try {
      const response = await fetch(`${API_BASE_URL}/transactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: date,
          descricao: suggestion.name,
          categoria: suggestion.category,
          tipo: 'despesa',
          valor: Number(suggestion.amount),
          origem_arquivo: '',
          hash_unico: '',
        }),
      })
      if (!response.ok) throw new Error()
      const saved = await response.json()
      const newExpense = {
        id: saved.id,
        name: saved.descricao,
        category: saved.categoria,
        amount: saved.valor,
        date: saved.data,
      }
      setExpenses((current) => [newExpense, ...current])
      setLastExpense(newExpense)
      bumpDashboard()
      showToast('Gasto adicionado com sucesso.')
      setActiveScreen('wallet')
    } catch {
      showToast('Nao foi possivel salvar o gasto no SQLite.')
    }
  }

  function updateSuggestion(id, field, value) {
    setSuggestions((current) => current.map((suggestion) => (
      suggestion.id === id
        ? { ...suggestion, [field]: field === 'amount' ? Number(value) : value }
        : suggestion
    )))
  }

  async function saveSuggestion(suggestion) {
    try {
      const response = await fetch(`${API_BASE_URL}/suggested-categories/${suggestion.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: suggestion.id,
          name: suggestion.name,
          monthly_limit: Number(suggestion.amount),
          description: suggestion.category,
        }),
      })
      if (!response.ok) throw new Error()
      setEditingSuggestionId(null)
      showToast('Gasto comum salvo no SQLite.')
    } catch {
      showToast('Nao foi possivel salvar o gasto comum.')
    }
  }

  async function deleteSuggestion(suggestionId) {
    if (!window.confirm('Tem certeza que deseja excluir este gasto comum?')) return
    try {
      const response = await fetch(`${API_BASE_URL}/suggested-categories/${suggestionId}`, { method: 'DELETE' })
      if (!response.ok) throw new Error()
      setSuggestions((current) => current.filter((suggestion) => suggestion.id !== suggestionId))
      showToast('Gasto comum excluido.')
    } catch {
      showToast('Nao foi possivel excluir o gasto comum.')
    }
  }

  async function addSuggestion(event) {
    event.preventDefault()
    const amount = Number(suggestionForm.amount)
    if (!suggestionForm.name.trim() || !amount) return
    try {
      const response = await fetch(`${API_BASE_URL}/suggested-categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: suggestionForm.name,
          monthly_limit: amount,
          description: suggestionForm.category,
        }),
      })
      if (!response.ok) throw new Error()
      const saved = await response.json()
      setSuggestions((current) => [
        ...current,
        {
          id: saved.id,
          name: saved.name,
          category: saved.description || 'Geral',
          amount: saved.monthly_limit,
        },
      ])
      setSuggestionForm({ name: '', category: 'Geral', amount: '' })
      showToast('Gasto comum criado.')
    } catch {
      showToast('Nao foi possivel criar o gasto comum.')
    }
  }

  async function addGoal(event) {
    event.preventDefault()
    const target = Number(goalForm.target)
    const monthly = Number(goalForm.monthly)
    if (!goalForm.name.trim() || !target || !monthly) return

    try {
      const response = await fetch(`${API_BASE_URL}/goals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: goalForm.name,
          valor_objetivo: target,
          valor_atual: Number(goalForm.saved) || 0,
          prazo: '2026-12-31',
          foto_url: '',
        }),
      })
      if (!response.ok) throw new Error()
      await loadFinanceData()
      setGoalForm({ name: '', target: '', saved: '', monthly: '' })
      bumpDashboard()
      showToast('Meta salva no SQLite.')
      setActiveScreen('goals')
    } catch {
      showToast('Nao foi possivel salvar a meta.')
    }
  }

  async function saveGoal(goal) {
    try {
      const response = await fetch(`${API_BASE_URL}/goals/${goal.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: goal.id,
          nome: goal.name,
          valor_objetivo: Number(goal.target),
          valor_atual: Number(goal.saved),
          prazo: goal.deadline || '2026-12-31',
          foto_url: goal.photoUrl?.replace(API_BASE_URL, '') || '',
        }),
      })
      if (!response.ok) throw new Error()
      setEditingGoalId(null)
      await loadFinanceData()
      bumpDashboard()
      showToast('Meta atualizada.')
    } catch {
      showToast('Nao foi possivel editar a meta.')
    }
  }

  async function deleteGoal(goalId) {
    if (!window.confirm('Tem certeza que deseja excluir esta meta?')) return
    try {
      const response = await fetch(`${API_BASE_URL}/goals/${goalId}`, { method: 'DELETE' })
      if (!response.ok) throw new Error()
      setGoals((current) => current.filter((goal) => goal.id !== goalId))
      bumpDashboard()
      showToast('Meta excluida.')
    } catch {
      showToast('Nao foi possivel excluir a meta.')
    }
  }

  function updateGoalField(goalId, field, value) {
    setGoals((current) => current.map((goal) => (
      goal.id === goalId
        ? { ...goal, [field]: field === 'target' || field === 'saved' || field === 'monthly' ? Number(value) : value }
        : goal
    )))
  }

  async function uploadGoalPhoto(goalId, file) {
    if (!file) return
    const localUrl = URL.createObjectURL(file)
    setGoals((current) => current.map((goal) => (
      goal.id === goalId ? { ...goal, photoUrl: localUrl } : goal
    )))
    const formData = new FormData()
    formData.append('foto', file)
    try {
      const response = await fetch(`${API_BASE_URL}/metas/${goalId}/foto`, {
        method: 'POST',
        body: formData,
      })
      if (response.ok) {
        const updatedGoal = await response.json()
        setGoals((current) => current.map((goal) => (
          goal.id === goalId
            ? { ...goal, photoUrl: `${API_BASE_URL}${updatedGoal.foto_url}` }
            : goal
        )))
        bumpDashboard()
      }
    } catch {
      showToast('Foto salva apenas na tela atual porque o backend esta offline.')
      return
    }
    showToast('Foto da meta atualizada.')
  }

  return (
    <main className="app-shell">
      {toast && <div className="toast-message">{toast}</div>}
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">F</span>
          <div>
            <strong>FinUp</strong>
            <small>personal money</small>
          </div>
        </div>

        <nav className="nav-list" aria-label="Principal">
          {Object.entries(screens).map(([key, label]) => (
            <button
              className={activeScreen === key ? 'active' : ''}
              key={key}
              type="button"
              onClick={() => setActiveScreen(key)}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="profile-box">
          <span>Saldo disponivel</span>
          <strong>{money.format(balance)}</strong>
          <small>{savingRate}% da renda ainda pode virar meta este mes.</small>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">Controle financeiro pessoal</span>
            <h1>{screens[activeScreen]}</h1>
          </div>
          <button type="button" onClick={() => setActiveScreen('wallet')}>+ Novo Gasto</button>
        </header>

        {activeScreen === 'home' && (
          <>
            <section className="hero-panel" aria-label="Resumo financeiro">
              <div>
                <p className="hero-kicker">Visao geral</p>
                <h2>Seu dinheiro, suas metas e seus habitos no mesmo raciocinio.</h2>
                <p>
                  Informe o salario, registre gastos reais e acompanhe como cada
                  escolha impacta objetivos como viagem, reserva e compras importantes.
                </p>
              </div>
              <div className="hero-metrics">
                <div>
                  <span>Salario mensal</span>
                  <strong>{money.format(salary)}</strong>
                </div>
                <div>
                  <span>Gastos do mes</span>
                  <strong>{money.format(totalExpenses)}</strong>
                </div>
                <div>
                  <span>Saldo livre</span>
                  <strong>{money.format(balance)}</strong>
                </div>
              </div>
            </section>

            <section className="content-grid">
              <div className="panel salary-card">
                <span className="eyebrow">Renda</span>
                <h3>Meu salario</h3>
                <label className="field">
                  <span>Quanto entra por mes?</span>
                  <input
                    min="0"
                    type="number"
                    value={salary}
                    onChange={(event) => setSalary(Number(event.target.value))}
                    onBlur={saveSalary}
                  />
                </label>
                <p className="panel-note">Esse valor e salvo no SQLite como receita fixa e guia todos os calculos do app.</p>
              </div>

              <div className="panel">
                <span className="eyebrow">Inteligencia</span>
                <h3>Impacto recente</h3>
                <p className="insight">
                  {lastExpense && mainGoalMath
                    ? `Voce adicionou ${money.format(lastExpense.amount)} em ${lastExpense.name}. Por causa disso, a meta "${mainGoal.name}" pode demorar mais ${mainGoalMath.delay} mes(es), mantendo o ritmo atual.`
                    : 'Adicione um gasto para o FinUp calcular como isso muda o prazo das suas metas.'}
                </p>
              </div>


            </section>
          </>
        )}

        {activeScreen === 'wallet' && (
          <section className="content-grid">
            <div className="panel wide">
              <div className="panel-heading">
                <div>
                  <span className="eyebrow">Meu Histórico</span>
                  <h3>Todos os gastos</h3>
                </div>
                <strong>{money.format(totalExpenses)}</strong>
              </div>

              <form className="form-grid" onSubmit={addExpense}>
                <label className="field">
                  <span>Descricao</span>
                  <input
                    value={expenseForm.name}
                    onChange={(event) => setExpenseForm({ ...expenseForm, name: event.target.value })}
                    placeholder="Ex: almoco, mercado, farmacia"
                  />
                </label>
                <label className="field">
                  <span>Categoria</span>
                  <select
                    value={expenseForm.category}
                    onChange={(event) => setExpenseForm({ ...expenseForm, category: event.target.value })}
                  >
                    <option>Alimentacao</option>
                    <option>Casa</option>
                    <option>Transporte</option>
                    <option>Lazer</option>
                    <option>Saude</option>
                    <option>Estudos</option>
                    <option>Assinaturas</option>
                  </select>
                </label>
                <label className="field">
                  <span>Valor</span>
                  <input
                    min="0"
                    type="number"
                    value={expenseForm.amount}
                    onChange={(event) => setExpenseForm({ ...expenseForm, amount: event.target.value })}
                    placeholder="0"
                  />
                </label>
                <button type="submit">Adicionar</button>
              </form>
            </div>

            <div className="panel wide">
              <div className="project-list">
                {expenses.map((expense) => (
                  <article className="project-row" key={expense.id}>
                    <div>
                      {editingExpenseId === expense.id ? (
                        <div className="expense-editor">
                          <input value={editingExpenseForm.name} onChange={(e) => setEditingExpenseForm({ ...editingExpenseForm, name: e.target.value })} />
                          <select value={editingExpenseForm.category} onChange={(e) => setEditingExpenseForm({ ...editingExpenseForm, category: e.target.value })}>
                            {categories.map((c) => <option key={c}>{c}</option>)}
                          </select>
                          <input type="number" min="0" value={editingExpenseForm.amount} onChange={(e) => setEditingExpenseForm({ ...editingExpenseForm, amount: e.target.value })} />
                        </div>
                      ) : (
                        <>
                          <strong>{expense.name}</strong>
                          <span>{expense.category} - {expense.date}</span>
                        </>
                      )}
                    </div>
                    <div className="progress-track" aria-label="peso no salario">
                      <span style={{ width: `${Math.min((expense.amount / Math.max(salary, 1)) * 100, 100)}%` }} />
                    </div>
                    <span className="budget">- {money.format(expense.amount)}</span>
                    <span className={`status ${expense.amount > salary * 0.1 ? 'warning' : ''}`}>
                      {expense.amount > salary * 0.1 ? 'Revisar' : 'Ok'}
                    </span>
                    {editingExpenseId === expense.id ? (
                      <>
                        <button type="button" onClick={() => updateExpense(expense.id)}>Salvar</button>
                        <button className="ghost" type="button" onClick={cancelEditExpense}>Cancelar</button>
                      </>
                    ) : (
                      <>
                        <button type="button" onClick={() => startEditExpense(expense)}>Editar</button>
                        <button className="danger-button" type="button" onClick={() => deleteExpense(expense.id)}>Excluir</button>
                      </>
                    )}
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}

        {activeScreen === 'habits' && (
          <section className="content-grid">
            <div className="panel wide">
              <span className="eyebrow">Gastos Fixos</span>
              <h3>Gastos comuns do dia a dia</h3>
              <form className="form-grid suggestion-create" onSubmit={addSuggestion}>
                <label className="field">
                  <span>Nome</span>
                  <input
                    value={suggestionForm.name}
                    onChange={(event) => setSuggestionForm({ ...suggestionForm, name: event.target.value })}
                    placeholder="Ex: Mercado"
                  />
                </label>
                <label className="field">
                  <span>Categoria</span>
                  <select value={suggestionForm.category} onChange={(event) => setSuggestionForm({ ...suggestionForm, category: event.target.value })}>
                    {categories.map((c) => <option key={c}>{c}</option>)}
                  </select>
                </label>
                <label className="field">
                  <span>Valor padrao</span>
                  <input
                    min="0"
                    type="number"
                    value={suggestionForm.amount}
                    onChange={(event) => setSuggestionForm({ ...suggestionForm, amount: event.target.value })}
                    placeholder="0"
                  />
                </label>
                <button type="submit">Criar gasto comum</button>
              </form>
              <div className="add-category">
                <label className="field">
                  <span>Adicionar categoria</span>
                  <input placeholder="Nova categoria" id="new-category-input" />
                </label>
                <button type="button" onClick={() => {
                  const el = document.getElementById('new-category-input')
                  if (!el) return
                  addCategory(el.value)
                  el.value = ''
                }}>Adicionar</button>
              </div>
              {suggestions.length === 0 && (
                <div className="empty-state">
                  <strong>Nenhum gasto comum cadastrado.</strong>
                  <span>Crie um gasto acima para voltar a adicionar despesas rapidas na carteira.</span>
                </div>
              )}
              <div className="suggestion-grid">
                {suggestions.map((suggestion) => (
                  <article className="suggestion-card" key={suggestion.id}>
                    <div className="floating-actions">
                      <button className="icon-button" type="button" onClick={() => setEditingSuggestionId(editingSuggestionId === suggestion.id ? null : suggestion.id)}>Editar</button>
                      <button className="icon-button danger-mini" type="button" onClick={() => deleteSuggestion(suggestion.id)}>Excluir</button>
                    </div>
                    <button className="suggestion-action" type="button" onClick={() => addSuggestedExpense(suggestion)}>
                      <span>{suggestion.category}</span>
                      <strong>{suggestion.name}</strong>
                      <small>{money.format(suggestion.amount)}</small>
                    </button>
                    {editingSuggestionId === suggestion.id && (
                      <div className="suggestion-editor">
                          <input value={suggestion.name} onChange={(event) => updateSuggestion(suggestion.id, 'name', event.target.value)} />
                          <select value={suggestion.category} onChange={(event) => updateSuggestion(suggestion.id, 'category', event.target.value)}>
                            {categories.map((c) => <option key={c}>{c}</option>)}
                          </select>
                          <input type="number" min="0" value={suggestion.amount} onChange={(event) => updateSuggestion(suggestion.id, 'amount', event.target.value)} />
                          <button type="button" onClick={() => saveSuggestion(suggestion)}>Salvar</button>
                        </div>
                    )}
                  </article>
                ))}
              </div>
            </div>
          </section>
        )}

        {activeScreen === 'indicators' && (
          <section className="content-grid">
            <div className="panel wide">
              <div className="panel-heading">
                <div>
                  <span className="eyebrow">Banco Central</span>
                  <h3>Indicadores economicos</h3>
                </div>
                <span className={`status ${indicatorStatus === 'error' ? 'warning' : ''}`}>
                  {indicatorStatus === 'loading' ? 'Atualizando' : indicatorStatus === 'error' ? 'Offline' : 'Atualizado'}
                </span>
              </div>
              <div className="indicator-grid">
                {indicatorList.map((indicator) => (
                  <article className="indicator-card" key={indicator.key}>
                    <span>{indicatorLabels[indicator.key]}</span>
                    <strong>{formatIndicator(indicator)}</strong>
                    <small>
                      {indicator?.data_referencia
                        ? `${indicator.fonte} - ${indicator.data_referencia}`
                        : 'Inicie o backend para consultar o Banco Central.'}
                    </small>
                  </article>
                ))}
              </div>
            </div>

            <div className="panel wide">
              <span className="eyebrow">Leitura economica</span>
              <h3>Insights publicos</h3>
              <div className="insight-list">
                <p>A cotacao do dolar esta alta? Cuidado com compras internacionais e assinaturas em moeda estrangeira.</p>
                <p>Com a Selic atual, investimentos de renda fixa podem estar mais atrativos para reserva de emergencia.</p>
                <p>A inflacao medida pelo IPCA impacta seu poder de compra e pode exigir revisar metas e limites mensais.</p>
              </div>
            </div>
          </section>
        )}

        {activeScreen === 'goals' && (
          <section className="content-grid">
            <div className="panel wide">
              <div className="panel-heading">
                <div>
                  <span className="eyebrow">Objetivos</span>
                  <h3>Metas financeiras</h3>
                </div>
                <strong>{goals.length} ativas</strong>
              </div>
              <form className="form-grid" onSubmit={addGoal}>
                <label className="field">
                  <span>Nome da meta</span>
                  <input value={goalForm.name} onChange={(event) => setGoalForm({ ...goalForm, name: event.target.value })} placeholder="Ex: viagem" />
                </label>
                <label className="field">
                  <span>Valor alvo</span>
                  <input min="0" type="number" value={goalForm.target} onChange={(event) => setGoalForm({ ...goalForm, target: event.target.value })} />
                </label>
                <label className="field">
                  <span>Ja guardado</span>
                  <input min="0" type="number" value={goalForm.saved} onChange={(event) => setGoalForm({ ...goalForm, saved: event.target.value })} />
                </label>
                <label className="field">
                  <span>Guardar por mes</span>
                  <input min="0" type="number" value={goalForm.monthly} onChange={(event) => setGoalForm({ ...goalForm, monthly: event.target.value })} />
                </label>
                <button type="submit">Criar meta</button>
              </form>
            </div>

            <div className="panel wide">
              <div className="risk-grid">
                {goals.map((goal) => {
                  const percent = Math.min(Math.round((goal.saved / goal.target) * 100), 100)
                  const { baseMonths, delay } = monthsToGoal(goal, lastExpense?.amount ?? 0)
                  return (
                    <div className="risk-card" key={goal.id}>
                      {goal.photoUrl && <img className="goal-photo" src={goal.photoUrl} alt="" />}
                      <div className="card-actions-row">
                        <span>{goal.name}</span>
                        <div className="table-actions">
                          <button type="button" onClick={() => setEditingGoalId(editingGoalId === goal.id ? null : goal.id)}>Editar</button>
                          <button className="danger-button" type="button" onClick={() => deleteGoal(goal.id)}>Excluir</button>
                        </div>
                      </div>
                      {editingGoalId === goal.id ? (
                        <div className="suggestion-editor">
                          <input value={goal.name} onChange={(event) => updateGoalField(goal.id, 'name', event.target.value)} />
                          <input type="number" min="0" value={goal.target} onChange={(event) => updateGoalField(goal.id, 'target', event.target.value)} />
                          <input type="number" min="0" value={goal.saved} onChange={(event) => updateGoalField(goal.id, 'saved', event.target.value)} />
                          <input value={goal.deadline || '2026-12-31'} onChange={(event) => updateGoalField(goal.id, 'deadline', event.target.value)} />
                          <button type="button" onClick={() => saveGoal(goal)}>Salvar meta</button>
                          <button className="ghost" type="button" onClick={() => setEditingGoalId(null)}>Cancelar</button>
                        </div>
                      ) : (
                        <>
                          <strong>{percent}%</strong>
                          <small>
                            Faltam {money.format(goal.target - goal.saved)}. No ritmo atual:
                            {' '}{baseMonths} mes(es).{lastExpense ? ` Ultimo gasto adiciona ${delay} mes(es) de impacto.` : ''}
                          </small>
                        </>
                      )}
                      <label className="photo-upload">
                        {goal.photoUrl ? 'Alterar foto' : 'Adicionar foto'}
                        <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => uploadGoalPhoto(goal.id, event.target.files?.[0])} />
                      </label>
                    </div>
                  )
                })}
              </div>
            </div>
          </section>
        )}

        {activeScreen === 'financeDashboard' && <FinanceDashboard refreshKey={refreshKey} />}
      </section>
    </main>
  )
}

export default App
