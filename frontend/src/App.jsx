import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchVirtualCenters, login } from './api'

function LoginPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ baseUrl: '', username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const onChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login(form)
      navigate('/virtualcenters', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page login-page">
      <form onSubmit={onSubmit} className="card form-card">
        <h1>VCF Login</h1>
        <label>
          URL
          <input
            name="baseUrl"
            type="url"
            placeholder="https://vcf.example.local"
            value={form.baseUrl}
            onChange={onChange}
          />
        </label>
        <label>
          Username
          <input name="username" type="text" required value={form.username} onChange={onChange} />
        </label>
        <label>
          Password
          <input name="password" type="password" required value={form.password} onChange={onChange} />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? '로그인 중...' : '로그인'}
        </button>
      </form>
    </div>
  )
}

function VirtualCentersPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')

    try {
      const data = await fetchVirtualCenters()
      setItems(data.items || [])
    } catch (err) {
      if (err.status === 401) {
        navigate('/', { replace: true, state: { reason: err.message } })
        return
      }
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page">
      <div className="card">
        <div className="header-row">
          <h1>Virtual Centers</h1>
          <button type="button" onClick={load} disabled={loading}>
            {loading ? '로딩 중...' : '새로고침'}
          </button>
        </div>

        {location.state?.reason && <p className="error">{location.state.reason}</p>}

        {loading && <p>데이터를 불러오는 중입니다...</p>}

        {!loading && error && <p className="error">{error}</p>}

        {!loading && !error && items.length === 0 && <p>표시할 Virtual Center 데이터가 없습니다.</p>}

        {!loading && !error && items.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>ID</th>
                <th>Status</th>
                <th>Version</th>
                <th>FQDN</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id || item.name}>
                  <td>{item.name || '-'}</td>
                  <td>{item.id || '-'}</td>
                  <td>{item.status || '-'}</td>
                  <td>{item.version || '-'}</td>
                  <td>{item.fqdn || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/virtualcenters" element={<VirtualCentersPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
