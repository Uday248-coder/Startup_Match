const API_URL = 'http://localhost:5000/api'

export const API = {
  // Auth
  signupInvestor: (data) => fetch(`${API_URL}/auth/signup/investor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  signupStartup: (data) => fetch(`${API_URL}/auth/signup/startup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  login: (email, password, userType) => fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, user_type: userType })
  }).then(r => r.json()),

  // Investor
  getInvestorProfile: (token) => fetch(`${API_URL}/investor/profile`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json()),

  updateInvestorProfile: (token, data) => fetch(`${API_URL}/investor/profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  getInvestorMatches: (token, top = 10) => fetch(`${API_URL}/investor/matches?top=${top}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json()),

  // Startup
  getStartupProfile: (token) => fetch(`${API_URL}/startup/profile`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json()),

  updateStartupProfile: (token, data) => fetch(`${API_URL}/startup/profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify(data)
  }).then(r => r.json()),

  getStartupMatches: (token, top = 10) => fetch(`${API_URL}/startup/matches?top=${top}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json()),
}
