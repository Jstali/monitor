import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Save, X, Shield } from 'lucide-react';
import './MonitoringConfigManager.css';

const MonitoringConfigManager = ({ apiUrl, token }) => {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingConfig, setEditingConfig] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    config_type: 'application',
    pattern: '',
    folder_name: '',
    is_active: true
  });

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const response = await fetch(`${apiUrl}/monitoring-config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setConfigs(data);
    } catch (error) {
      console.error('Failed to load configurations:', error);
      alert('Failed to load monitoring configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    try {
      const response = await fetch(`${apiUrl}/monitoring-config`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setShowAddForm(false);
        setFormData({
          config_type: 'application',
          pattern: '',
          folder_name: '',
          is_active: true
        });
        loadConfigs();
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to create configuration');
      }
    } catch (error) {
      console.error('Failed to create configuration:', error);
      alert('Failed to create configuration');
    }
  };

  const handleUpdate = async (id) => {
    try {
      const response = await fetch(`${apiUrl}/monitoring-config/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editingConfig)
      });

      if (response.ok) {
        setEditingConfig(null);
        loadConfigs();
      } else {
        alert('Failed to update configuration');
      }
    } catch (error) {
      console.error('Failed to update configuration:', error);
      alert('Failed to update configuration');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this configuration?')) {
      try {
        const response = await fetch(`${apiUrl}/monitoring-config/${id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
          loadConfigs();
        } else {
          alert('Failed to delete configuration');
        }
      } catch (error) {
        console.error('Failed to delete configuration:', error);
        alert('Failed to delete configuration');
      }
    }
  };

  const handleToggleActive = async (config) => {
    try {
      const response = await fetch(`${apiUrl}/monitoring-config/${config.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !config.is_active })
      });

      if (response.ok) {
        loadConfigs();
      }
    } catch (error) {
      console.error('Failed to toggle configuration:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading monitoring configurations...</div>;
  }

  return (
    <div className="monitoring-config-manager">
      <div className="config-header">
        <div>
          <h2>
            <Shield size={24} />
            Monitoring Configuration
          </h2>
          <p className="config-subtitle">
            Configure which applications and URLs to monitor. Only matching activities will be captured.
          </p>
        </div>
        <button onClick={() => setShowAddForm(true)} className="btn btn-primary">
          <Plus size={18} />
          Add Configuration
        </button>
      </div>

      <div className="config-info-box">
        <h4>📋 How It Works:</h4>
        <ul>
          <li><strong>Application:</strong> Monitor specific apps (e.g., "Cursor", "Slack")</li>
          <li><strong>URL:</strong> Monitor specific websites (e.g., "chatgpt.com", "figma.com")</li>
          <li><strong>Folder:</strong> Screenshots are saved to <code>screenshots/{'{folder_name}'}/</code></li>
          <li><strong>Active Only:</strong> Only active configurations are monitored</li>
        </ul>
      </div>

      {showAddForm && (
        <div className="config-form card">
          <h3>Add New Configuration</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Type</label>
              <select
                value={formData.config_type}
                onChange={(e) => setFormData({ ...formData, config_type: e.target.value })}
                className="form-control"
              >
                <option value="application">Application</option>
                <option value="url">URL</option>
              </select>
            </div>
            <div className="form-group">
              <label>Pattern</label>
              <input
                type="text"
                value={formData.pattern}
                onChange={(e) => setFormData({ ...formData, pattern: e.target.value })}
                placeholder={formData.config_type === 'application' ? 'e.g., Cursor, Slack' : 'e.g., chatgpt.com, github.com'}
                className="form-control"
              />
              <small>Case-insensitive matching</small>
            </div>
            <div className="form-group">
              <label>Folder Name</label>
              <input
                type="text"
                value={formData.folder_name}
                onChange={(e) => setFormData({ ...formData, folder_name: e.target.value })}
                placeholder="e.g., Cursor, ChatGPT"
                className="form-control"
              />
              <small>Screenshots saved to this folder</small>
            </div>
          </div>
          <div className="form-actions">
            <button 
              onClick={handleAdd} 
              className="btn btn-primary" 
              disabled={!formData.pattern || !formData.folder_name}
            >
              <Save size={16} />
              Save Configuration
            </button>
            <button onClick={() => setShowAddForm(false)} className="btn btn-secondary">
              <X size={16} />
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="configs-list">
        {configs.length === 0 ? (
          <div className="empty-state">
            <Shield size={48} />
            <p>No monitoring configurations yet</p>
            <p className="empty-subtitle">Add configurations to enable selective monitoring</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Pattern</th>
                <th>Folder</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs.map((config) => (
                <tr key={config.id}>
                  <td>
                    <span className={`badge badge-${config.config_type === 'application' ? 'primary' : 'secondary'}`}>
                      {config.config_type}
                    </span>
                  </td>
                  <td>
                    {editingConfig?.id === config.id ? (
                      <input
                        type="text"
                        value={editingConfig.pattern}
                        onChange={(e) => setEditingConfig({ ...editingConfig, pattern: e.target.value })}
                        className="form-control"
                      />
                    ) : (
                      <strong>{config.pattern}</strong>
                    )}
                  </td>
                  <td>
                    {editingConfig?.id === config.id ? (
                      <input
                        type="text"
                        value={editingConfig.folder_name}
                        onChange={(e) => setEditingConfig({ ...editingConfig, folder_name: e.target.value })}
                        className="form-control"
                      />
                    ) : (
                      <code>{config.folder_name}/</code>
                    )}
                  </td>
                  <td>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={config.is_active}
                        onChange={() => handleToggleActive(config)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                    <span className={`status-text ${config.is_active ? 'active' : 'inactive'}`}>
                      {config.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      {editingConfig?.id === config.id ? (
                        <>
                          <button onClick={() => handleUpdate(config.id)} className="btn btn-sm btn-primary">
                            <Save size={14} />
                          </button>
                          <button onClick={() => setEditingConfig(null)} className="btn btn-sm btn-secondary">
                            <X size={14} />
                          </button>
                        </>
                      ) : (
                        <>
                          <button onClick={() => setEditingConfig(config)} className="btn btn-sm btn-secondary">
                            <Edit2 size={14} />
                          </button>
                          <button onClick={() => handleDelete(config.id)} className="btn btn-sm btn-danger">
                            <Trash2 size={14} />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {configs.length > 0 && (
        <div className="config-summary">
          <p>
            <strong>{configs.filter(c => c.is_active).length}</strong> active configuration(s) | 
            <strong> {configs.length}</strong> total
          </p>
        </div>
      )}
    </div>
  );
};

export default MonitoringConfigManager;
