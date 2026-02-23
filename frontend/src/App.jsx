import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import InvestorDashboard from './pages/InvestorDashboard'
import StartupDashboard from './pages/StartupDashboard'
import './App.css'

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <h1>StartupMatch</h1>
          {user && (
            <div className="user-info">
              <span>Welcome, {user.name}</span>
              <button onClick={handleLogout}>Logout</button>
            </div>
          )}
        </header>
        <main>
          <Routes>
            <Route path="/" element={
              user ? <Navigate to={user.user_type === 'investor' ? '/investor' : '/startup'} /> : <Login onLogin={handleLogin} />
            } />
            <Route path="/login" element={
              user ? <Navigate to={user.user_type === 'investor' ? '/investor' : '/startup'} /> : <Login onLogin={handleLogin} />
            } />
            <Route path="/register" element={
              user ? <Navigate to={user.user_type === 'investor' ? '/investor' : '/startup'} /> : <Register />
            } />
            <Route path="/investor" element={
              user?.user_type === 'investor' ? <InvestorDashboard user={user} /> : <Navigate to="/login" />
            } />
            <Route path="/startup" element={
              user?.user_type === 'startup' ? <StartupDashboard user={user} /> : <Navigate to="/login" />
            } />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
