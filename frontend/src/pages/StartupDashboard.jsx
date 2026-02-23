import { useState, useEffect } from 'react'
import { API } from '../api'

export default function StartupDashboard({ user }) {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      const token = user.token
      
      const [profileRes, matchesRes] = await Promise.all([
        API.getStartupProfile(token),
        API.getStartupMatches(token, 10)
      ])
      
      if (profileRes.user) setProfile(profileRes.user)
      if (matchesRes.matches) setMatches(matchesRes.matches)
      setLoading(false)
    }
    
    fetchData()
  }, [user])

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Startup Dashboard</h2>
        <p>Welcome back, {user.name}</p>
      </div>

      <div className="profile-section">
        <h3>Your Profile</h3>
        {profile && (
          <div className="profile-info">
            <p><strong>Sector:</strong> {profile.sector || 'Not set'}</p>
            <p><strong>Stage:</strong> {profile.stage || 'Not set'}</p>
            <p><strong>Funding Needed:</strong> ${profile.funding_needed?.toLocaleString() || 0}</p>
            <p><strong>Location:</strong> {profile.location || 'Not set'}</p>
            <p><strong>Team Size:</strong> {profile.team_size || 0}</p>
            <p><strong>Revenue:</strong> ${profile.revenue?.toLocaleString() || 0}</p>
          </div>
        )}
      </div>

      <div className="matches-section">
        <h3>Recommended Investors</h3>
        {matches.length === 0 ? (
          <p>No matches found. Complete your profile to get recommendations.</p>
        ) : (
          <div className="matches-grid">
            {matches.map((investor) => (
              <div key={investor.id} className="match-card investor-card">
                <div className="match-header">
                  <h4>{investor.name}</h4>
                  <span className="match-score">{Math.round(investor.match_score * 100)}% Match</span>
                </div>
                <p className="investor-company">{investor.company}</p>
                <p className="investor-sectors">Focus: {investor.sectors}</p>
                <p className="investor-stage">Prefers: {investor.stage_preference}</p>
                <p className="investor-check">Check: ${investor.min_check?.toLocaleString()} - ${investor.max_check?.toLocaleString()}</p>
                <p className="investor-locations">{investor.locations}</p>
                <div className="match-details">
                  <span>Sector: {Math.round(investor.match_details?.sector * 100)}%</span>
                  <span>Stage: {Math.round(investor.match_details?.stage * 100)}%</span>
                  <span>Location: {Math.round(investor.match_details?.location * 100)}%</span>
                  <span>Funding: {Math.round(investor.match_details?.funding * 100)}%</span>
                </div>
                <button className="contact-btn">Connect</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
