import { useEffect, useState, type FormEvent } from 'react'
import './App.css'

const API = ''

type User = {
  id: number
  name: string
  email: string
  role: string
  active: boolean
  createdAt: string
}

type Stats = { totalUsers: number; activeUsers: number; adminUsers: number }

const blankForm = { name: '', email: '', role: 'viewer', active: true }

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [loginError, setLoginError] = useState('')

  const [users, setUsers] = useState<User[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(blankForm)

  const headers = (): HeadersInit => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  })

  async function login(e: FormEvent) {
    e.preventDefault()
    setLoginError('')
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      setLoginError('Invalid credentials')
      return
    }
    const data = await res.json()
    localStorage.setItem('token', data.token)
    setToken(data.token)
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
    setUsers([])
    setStats(null)
  }

  async function refresh() {
    setError('')
    try {
      const [uRes, sRes] = await Promise.all([
        fetch(`${API}/api/users`, { headers: headers() }),
        fetch(`${API}/api/stats`, { headers: headers() }),
      ])
      if (uRes.status === 401 || sRes.status === 401) {
        logout()
        return
      }
      setUsers(await uRes.json())
      setStats(await sRes.json())
    } catch (err) {
      setError(`Failed to load: ${(err as Error).message}`)
    }
  }

  useEffect(() => {
    if (token) refresh()
  }, [token])

  async function submitForm(e: FormEvent) {
    e.preventDefault()
    setError('')
    const url = editingId == null ? `${API}/api/users` : `${API}/api/users/${editingId}`
    const method = editingId == null ? 'POST' : 'PUT'
    const res = await fetch(url, { method, headers: headers(), body: JSON.stringify(form) })
    if (!res.ok) {
      setError(`Save failed (${res.status})`)
      return
    }
    setForm(blankForm)
    setEditingId(null)
    refresh()
  }

  function startEdit(u: User) {
    setEditingId(u.id)
    setForm({ name: u.name, email: u.email, role: u.role, active: u.active })
  }

  async function remove(id: number) {
    if (!confirm('Delete this user?')) return
    const res = await fetch(`${API}/api/users/${id}`, { method: 'DELETE', headers: headers() })
    if (!res.ok) setError(`Delete failed (${res.status})`)
    refresh()
  }

  if (!token) {
    return (
      <div className="login-shell">
        <form className="card login-card" onSubmit={login}>
          <h1>Admin Login</h1>
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <button type="submit">Sign in</button>
          {loginError && <p className="error">{loginError}</p>}
          <p className="hint">Demo credentials: admin / admin123</p>
        </form>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>Admin Console</h1>
        <button onClick={logout}>Logout</button>
      </header>

      {stats && (
        <section className="stats">
          <div className="card stat"><span>Total</span><strong>{stats.totalUsers}</strong></div>
          <div className="card stat"><span>Active</span><strong>{stats.activeUsers}</strong></div>
          <div className="card stat"><span>Admins</span><strong>{stats.adminUsers}</strong></div>
        </section>
      )}

      <section className="card">
        <h2>{editingId == null ? 'Create user' : `Edit user #${editingId}`}</h2>
        <form className="user-form" onSubmit={submitForm}>
          <input
            placeholder="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <input
            placeholder="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="admin">admin</option>
            <option value="editor">editor</option>
            <option value="viewer">viewer</option>
          </select>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) => setForm({ ...form, active: e.target.checked })}
            />
            Active
          </label>
          <div className="actions">
            <button type="submit">{editingId == null ? 'Create' : 'Save'}</button>
            {editingId != null && (
              <button type="button" onClick={() => { setEditingId(null); setForm(blankForm) }}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Users</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Active</th><th>Created</th><th></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td><span className={`badge role-${u.role}`}>{u.role}</span></td>
                <td>{u.active ? 'Yes' : 'No'}</td>
                <td>{new Date(u.createdAt).toLocaleDateString()}</td>
                <td className="row-actions">
                  <button onClick={() => startEdit(u)}>Edit</button>
                  <button className="danger" onClick={() => remove(u.id)}>Delete</button>
                </td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr><td colSpan={7} className="muted">No users</td></tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  )
}
