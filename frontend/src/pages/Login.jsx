import { useState } from 'react'
import { Link } from 'react-router-dom'
import { API } from '../api'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [userType, setUserType] = useState('investor')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const res = await API.login(email, password, userType)
    
    if (res.error) {
      setError(res.error)
      setLoading(false)
    } else {
      onLogin(res.user)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login to StartupMatch</h2>
        
        <div className="user-type-selector">
          <button 
            type="button"
            className={userType === 'investor' ? 'active' : ''} 
            onClick={() => setUserType('investor')}
          >
            Investor
          </button>
          <button 
            type="button"
            className={userType === 'startup' ? 'active' : ''} 
            onClick={() => setUserType('startup')}
          >
            Startup
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        <p className="auth-link">
          Don't have an account? <Link to="/register">Sign up</Link>
        </p>

        <div className="demo-credentials">
          <p><strong>Demo:</strong></p>
          <p>investor1@demo.com / password123</p>
          <p>startup1@demo.com / password123</p>
        </div>
      </div>
    </div>
  )
}
