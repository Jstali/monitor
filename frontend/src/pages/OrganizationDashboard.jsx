import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { organizationAPI, monitoringAPI, screenshotAPI, workflowAPI } from '../services/api';
import { Users, Settings, Activity, Image, LogOut, Download, Eye, FileText, Play, Layers } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './OrganizationDashboard.css';
import AuthenticatedImage from '../components/AuthenticatedImage';
import WorkflowModal from '../components/WorkflowModal';

const OrganizationDashboard = () => {
  const { user, logout } = useAuth();
  const [organization, setOrganization] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [screenshots, setScreenshots] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [screenshotInterval, setScreenshotInterval] = useState(10);
  const [processing, setProcessing] = useState(false);
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [workflowData, setWorkflowData] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [orgRes, empRes, sessRes] = await Promise.all([
        organizationAPI.getById(user.organization_id),
        organizationAPI.getEmployees(user.organization_id),
        monitoringAPI.getSessions(),
      ]);
      setOrganization(orgRes.data);
      setEmployees(empRes.data);
      setSessions(sessRes.data);
      setScreenshotInterval(orgRes.data.screenshot_interval);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateScreenshotInterval = async () => {
    try {
      await organizationAPI.update(user.organization_id, {
        screenshot_interval: screenshotInterval,
      });
      alert('Screenshot interval updated successfully');
    } catch (error) {
      alert('Failed to update interval');
    }
  };

  const viewEmployeeDetails = async (employee) => {
    setSelectedEmployee(employee);
    try {
      const sessRes = await monitoringAPI.getSessions({ employee_id: employee.id });
      setSessions(sessRes.data);
    } catch (error) {
      console.error('Failed to load employee sessions:', error);
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
      alert('Failed to load session details. Please try again.');
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

  const extractScreenshotData = async (screenshotId) => {
    try {
      await screenshotAPI.extract(screenshotId);
      // Refresh screenshots
      const res = await screenshotAPI.getSessionScreenshots(selectedSession.id);
      setScreenshots(res.data);
    } catch (error) {
      console.error('Failed to extract screenshot data:', error);
      alert('Failed to extract screenshot data');
    }
  };

  const handleExtractAll = async () => {
    if (!screenshots || screenshots.length === 0) {
      alert('No screenshots available to extract.');
      return;
    }
    
    if (!selectedSession) {
      alert('Please select a session first.');
      return;
    }

    setProcessing(true);
    try {
      // Step 1: Extract data from all screenshots
      const unprocessed = screenshots.filter(s => !s.is_processed);
      let itemsToProcess = unprocessed.length > 0 ? unprocessed : screenshots;
      
      console.log(`Extracting data from ${itemsToProcess.length} screenshots...`);
      
      let processedCount = 0;
      for (const screenshot of itemsToProcess) {
        try {
          await screenshotAPI.extract(screenshot.id);
          processedCount++;
        } catch (err) {
          console.error(`Failed to extract ${screenshot.id}:`, err);
        }
      }
      
      console.log(`Extraction complete. Processed: ${processedCount}`);
      
      // Step 2: Fetch workflow data
      console.log('Fetching workflow data...');
      const workflowRes = await workflowAPI.getSessionDiagram(selectedSession.id, 'json');
      setWorkflowData(workflowRes.data);
      
      // Step 3: Show modal
      setShowWorkflowModal(true);
      
      // Refresh session data in background
      if (selectedSession) {
        await viewSessionDetails(selectedSession);
      }
    } catch (error) {
      console.error('Extraction or workflow generation failed:', error);
      alert('Failed to generate workflow. Check console for details.');
    } finally {
      setProcessing(false);
    }
  };

  const handleGenerateWorkflow = async (format = 'html') => {
    if (!selectedSession) return;

    try {
      const response = await workflowAPI.getSessionDiagram(selectedSession.id, format);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `workflow_session_${selectedSession.id}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to generate workflow:', error);
      alert('Failed to generate workflow');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  // Calculate statistics
  const activeEmployees = employees.filter(e => e.is_active).length;
  const totalSessions = sessions.length;
  const activeSessions = sessions.filter(s => s.is_active).length;

  // Activity type distribution
  const activityTypes = activities.reduce((acc, act) => {
    acc[act.activity_type] = (acc[act.activity_type] || 0) + 1;
    return acc;
  }, {});

  const activityData = Object.entries(activityTypes).map(([type, count]) => ({
    name: type,
    value: count,
  }));

  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>{organization?.name}</h1>
          <p>Organization Dashboard</p>
        </div>
        <button onClick={logout} className="btn btn-secondary">
          <LogOut size={18} />
          Logout
        </button>
      </header>

      <div className="dashboard-content">
        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <Users size={24} className="stat-icon" />
            <div>
              <div className="stat-value">{activeEmployees}</div>
              <div className="stat-label">Active Employees</div>
            </div>
          </div>
          <div className="stat-card">
            <Activity size={24} className="stat-icon" />
            <div>
              <div className="stat-value">{totalSessions}</div>
              <div className="stat-label">Total Sessions</div>
            </div>
          </div>
          <div className="stat-card">
            <Activity size={24} className="stat-icon active" />
            <div>
              <div className="stat-value">{activeSessions}</div>
              <div className="stat-label">Active Sessions</div>
            </div>
          </div>
          <div className="stat-card">
            <Image size={24} className="stat-icon" />
            <div>
              <div className="stat-value">{screenshots.length}</div>
              <div className="stat-label">Screenshots</div>
            </div>
          </div>
        </div>

        {/* Settings */}
        <div className="card">
          <h2>
            <Settings size={20} />
            Settings
          </h2>
          <div className="settings-form">
            <div className="form-group">
              <label className="label">Screenshot Interval (seconds)</label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="number"
                  className="input"
                  value={screenshotInterval}
                  onChange={(e) => setScreenshotInterval(Number(e.target.value))}
                  min="5"
                  max="300"
                />
                <button onClick={updateScreenshotInterval} className="btn btn-primary">
                  Update
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Employees List */}
        <div className="card">
          <h2>
            <Users size={20} />
            Employees
          </h2>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.id}>
                    <td>{emp.name}</td>
                    <td>{emp.email}</td>
                    <td>
                      <span className={`badge badge-${emp.role === 'admin' ? 'primary' : 'secondary'}`}>
                        {emp.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${emp.is_active ? 'success' : 'danger'}`}>
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => viewEmployeeDetails(emp)}
                        className="btn btn-primary btn-sm"
                      >
                        <Eye size={16} />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Employee Sessions */}
        {selectedEmployee && (
          <div className="card">
            <h2>Sessions for {selectedEmployee.name}</h2>
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
                          <Eye size={16} />
                          Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Session Details */}
        {selectedSession && (
          <>
            {/* Activity Chart */}
            {activities.length > 0 && (
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h2>Activity Distribution</h2>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                      onClick={() => handleGenerateWorkflow('html')} 
                      className="btn btn-secondary btn-sm"
                      title="Generate Workflow Diagram"
                    >
                      <Layers size={16} />
                      Generate Workflow
                    </button>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={activityData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {activityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Screenshots Gallery */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>
                  <Image size={20} />
                  Screenshots ({screenshots.length})
                </h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    onClick={handleExtractAll} 
                    className="btn btn-primary btn-sm"
                    disabled={processing || !screenshots.some(s => !s.is_processed)}
                  >
                    {processing ? 'Processing...' : 'Extract All Data'}
                  </button>
                </div>
              </div>
              
              {screenshots.length === 0 ? (
                <div className="no-data-message" style={{ padding: '20px', textAlign: 'center', color: '#6b7280' }}>
                  No screenshots captured for this session.
                </div>
              ) : (
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
                          {new Date(screenshot.timestamp).toLocaleTimeString()}
                        </div>
                        <div className="screenshot-actions">
                          <button
                            onClick={() => downloadScreenshot(screenshot.id)}
                            className="btn btn-sm btn-secondary"
                            title="Download"
                          >
                            <Download size={16} />
                          </button>
                          {!screenshot.is_processed && (
                            <button
                              onClick={() => extractScreenshotData(screenshot.id)}
                              className="btn btn-sm btn-primary"
                              title="Extract Data"
                            >
                              Extract
                            </button>
                          )}
                        </div>
                      </div>
                      {screenshot.is_processed && screenshot.extracted_text && (
                        <div className="screenshot-text">
                          <strong>Extracted:</strong> {screenshot.extracted_text.substring(0, 100)}...
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Activities List */}
            <div className="card">
              <h2>Activities</h2>
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
      {/* Workflow Modal */}
      <WorkflowModal 
        isOpen={showWorkflowModal}
        onClose={() => setShowWorkflowModal(false)}
        workflowData={workflowData}
      />
    </div>
  );
};

export default OrganizationDashboard;
