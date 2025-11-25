import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { organizationAPI, employeeAPI, monitoringAPI, screenshotAPI, workflowAPI } from '../services/api';
import { Users, Settings, Activity, Image, LogOut, Download, Eye, FileText, Play, Layers, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './OrganizationDashboard.css';
import AuthenticatedImage from '../components/AuthenticatedImage';
import { formatToIST, formatTimeToIST } from '../utils/dateUtils';
import WorkflowModal from '../components/WorkflowModal';
import MonitoringConfigManager from '../components/MonitoringConfigManager';
import ProcessMiningModal from '../components/ProcessMiningModal';

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
  const [managerProfile, setManagerProfile] = useState(null);
  const [showProcessMining, setShowProcessMining] = useState(false);

  useEffect(() => {
    loadData();
    loadManagerProfile();
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

  const loadManagerProfile = async () => {
    try {
      const response = await employeeAPI.getProfile();
      setManagerProfile(response.data);
    } catch (error) {
      console.error('Failed to load manager profile:', error);
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

  const handleAssignManager = async (employeeId, managerId) => {
    try {
      await employeeAPI.assignManager(employeeId, managerId || null);
      // Refresh employees list
      const empRes = await organizationAPI.getEmployees(user.organization_id);
      setEmployees(empRes.data);
      // Refresh manager profile
      await loadManagerProfile();
    } catch (error) {
      console.error('Failed to assign manager:', error);
      alert('Failed to assign manager. Please try again.');
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
      await screenshotAPI.extractData(screenshotId);
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
      // Validate that we have screenshots
      if (!screenshots || screenshots.length === 0) {
        alert('No screenshots available. Please select a session with screenshots.');
        setProcessing(false);
        return;
      }

      // Get all unprocessed screenshot IDs
      const unprocessed = screenshots.filter(s => !s.is_processed);
      
      if (unprocessed.length === 0) {
        alert('All screenshots are already processed!');
        setProcessing(false);
        return;
      }
      
      const allScreenshotIds = unprocessed.map(s => s.id);
      
      console.log(`Extracting data from ${allScreenshotIds.length} screenshots...`);
      
      // Validate screenshot IDs
      if (!allScreenshotIds || allScreenshotIds.length === 0) {
        alert('No valid screenshot IDs found.');
        setProcessing(false);
        return;
      }
      
      // Process in batches of 50 (backend limit)
      const BATCH_SIZE = 50;
      const batches = [];
      for (let i = 0; i < allScreenshotIds.length; i += BATCH_SIZE) {
        batches.push(allScreenshotIds.slice(i, i + BATCH_SIZE));
      }
      
      console.log(`Processing ${batches.length} batch(es) of up to ${BATCH_SIZE} screenshots each...`);
      
      let totalProcessed = 0;
      let totalFailed = 0;
      
      // Process each batch
      for (let i = 0; i < batches.length; i++) {
        const batch = batches[i];
        console.log(`Processing batch ${i + 1}/${batches.length} (${batch.length} screenshots)...`);
        
        try {
          const response = await screenshotAPI.extractBatch(batch);
          console.log(`Batch ${i + 1} response:`, response.data);
          
          totalProcessed += response.data.processed_count || batch.length;
          totalFailed += response.data.failed_count || 0;
        } catch (batchError) {
          console.error(`Batch ${i + 1} failed:`, batchError);
          totalFailed += batch.length;
        }
      }
      
      console.log(`Extraction complete. Processed: ${totalProcessed}, Failed: ${totalFailed}`);
      console.log('Fetching workflow data...');
      
      // Fetch workflow data in JSON format
      const workflowRes = await workflowAPI.getSessionDiagram(selectedSession.id, 'json');
      setWorkflowData(workflowRes.data);
      
      // Show modal
      setShowWorkflowModal(true);
      
      // Refresh session data in background
      if (selectedSession) {
        await viewSessionDetails(selectedSession);
      }
      
      alert(`Successfully processed ${totalProcessed} screenshots!${totalFailed > 0 ? ` (${totalFailed} failed)` : ''}`);
    } catch (error) {
      console.error('Extraction or workflow generation failed:', error);
      console.error('Error details:', error.response?.data);
      alert(`Failed to extract data: ${error.response?.data?.error || error.message}`);
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

  const handleViewAnalysis = async () => {
    if (!selectedSession) return;
    
    try {
      setProcessing(true);
      // Fetch the workflow data in JSON format
      const response = await workflowAPI.getSessionDiagram(selectedSession.id, 'json');
      setWorkflowData(response.data);
      setShowWorkflowModal(true);
    } catch (error) {
      console.error('Failed to load analysis:', error);
      alert('Failed to load analysis. Please try extracting data first.');
    } finally {
      setProcessing(false);
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

        {/* Manager Profile */}
        {managerProfile && ['admin', 'super_admin'].includes(managerProfile.role) && (
          <div className="card">
            <h2>
              <Users size={20} />
              Manager Profile
            </h2>
            <div className="profile-info" style={{ padding: '1rem' }}>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Name:</strong> {managerProfile.name}
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Email:</strong> {managerProfile.email}
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <strong>Role:</strong> {managerProfile.role === 'super_admin' ? 'Super Admin' : 'Manager'}
              </div>
              {managerProfile.managed_employees_count !== undefined && (
                <div>
                  <strong>Employees Under Management:</strong> {managerProfile.managed_employees_count}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Monitoring Configuration */}
        {managerProfile && ['admin', 'super_admin'].includes(managerProfile.role) && (
          <div className="card">
            <MonitoringConfigManager 
              apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:3535/api'}
              token={localStorage.getItem('token')}
            />
          </div>
        )}

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
                  <th>Status</th>
                  {managerProfile?.role === 'super_admin' && <th>Manager</th>}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {/* Super admin sees ALL users (employees + managers), Admin sees only their assigned employees */}
                {(managerProfile?.role === 'super_admin' 
                  ? employees 
                  : employees.filter(emp => emp.role === 'employee')
                ).map((emp) => (
                  <tr key={emp.id}>
                    <td>{emp.name}</td>
                    <td>{emp.email}</td>
                    <td>
                      <span className={`badge badge-${emp.is_active ? 'success' : 'danger'}`}>
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    {managerProfile?.role === 'super_admin' && (
                      <td>
                        {/* Only show manager dropdown for employees, not for admins/super_admins */}
                        {emp.role === 'employee' ? (
                          <select
                            value={emp.manager_id || ''}
                            onChange={(e) => handleAssignManager(emp.id, e.target.value)}
                            className="input"
                            style={{ padding: '0.25rem', fontSize: '0.875rem' }}
                          >
                            <option value="">Unassigned</option>
                            {employees.filter(e => ['admin', 'super_admin'].includes(e.role)).map(manager => (
                              <option key={manager.id} value={manager.id}>
                                {manager.name}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <span className="badge badge-primary">{emp.role === 'super_admin' ? 'Super Admin' : 'Manager'}</span>
                        )}
                      </td>
                    )}
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
            {/* Activity Distribution */}
            {activities.length > 0 && (
              <div className="card">
                <h2>Activity Distribution</h2>
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
                    onClick={() => setShowProcessMining(true)}
                    className="btn btn-primary btn-sm"
                    disabled={processing || screenshots.length === 0}
                    title="View Process Mining Diagram"
                  >
                    <TrendingUp size={16} />
                    Process Mining
                  </button>
                  <button 
                    onClick={handleViewAnalysis}
                    className="btn btn-secondary btn-sm"
                    disabled={processing || screenshots.length === 0}
                    title="View Workflow Analysis"
                  >
                    <Layers size={16} />
                    View Analysis
                  </button>
                  <button 
                    onClick={handleExtractAll} 
                    className="btn btn-secondary btn-sm"
                    disabled={processing || !screenshots || screenshots.length === 0 || !screenshots.some(s => !s.is_processed)}
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
      
      {/* Process Mining Modal */}
      {showProcessMining && selectedSession && (
        <ProcessMiningModal 
          sessionId={selectedSession.id}
          onClose={() => setShowProcessMining(false)}
          apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:5001/api'}
          token={localStorage.getItem('token')}
        />
      )}
    </div>
  );
};

export default OrganizationDashboard;
