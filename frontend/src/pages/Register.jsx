import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { API } from '../api'

export default function Register() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    userType: 'investor',
    company: '',
    sectors: '',
    stagePreference: '',
    minCheck: '',
    maxCheck: '',
    locations: '',
    sector: '',
    stage: '',
    fundingNeeded: '',
    location: '',
    description: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const data = {
      email: formData.email,
      password: formData.password,
      name: formData.name,
    }

    if (formData.userType === 'investor') {
      data.company = formData.company
      data.sectors = formData.sectors.split(',').map(s => s.trim())
      data.stage_preference = formData.stagePreference
      data.min_check = parseInt(formData.minCheck) || 0
      data.max_check = parseInt(formData.maxCheck) || 0
      data.locations = formData.locations.split(',').map(l => l.trim())
    } else {
      data.name = formData.company || formData.name
      data.description = formData.description
      data.sector = formData.sector
      data.stage = formData.stage
      data.funding_needed = parseInt(formData.fundingNeeded) || 0
      data.location = formData.location
    }

    const res = formData.userType === 'investor' 
      ? await API.signupInvestor(data)
      : await API.signupStartup(data)

    if (res.error) {
      setError(res.error)
      setLoading(false)
    } else {
      navigate('/login')
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Sign Up for StartupMatch</h2>
        
        <div className="user-type-selector">
          <button 
            type="button"
            className={formData.userType === 'investor' ? 'active' : ''} 
            onClick={() => setFormData({ ...formData, userType: 'investor' })}
          >
            Investor
          </button>
          <button 
            type="button"
            className={formData.userType === 'startup' ? 'active' : ''} 
            onClick={() => setFormData({ ...formData, userType: 'startup' })}
          >
            Startup
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="name"
            placeholder={formData.userType === 'investor' ? 'Your Name' : 'Startup Name'}
            value={formData.name}
            onChange={handleChange}
            required
          />

          {formData.userType === 'investor' ? (
            <>
              <input
                type="text"
                name="company"
                placeholder="Company Name"
                value={formData.company}
                onChange={handleChange}
              />
              <input
                type="text"
                name="sectors"
                placeholder="Sectors (comma-separated, e.g., Technology,Healthcare)"
                value={formData.sectors}
                onChange={handleChange}
              />
              <select name="stagePreference" value={formData.stagePreference} onChange={handleChange}>
                <option value="">Stage Preference</option>
                <option value="Pre-Seed">Pre-Seed</option>
                <option value="Seed">Seed</option>
                <option value="Series A">Series A</option>
                <option value="Series B">Series B</option>
                <option value="Series C">Series C</option>
              </select>
              <div className="check-range">
                <input
                  type="number"
                  name="minCheck"
                  placeholder="Min Check ($)"
                  value={formData.minCheck}
                  onChange={handleChange}
                />
                <input
                  type="number"
                  name="maxCheck"
                  placeholder="Max Check ($)"
                  value={formData.maxCheck}
                  onChange={handleChange}
                />
              </div>
              <input
                type="text"
                name="locations"
                placeholder="Locations (e.g., North America,Europe)"
                value={formData.locations}
                onChange={handleChange}
              />
            </>
          ) : (
            <>
              <textarea
                name="description"
                placeholder="Startup Description"
                value={formData.description}
                onChange={handleChange}
              />
              <select name="sector" value={formData.sector} onChange={handleChange}>
                <option value="">Select Sector</option>
                <option value="Technology">Technology</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Finance">Finance</option>
                <option value="E-commerce">E-commerce</option>
                <option value="Education">Education</option>
                <option value="Energy">Energy</option>
              </select>
              <select name="stage" value={formData.stage} onChange={handleChange}>
                <option value="">Funding Stage</option>
                <option value="Pre-Seed">Pre-Seed</option>
                <option value="Seed">Seed</option>
                <option value="Series A">Series A</option>
                <option value="Series B">Series B</option>
              </select>
              <input
                type="number"
                name="fundingNeeded"
                placeholder="Funding Needed ($)"
                value={formData.fundingNeeded}
                onChange={handleChange}
              />
              <select name="location" value={formData.location} onChange={handleChange}>
                <option value="">Location</option>
                <option value="North America">North America</option>
                <option value="Europe">Europe</option>
                <option value="Asia">Asia</option>
                <option value="Global">Global</option>
              </select>
            </>
          )}

          <button type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
