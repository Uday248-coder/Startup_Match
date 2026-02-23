import { useState, useEffect } from 'react'
import { API } from '../api'

export default function InvestorDashboard({ user }) {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      const token = user.token
      
      const [profileRes, matchesRes] = await Promise.all([
        API.getInvestorProfile(token),
        API.getInvestorMatches(token, 10)
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
        <h2>Investor Dashboard</h2>
        <p>Welcome back, {user.name}</p>
      </div>

      <div className="profile-section">
        <h3>Your Profile</h3>
        {profile && (
          <div className="profile-info">
            <p><strong>Company:</strong> {profile.company || 'Not set'}</p>
            <p><strong>Sectors:</strong> {profile.sectors || 'Not set'}</p>
            <p><strong>Stage Preference:</strong> {profile.stage_preference || 'Not set'}</p>
            <p><strong>Check Size:</strong> ${profile.min_check || 0} - ${profile.max_check || 0}</p>
            <p><strong>Locations:</strong> {profile.locations || 'Not set'}</p>
          </div>
        )}
      </div>

      <div className="matches-section">
        <h3>Recommended Startups</h3>
        {matches.length === 0 ? (
          <p>No matches found. Complete your profile to get recommendations.</p>
        ) : (
          <div className="matches-grid">
            {matches.map((startup) => (
              <div key={startup.id} className="match-card">
                <div className="match-header">
                  <h4>{startup.name}</h4>
                  <span className="match-score">{Math.round(startup.match_score * 100)}% Match</span>
                </div>
                <p className="startup-sector">{startup.sector}</p>
                <p className="startup-stage">{startup.stage} - ${startup.funding_needed?.toLocaleString()}</p>
                <p className="startup-location">{startup.location}</p>
                {startup.description && <p className="startup-desc">{startup.description}</p>}
                <div className="match-details">
                  <span>Sector: {Math.round(startup.match_details?.sector * 100)}%</span>
                  <span>Stage: {Math.round(startup.match_details?.stage * 100)}%</span>
                  <span>Location: {Math.round(startup.match_details?.location * 100)}%</span>
                  <span>Funding: {Math.round(startup.match_details?.funding * 100)}%</span>
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
