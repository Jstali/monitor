import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { monitoringAPI, screenshotAPI } from '../services/api';
import { Activity, Image, LogOut, Clock, Download } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './EmployeeDashboard.css';

const EmployeeDashboard = () => {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [screenshots, setScreenshots] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadCurrentSession, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [sessRes, currentRes] = await Promise.all([
        monitoringAPI.getSessions(),
        monitoringAPI.getCurrentSession(),
      ]);
      setSessions(sessRes.data);
      setCurrentSession(currentRes.data.session);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentSession = async () => {
    try {
      const res = await monitoringAPI.getCurrentSession();
      setCurrentSession(res.data.session);
    } catch (error) {
      console.error('Failed to load current session:', error);
    }
  };

  const viewSessionDetails = async (session) => {
    setSelectedSession(session);
    try {
      const [screenshotsRes, activitiesRes] = await Promise.all([
        screenshotAPI.getSessionScreenshots(session.id),
        monitoringAPI.getActivities(session.id),
      ]);
      setScreenshots(screenshotsRes.data);
      setActivities(activitiesRes.data);
    } catch (error) {
      console.error('Failed to load session details:', error);
    }
  };

  const downloadScreenshot = async (screenshotId) => {
    try {
      const response = await screenshotAPI.getFile(screenshotId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `screenshot_${screenshotId}.png`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to download screenshot');
    }
  };

  const handleStartSession = async () => {
    try {
      setLoading(true);
      await monitoringAPI.startSession();
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Failed to start session:', error);
      alert('Failed to start monitoring session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStopSession = async () => {
    try {
      if (window.confirm('Are you sure you want to stop monitoring?')) {
        setLoading(true);
        console.log('Stopping monitoring session...');
        const response = await monitoringAPI.stopSession();
        console.log('Stop session response:', response.data);
        
        // Show success message
        alert('Monitoring stopped successfully!');
        
        // Refresh data
        await loadData();
      }
    } catch (error) {
      console.error('Failed to stop session:', error);
      console.error('Error details:', error.response?.data);
      alert(`Failed to stop monitoring session: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  // Calculate activity timeline for chart
  const activityTimeline = activities.reduce((acc, activity) => {
    const hour = new Date(activity.timestamp).getHours();
    const existing = acc.find(item => item.hour === hour);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ hour, count: 1 });
    }
    return acc;
  }, []).sort((a, b) => a.hour - b.hour);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Welcome, {user.name}</h1>
          <p>Employee Dashboard</p>
        </div>
        <button onClick={logout} className="btn btn-secondary">
          <LogOut size={18} />
          Logout
        </button>
      </header>

      <div className="dashboard-content">
        {/* Current Session Status */}
        <div className="card">
          <h2>
            <Activity size={20} />
            Current Session Status
          </h2>
          {currentSession ? (
            <div className="session-status active">
              <div className="status-indicator"></div>
              <div className="status-content">
                <div className="status-title">Monitoring Active</div>
                <div className="status-subtitle">
                  Started at {new Date(currentSession.start_time).toLocaleString()}
                </div>
                <div className="guidance-text">
                  <p><strong>Monitoring is active.</strong> Your screen activity is being recorded.</p>
                  <ul>
                    <li>Screenshots are taken every {currentSession.screenshot_interval || 10} seconds.</li>
                    <li>Active window titles and application names are logged.</li>
                    <li>You can stop monitoring at any time using the button below.</li>
                  </ul>
                </div>
                <button 
                  onClick={handleStopSession} 
                  className="btn btn-danger"
                  style={{ marginTop: '1rem' }}
                >
                  Stop Monitoring
                </button>
              </div>
            </div>
          ) : (
            <div className="session-status inactive">
              <div className="status-indicator"></div>
              <div className="status-content">
                <div className="status-title">No Active Session</div>
                <div className="status-subtitle">
                  Start monitoring to begin tracking your work activity.
                </div>
                <div className="guidance-text">
                  <p>When you start monitoring:</p>
                  <ul>
                    <li>Your screen will be captured periodically.</li>
                    <li>Your work activity will be logged for productivity tracking.</li>
                  </ul>
                </div>
                <button 
                  onClick={handleStartSession} 
                  className="btn btn-primary"
                  style={{ marginTop: '1rem' }}
                >
                  Start Monitoring
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <Activity size={24} className="stat-icon" />
            <div>
              <div className="stat-value">{sessions.length}</div>
              <div className="stat-label">Total Sessions</div>
            </div>
          </div>
          <div className="stat-card">
            <Clock size={24} className="stat-icon" />
            <div>
              <div className="stat-value">
                {Math.round(sessions.reduce((sum, s) => sum + (s.duration_seconds || 0), 0) / 3600)}h
              </div>
              <div className="stat-label">Total Time Tracked</div>
            </div>
          </div>
          <div className="stat-card">
            <Image size={24} className="stat-icon" />
            <div>
              <div className="stat-value">{screenshots.length}</div>
              <div className="stat-label">Screenshots Captured</div>
            </div>
          </div>
        </div>

        {/* Session History */}
        <div className="card">
          <h2>Session History</h2>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td>{new Date(session.start_time).toLocaleString()}</td>
                    <td>{session.end_time ? new Date(session.end_time).toLocaleString() : '-'}</td>
                    <td>{session.duration_seconds ? `${Math.round(session.duration_seconds / 60)} min` : '-'}</td>
                    <td>
                      <span className={`badge badge-${session.is_active ? 'success' : 'danger'}`}>
                        {session.is_active ? 'Active' : 'Ended'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => viewSessionDetails(session)}
                        className="btn btn-primary btn-sm"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Session Details */}
        {selectedSession && (
          <>
            {/* Activity Timeline Chart */}
            {activityTimeline.length > 0 && (
              <div className="card">
                <h2>Activity Timeline</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={activityTimeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" label={{ value: 'Hour', position: 'insideBottom', offset: -5 }} />
                    <YAxis label={{ value: 'Activities', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} name="Activity Count" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Screenshots */}
            <div className="card">
              <h2>
                <Image size={20} />
                Screenshots ({screenshots.length})
              </h2>
              <div className="screenshots-grid">
                {screenshots.map((screenshot) => (
                  <div key={screenshot.id} className="screenshot-card">
                    <div className="screenshot-info">
                      <div className="screenshot-time">
                        {new Date(screenshot.timestamp).toLocaleTimeString()}
                      </div>
                      <button
                        onClick={() => downloadScreenshot(screenshot.id)}
                        className="btn btn-sm btn-secondary"
                        title="Download"
                      >
                        <Download size={16} />
                      </button>
                    </div>
                    {screenshot.is_processed && screenshot.extracted_text && (
                      <div className="screenshot-text">
                        <strong>Extracted:</strong> {screenshot.extracted_text.substring(0, 100)}...
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Activities */}
            <div className="card">
              <h2>Activity Log</h2>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Type</th>
                      <th>Application</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activities.map((activity) => (
                      <tr key={activity.id}>
                        <td>{new Date(activity.timestamp).toLocaleTimeString()}</td>
                        <td>
                          <span className={`badge badge-${activity.activity_type === 'website' ? 'primary' : 'secondary'}`}>
                            {activity.activity_type}
                          </span>
                        </td>
                        <td>{activity.application_name || '-'}</td>
                        <td>{activity.url || activity.window_title || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EmployeeDashboard;
