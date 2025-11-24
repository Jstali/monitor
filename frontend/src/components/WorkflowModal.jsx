import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import './WorkflowModal.css';

const WorkflowModal = ({ isOpen, onClose, workflowData }) => {
  const mermaidRef = useRef(null);

  useEffect(() => {
    if (isOpen && workflowData?.mermaid_diagram && mermaidRef.current) {
      mermaid.initialize({ startOnLoad: false, theme: 'default' });
      mermaidRef.current.innerHTML = workflowData.mermaid_diagram;
      mermaid.run({ nodes: [mermaidRef.current] });
    }
  }, [isOpen, workflowData]);

  if (!isOpen) return null;

  const generateSummary = () => {
    // screenshot_workflow is now a pre-formatted string from the backend
    if (!workflowData?.screenshot_workflow) return 'No workflow data available.';
    
    // Return the pre-formatted summary text directly
    return workflowData.screenshot_workflow;
  };

  return (
    <div className="workflow-modal-overlay" onClick={onClose}>
      <div className="workflow-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="workflow-modal-header">
          <h2>Workflow Analysis</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="workflow-modal-body">
          {/* Summary Section */}
          <div className="workflow-summary-section">
            <h3>Activity Summary</h3>
            <div className="workflow-summary-text">
              <pre>{generateSummary()}</pre>
            </div>
          </div>

          {/* Diagram Section */}
          <div className="workflow-diagram-section">
            <h3>Process Flow Diagram</h3>
            <div className="mermaid-container">
              <div ref={mermaidRef} className="mermaid"></div>
            </div>
          </div>
        </div>

        <div className="workflow-modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default WorkflowModal;
