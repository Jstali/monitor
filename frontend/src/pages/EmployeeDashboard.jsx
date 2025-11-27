
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { monitoringAPI, screenshotAPI, workflowAPI } from '../services/api';
import { Play, Square, RefreshCw, Clock, Image, Activity, Download, FileText, Layers, TrendingUp, LogOut } from 'lucide-react';
import AuthenticatedImage from '../components/AuthenticatedImage';

import ProcessMiningModal from '../components/ProcessMiningModal';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import './EmployeeDashboard.css';
import { formatToIST, formatTimeToIST } from '../utils/dateUtils';
import BackgroundAnimation from '../components/BackgroundAnimation';

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

  useEffect(() => {
    loadData();
    const interval = setInterval(loadCurrentSession, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      // Load sessions history
      try {
        const sessRes = await monitoringAPI.getSessions();
        setSessions(sessRes.data);
      } catch (error) {
        console.error('Failed to load sessions history:', error);
      }

      // Load current session (Critical for UI state)
      try {
        const currentRes = await monitoringAPI.getCurrentSession();
        setCurrentSession(currentRes.data.session);
      } catch (error) {
        console.error('Failed to load current session:', error);
      }
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
    try {
      setLoading(true);
      
      // Start session
      await monitoringAPI.startSession();
      
      // Refresh data
      await loadData();
    } catch (error) {
      console.error('Failed to start session:', error);
      alert(`Failed to start monitoring session: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStopSession = async () => {
    try {
      setLoading(true);
      
      // Optimistic update: Clear session immediately
      setCurrentSession(null);
      
      console.log('Stopping monitoring session...');
      await monitoringAPI.stopSession();
      
      // Refresh data to ensure sync
      await loadData();
      
    } catch (error) {
      console.error('Failed to stop session:', error);
      
      // If session is already stopped (404), just refresh
      if (error.response && error.response.status === 404) {
        await loadData();
        return;
      }

      // Revert state on error (optional, but safer)
      // await loadData(); 
      
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
      <BackgroundAnimation />
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
    </div>
  );
};

export default EmployeeDashboard;
