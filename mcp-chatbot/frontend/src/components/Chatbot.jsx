import React, { useMemo, useState } from 'react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function Chatbot() {
  const [token, setToken] = useState('')
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('password')
  const [query, setQuery] = useState('Show me failed orders today')
  const [messages, setMessages] = useState([])
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(false)

  async function login(e) {
    e.preventDefault()
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    try {
      const res = await axios.post(`${API_BASE}/auth/login`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      setToken(res.data.access_token)
    } catch (err) {
      alert('Login failed')
    }
  }

  async function sendQuery(e) {
    e.preventDefault()
    if (!token) {
      alert('Login first')
      return
    }
    setLoading(true)
    setMessages((m) => [...m, { role: 'user', content: query }])
    try {
      const res = await axios.post(`${API_BASE}/nl-query`, { query }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMessages((m) => [...m, { role: 'assistant', content: res.data.explanation }])
      setRows(res.data.rows || [])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: 'Error querying API' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="space-y-4">
        <form onSubmit={login} className="bg-white p-4 rounded border space-y-3">
          <div className="font-medium">Login</div>
          <input className="border px-3 py-2 w-full" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input className="border px-3 py-2 w-full" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="bg-black text-white px-4 py-2 rounded" type="submit">Get Token</button>
          {token && <div className="text-xs text-green-600 break-all">Token: {token}</div>}
        </form>

        <form onSubmit={sendQuery} className="bg-white p-4 rounded border space-y-3">
          <div className="font-medium">Chat</div>
          <textarea className="border px-3 py-2 w-full" rows={3} value={query} onChange={(e) => setQuery(e.target.value)} />
          <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded" type="submit">{loading ? 'Asking...' : 'Ask'}</button>
        </form>

        <div className="bg-white p-4 rounded border space-y-2">
          <div className="font-medium">Messages</div>
          <div className="space-y-2 max-h-64 overflow-auto">
            {messages.map((m, i) => (
              <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
                <span className={`inline-block px-3 py-2 rounded ${m.role === 'user' ? 'bg-blue-100' : 'bg-gray-100'}`}>{m.content}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded border">
        <div className="font-medium mb-3">Results</div>
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Order ID</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Error Message</th>
                <th className="py-2 pr-4">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-b last:border-b-0">
                  <td className="py-2 pr-4">{r.orderId}</td>
                  <td className="py-2 pr-4">{r.status}</td>
                  <td className="py-2 pr-4">{r.errorMessage || ''}</td>
                  <td className="py-2 pr-4">{new Date(r.timestamp).toLocaleString()}</td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan="4" className="py-6 text-center text-gray-400">No data</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}


