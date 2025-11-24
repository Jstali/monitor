import React, { useState, useEffect } from 'react';
import { X, Download, FileText, BarChart3, Loader } from 'lucide-react';
import ProcessFlowDiagram from './ProcessFlowDiagram';
import './ProcessMiningModal.css';

const ProcessMiningModal = ({ sessionId, onClose, apiUrl, token }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [diagramUrl, setDiagramUrl] = useState(null);
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [activityDetails, setActivityDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    loadProcessMap();
  }, [sessionId]);

  const loadProcessMap = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch statistics and summary in parallel
      const [statsResponse, summaryResponse] = await Promise.all([
        fetch(
          `${apiUrl}/workflow/session/${sessionId}/process-map?format=json`,
          { headers: { 'Authorization': `Bearer ${token}` } }
        ),
        fetch(
          `${apiUrl}/workflow/session/${sessionId}/diagram?format=json`,
          { headers: { 'Authorization': `Bearer ${token}` } }
        )
      ]);

      if (!statsResponse.ok) {
        throw new Error('Failed to load process map');
      }

      const statsData = await statsResponse.json();
      setStatistics(statsData.statistics);

      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        // Use screenshot_workflow for detailed steps, or activity_summary as fallback
        setSummary(summaryData.screenshot_workflow || summaryData.activity_summary || 'No summary available.');
        setTimeline(summaryData.timeline); 
      }

      // Set diagram URL for image display
      setDiagramUrl(
        `${apiUrl}/workflow/session/${sessionId}/process-map?format=png&token=${token}`
      );

    } catch (err) {
      console.error('Error loading process map:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadDiagram = () => {
    const link = document.createElement('a');
    link.href = `${apiUrl}/workflow/session/${sessionId}/process-map?format=png`;
    link.download = `process_map_session_${sessionId}.png`;
    link.click();
  };

  const downloadEventLog = () => {
    const link = document.createElement('a');
    link.href = `${apiUrl}/workflow/session/${sessionId}/process-map?format=csv`;
    link.download = `event_log_session_${sessionId}.csv`;
    link.click();
  };

  const handleNodeClick = async (activityName) => {
    setSelectedActivity(activityName);
    setLoadingDetails(true);
    
    try {
      // Fetch screenshots for this activity
      const response = await fetch(
        `${apiUrl}/screenshots/session/${sessionId}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      if (!response.ok) throw new Error('Failed to load screenshots');
      
      const screenshots = await response.json();
      
      // Filter screenshots by activity_name
      const activityScreenshots = screenshots.filter(
        s => s.activity_name === activityName
      );
      
      // Fetch activities for this session using correct endpoint
      const activitiesResponse = await fetch(
        `${apiUrl}/monitoring/activities?session_id=${sessionId}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      let activities = [];
      if (activitiesResponse.ok) {
        activities = await activitiesResponse.json();
      }
      
      // Filter activities by application name
      const activityLogs = activities.filter(
        a => a.application_name === activityName || 
             (a.url && a.url.includes(activityName))
      );
      
      setActivityDetails({
        name: activityName,
        screenshots: activityScreenshots,
        activities: activityLogs,
        totalTime: activityScreenshots.length * 10, // Approximate (screenshots * interval)
        count: activityScreenshots.length
      });
    } catch (err) {
      console.error('Error loading activity details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  return (
    <div className="process-mining-modal-overlay" onClick={onClose}>
      <div className="process-mining-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>
              <BarChart3 size={24} />
              Process Mining Analysis
            </h2>
            <p className="modal-subtitle">Session {sessionId} - Workflow Visualization</p>
          </div>
          <button onClick={onClose} className="close-button">
            <X size={20} />
          </button>
        </div>

        {loading && (
          <div className="loading-state">
            <Loader className="spinner" size={48} />
            <p>Generating process mining diagram...</p>
          </div>
        )}

        {error && (
          <div className="error-state">
            <p>Error: {error}</p>
            <button onClick={loadProcessMap} className="btn btn-primary">
              Retry
            </button>
          </div>
        )}

        {!loading && !error && statistics && (
          <>
            <div className="statistics-panel">
              <div className="stat-card">
                <div className="stat-label">Total Activities</div>
                <div className="stat-value">{statistics.total_activities}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Unique Activities</div>
                <div className="stat-value">{statistics.unique_activities}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Transitions</div>
                <div className="stat-value">{statistics.total_transitions}</div>
              </div>
            </div>
            
            {summary && (
              <div className="summary-panel">
                <h3>Activity Summary</h3>
                <div className="summary-content">
                  {summary.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </div>
            )}

            <div className="diagram-container">
              <div className="diagram-header">
                <h3>Process Flow Diagram</h3>
                <div className="diagram-actions">
                  <button onClick={downloadDiagram} className="btn btn-secondary btn-sm">
                    <Download size={16} />
                    Download PNG
                  </button>
                  <button onClick={downloadEventLog} className="btn btn-secondary btn-sm">
                    <FileText size={16} />
                    Export CSV
                  </button>
                </div>
              </div>

              <div className="diagram-viewer">
                <ProcessFlowDiagram 
                  statistics={statistics} 
                  timeline={timeline}
                  sessionId={sessionId}
                  apiUrl={apiUrl}
                  token={token}
                  onNodeClick={handleNodeClick}
                />
              </div>

              {selectedActivity && (
                <div className="activity-details-panel">
                  <div>
                  <div className="activity-details-header">
                    <h4>📊 {selectedActivity} - Detailed View</h4>
                    <button 
                      onClick={() => setSelectedActivity(null)}
                      className="close-details-btn"
                    >
                      <X size={16} />
                    </button>
                  </div>
                  
                  {loadingDetails ? (
                    <div className="details-loading">
                      <Loader className="spinner" size={24} />
                      <p>Loading activity details...</p>
                    </div>
                  ) : activityDetails ? (
                    <div className="activity-details-content">
                      <div className="details-stats">
                        <div className="detail-stat">
                          <span className="stat-label">Screenshots</span>
                          <span className="stat-value">{activityDetails.count}</span>
                        </div>
                        <div className="detail-stat">
                          <span className="stat-label">Est. Time</span>
                          <span className="stat-value">{Math.floor(activityDetails.totalTime / 60)}m</span>
                        </div>
                        <div className="detail-stat">
                          <span className="stat-label">Actions</span>
                          <span className="stat-value">{activityDetails.activities.length}</span>
                        </div>
                      </div>

                      {activityDetails.activities.length > 0 && (
                        <div className="activity-timeline">
                          <h5>Activity Timeline</h5>
                          <div className="timeline-list">
                            {activityDetails.activities.slice(0, 10).map((activity, idx) => (
                              <div key={idx} className="timeline-item">
                                <span className="timeline-time">
                                  {new Date(activity.timestamp).toLocaleTimeString()}
                                </span>
                                <span className="timeline-action">
                                  {activity.window_title || activity.url || 'Active'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {activityDetails.screenshots.length > 0 && (
                        <div className="activity-steps">
                          <h5>📝 Step-by-Step Activity Log</h5>
                          <p className="steps-description">
                            Extracted text from screenshots showing what the employee was doing:
                          </p>
                          <div className="steps-list">
                            {activityDetails.screenshots
                              .filter(s => s.extracted_text || s.extraction_data)
                              .slice(0, 10)
                              .map((screenshot, idx) => (
                              <div key={screenshot.id} className="step-item">
                                <div className="step-number">{idx + 1}</div>
                                <div className="step-content">
                                  <div className="step-time">
                                    {new Date(screenshot.timestamp).toLocaleTimeString()}
                                  </div>
                                  {screenshot.extraction_data && (
                                    <div className="step-details">
                                      <div className="step-app">
                                        <strong>App:</strong> {screenshot.activity_name || screenshot.extraction_data.app || 'Unknown'}
                                      </div>
                                      <div className="step-action">
                                        <strong>Action:</strong> {screenshot.extraction_data.action || 'Active'}
                                      </div>
                                      {screenshot.extraction_data.context && (
                                        <div className="step-context">
                                          <strong>Context:</strong> {screenshot.extraction_data.context}
                                        </div>
                                      )}
                                      {screenshot.extraction_data.details && (
                                        <div className="step-description">
                                          {screenshot.extraction_data.details}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                  {screenshot.extracted_text && !screenshot.extraction_data && (
                                    <div className="step-text">
                                      {screenshot.extracted_text.substring(0, 200)}
                                      {screenshot.extracted_text.length > 200 && '...'}
                                    </div>
                                  )}
                                  {!screenshot.extracted_text && !screenshot.extraction_data && (
                                    <div className="step-no-data">
                                      No extracted data available. Click "Extract" to analyze this screenshot.
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                          {activityDetails.screenshots.filter(s => !s.extracted_text && !s.extraction_data).length > 0 && (
                            <div className="extraction-notice">
                              ℹ️ Some screenshots haven't been analyzed yet. Use the "Extract All Data" button to process them.
                            </div>
                          )}
                        </div>
                      )}

                      {activityDetails.screenshots.length > 0 && (
                        <div className="activity-screenshots">
                          <h5>Screenshots ({activityDetails.screenshots.length})</h5>
                          <div className="screenshots-grid">
                            {activityDetails.screenshots.slice(0, 6).map((screenshot) => (
                              <div key={screenshot.id} className="screenshot-thumb">
                                <img 
                                  src={`${apiUrl}/screenshots/${screenshot.id}/file?token=${token}`}
                                  alt={`Screenshot at ${new Date(screenshot.timestamp).toLocaleTimeString()}`}
                                  onClick={() => window.open(`${apiUrl}/screenshots/${screenshot.id}/file?token=${token}`, '_blank')}
                                />
                                <span className="screenshot-time">
                                  {new Date(screenshot.timestamp).toLocaleTimeString()}
                                </span>
                              </div>
                            ))}
                          </div>
                          {activityDetails.screenshots.length > 6 && (
                            <p className="more-screenshots">
                              +{activityDetails.screenshots.length - 6} more screenshots
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  ) : null}
                  </div>
                </div>
              )}

              <div className="diagram-legend">
                <h4>Legend</h4>
                <div className="legend-items">
                  <div className="legend-item">
                    <div className="legend-color" style={{ backgroundColor: '#4CAF50' }}></div>
                    <span>Start Node</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{ backgroundColor: '#F44336' }}></div>
                    <span>End Node</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{ backgroundColor: '#2196F3' }}></div>
                    <span>High Frequency Activity</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{ backgroundColor: '#64B5F6' }}></div>
                    <span>Medium Frequency Activity</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{ backgroundColor: '#BBDEFB' }}></div>
                    <span>Low Frequency Activity</span>
                  </div>
                </div>
                <p className="legend-note">
                  <strong>Numbers on edges:</strong> Transition frequency (how many times users moved from one activity to another)
                </p>
                <p className="legend-note">
                  <strong>Numbers in nodes:</strong> Activity occurrence count
                </p>
              </div>
            </div>

            {statistics.activity_distribution && (
              <div className="activity-distribution">
                <h3>Activity Distribution</h3>
                <div className="distribution-list">
                  {Object.entries(statistics.activity_distribution)
                    .sort(([, a], [, b]) => b - a)
                    .map(([activity, count]) => (
                      <div key={activity} className="distribution-item">
                        <span className="activity-name">{activity}</span>
                        <div className="activity-bar-container">
                          <div 
                            className="activity-bar" 
                            style={{ 
                              width: `${(count / statistics.total_activities) * 100}%`,
                              backgroundColor: count >= statistics.total_activities * 0.5 ? '#2196F3' : '#64B5F6'
                            }}
                          ></div>
                          <span className="activity-count">{count}</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {statistics.top_transitions && statistics.top_transitions.length > 0 && (
              <div className="top-transitions">
                <h3>Top Transitions</h3>
                <table className="transitions-table">
                  <thead>
                    <tr>
                      <th>From</th>
                      <th>To</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statistics.top_transitions.map(([[from, to], count], index) => (
                      <tr key={index}>
                        <td>{from}</td>
                        <td>{to}</td>
                        <td><strong>{count}</strong></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ProcessMiningModal;
