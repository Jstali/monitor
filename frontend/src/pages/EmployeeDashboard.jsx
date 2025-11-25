
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { monitoringAPI, screenshotAPI, workflowAPI } from '../services/api';
import { Play, Square, RefreshCw, Clock, Image, Activity, Download, FileText, Layers, TrendingUp, LogOut } from 'lucide-react';
import AuthenticatedImage from '../components/AuthenticatedImage';

import ProcessMiningModal from '../components/ProcessMiningModal';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import './EmployeeDashboard.css';
import { formatToIST, formatTimeToIST } from '../utils/dateUtils';

const EmployeeDashboard = () => {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [screenshots, setScreenshots] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [showProcessMining, setShowProcessMining] = useState(false);
  const [showCredentialsModal, setShowCredentialsModal] = useState(false);
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [credentialsError, setCredentialsError] = useState('');
  const [credentialsStatus, setCredentialsStatus] = useState({ has_credentials: false, masked_email: null });
  const [showUpdateCredentials, setShowUpdateCredentials] = useState(false);

  useEffect(() => {
    loadData();
    loadCredentialsStatus();
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

  const loadCredentialsStatus = async () => {
    try {
      const res = await monitoringAPI.getCredentialsStatus();
      setCredentialsStatus(res.data);
    } catch (error) {
      console.error('Failed to load credentials status:', error);
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

  const handleExtractAll = async () => {
    if (!selectedSession) return;
    
    try {
      setProcessing(true);
      
      // Get all unprocessed screenshot IDs
      const unprocessed = screenshots.filter(s => !s.is_processed);
      
      if (unprocessed.length === 0) {
        alert('All screenshots are already processed!');
        setProcessing(false);
        return;
      }
      
      const screenshotIds = unprocessed.map(s => s.id);
      
      // Use batch extraction API
      await screenshotAPI.extractBatch(screenshotIds);
      
      // Refresh screenshots to get updated data
      const screenshotsRes = await screenshotAPI.getSessionScreenshots(selectedSession.id);
      setScreenshots(screenshotsRes.data);
      
      alert(`Successfully processed ${screenshotIds.length} screenshots!`);
      
      // Automatically show process mining analysis
      setShowProcessMining(true);
    } catch (error) {
      console.error('Extraction or workflow generation failed:', error);
      alert('Failed to extract data. Check console for details.');
    } finally {
      setProcessing(false);
    }
  };



  const handleStartSession = async () => {
    // Show credentials modal first
    setShowCredentialsModal(true);
  };

  const handleSubmitCredentials = async () => {
    if (!credentials.email || !credentials.password) {
      setCredentialsError('Please enter both email and password');
      return;
    }

    try {
      setLoading(true);
      setCredentialsError('');
      
      // Start session with credentials
      await monitoringAPI.startSession({
        agent_email: credentials.email,
        agent_password: credentials.password
      });
      
      // Refresh credentials status
      await loadCredentialsStatus();
      
      // Close modal and refresh data
      setShowCredentialsModal(false);
      setCredentials({ email: '', password: '' });
      await loadData();
    } catch (error) {
      console.error('Failed to start session:', error);
      setCredentialsError(error.response?.data?.error || 'Failed to start monitoring session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateCredentials = async () => {
    if (!credentials.email || !credentials.password) {
      setCredentialsError('Please enter both email and password');
      return;
    }

    try {
      setLoading(true);
      setCredentialsError('');
      
      // Update credentials
      await monitoringAPI.updateAgentCredentials({
        agent_email: credentials.email,
        agent_password: credentials.password
      });
      
      // Refresh credentials status
      await loadCredentialsStatus();
      
      // Close modal
      setShowUpdateCredentials(false);
      setCredentials({ email: '', password: '' });
      alert('Credentials updated successfully!');
    } catch (error) {
      console.error('Failed to update credentials:', error);
      setCredentialsError(error.response?.data?.error || 'Failed to update credentials. Please try again.');
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
        {/* Agent Credentials Management */}
        <div className="card">
          <h2>
            <Activity size={20} />
            Agent Credentials
          </h2>
          <div style={{ marginTop: '1rem' }}>
            {credentialsStatus.has_credentials ? (
              <div style={{ 
                padding: '1rem', 
                backgroundColor: '#d1fae5', 
                borderRadius: '8px',
                border: '1px solid #a7f3d0'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ color: '#065f46' }}>✓ Credentials Stored</strong>
                    <p style={{ margin: '0.5rem 0 0 0', color: '#047857', fontSize: '14px' }}>
                      Email: {credentialsStatus.masked_email}
                    </p>
                    <p style={{ margin: '0.5rem 0 0 0', color: '#6b7280', fontSize: '13px' }}>
                      Your agent credentials are securely stored. You can update them anytime.
                    </p>
                  </div>
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowUpdateCredentials(true);
                      setCredentials({ email: '', password: '' });
                      setCredentialsError('');
                    }}
                    style={{ marginLeft: '1rem' }}
                  >
                    Update Credentials
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ 
                padding: '1rem', 
                backgroundColor: '#fef3c7', 
                borderRadius: '8px',
                border: '1px solid #fbbf24'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ color: '#92400e' }}>⚠ No Credentials Stored</strong>
                    <p style={{ margin: '0.5rem 0 0 0', color: '#78350f', fontSize: '14px' }}>
                      You need to provide agent credentials to start monitoring.
                    </p>
                    <p style={{ margin: '0.5rem 0 0 0', color: '#6b7280', fontSize: '13px' }}>
                      Credentials will be requested when you click "Start Monitoring".
                    </p>
                  </div>
                  <button
                    className="btn btn-primary"
                    onClick={() => {
                      setShowUpdateCredentials(true);
                      setCredentials({ email: '', password: '' });
                      setCredentialsError('');
                    }}
                    style={{ marginLeft: '1rem' }}
                  >
                    Set Credentials
                  </button>
                </div>
              </div>
            )}
          </div>
          <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: '#f3f4f6', borderRadius: '6px', fontSize: '13px', color: '#6b7280' }}>
            <strong>Note:</strong> These credentials are used by the monitoring agent. 
            Make sure to set JWT_TOKEN in agent/.env file (get it from browser Local Storage after logging in).
          </div>
        </div>

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
                  Started at {formatToIST(currentSession.start_time)}
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
                    <td>{formatToIST(session.start_time)}</td>
                    <td>{formatToIST(session.end_time)}</td>
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>
                  <Image size={20} />
                  Screenshots ({screenshots.length})
                </h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    onClick={() => setShowProcessMining(true)}
                    className="btn btn-primary btn-sm"
                    disabled={processing || screenshots.length === 0}
                    title="View Workflow Analysis"
                  >
                    <TrendingUp size={16} />
                    View Analysis
                  </button>
                  <button 
                    onClick={handleExtractAll} 
                    className="btn btn-primary btn-sm"
                    disabled={processing || !screenshots.some(s => !s.is_processed)}
                  >
                    {processing ? 'Processing...' : 'Extract All Data'}
                  </button>
                </div>
              </div>
              <div className="screenshots-grid">
                {screenshots.map((screenshot) => (
                  <div key={screenshot.id} className="screenshot-card">
                    <div className="screenshot-image-container">
                      <AuthenticatedImage 
                        url={`/screenshots/${screenshot.id}/file`}
                        alt={`Screenshot ${screenshot.id}`}
                        className="screenshot-image"
                        onClick={() => window.open(`${import.meta.env.VITE_API_URL || 'http://localhost:5001/api'}/screenshots/${screenshot.id}/file?token=${localStorage.getItem('token')}`, '_blank')}
                      />
                    </div>
                    <div className="screenshot-info">
                      <div className="screenshot-time">
                        {formatTimeToIST(screenshot.timestamp)}
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
                        <td>{formatTimeToIST(activity.timestamp)}</td>
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


      
      {/* Process Mining Modal */}
      {showProcessMining && selectedSession && (
        <ProcessMiningModal 
          sessionId={selectedSession.id}
          onClose={() => setShowProcessMining(false)}
          apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:3232/api'}
          token={localStorage.getItem('token')}
        />
      )}

      {/* Credentials Modal (for starting session) */}
      {showCredentialsModal && (
        <div className="modal-overlay" onClick={() => setShowCredentialsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Enter Agent Credentials</h2>
              <button 
                className="modal-close" 
                onClick={() => {
                  setShowCredentialsModal(false);
                  setCredentials({ email: '', password: '' });
                  setCredentialsError('');
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
                Please enter your email and password for the monitoring agent. 
                These credentials will be securely stored and used by the agent to authenticate.
              </p>
              
              {credentialsStatus.has_credentials && (
                <div style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#dbeafe', color: '#1e40af', borderRadius: '4px', fontSize: '14px' }}>
                  <strong>Note:</strong> You have credentials stored ({credentialsStatus.masked_email}). 
                  You can update them or use the existing ones.
                </div>
              )}
              
              {credentialsError && (
                <div className="error" style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#fee', color: '#c33', borderRadius: '4px' }}>
                  {credentialsError}
                </div>
              )}

              <div className="form-group">
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={credentials.email}
                  onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                  placeholder="your.email@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Password</label>
                <input
                  type="password"
                  className="input"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setShowCredentialsModal(false);
                  setCredentials({ email: '', password: '' });
                  setCredentialsError('');
                }}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSubmitCredentials}
                disabled={loading}
              >
                {loading ? 'Starting...' : 'Start Monitoring'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Update Credentials Modal */}
      {showUpdateCredentials && (
        <div className="modal-overlay" onClick={() => setShowUpdateCredentials(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{credentialsStatus.has_credentials ? 'Update' : 'Set'} Agent Credentials</h2>
              <button 
                className="modal-close" 
                onClick={() => {
                  setShowUpdateCredentials(false);
                  setCredentials({ email: '', password: '' });
                  setCredentialsError('');
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
                {credentialsStatus.has_credentials 
                  ? 'Update your agent credentials. These will be used by the monitoring agent.'
                  : 'Set your agent credentials. These will be securely stored and used by the monitoring agent to authenticate.'}
              </p>
              
              {credentialsError && (
                <div className="error" style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#fee', color: '#c33', borderRadius: '4px' }}>
                  {credentialsError}
                </div>
              )}

              <div className="form-group">
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={credentials.email}
                  onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                  placeholder="your.email@example.com"
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Password</label>
                <input
                  type="password"
                  className="input"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setShowUpdateCredentials(false);
                  setCredentials({ email: '', password: '' });
                  setCredentialsError('');
                }}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleUpdateCredentials}
                disabled={loading}
              >
                {loading ? 'Saving...' : credentialsStatus.has_credentials ? 'Update Credentials' : 'Save Credentials'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeeDashboard;
