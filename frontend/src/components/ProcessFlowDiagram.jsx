import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.css';

const ProcessFlowDiagram = ({ statistics, sessionId, apiUrl, token, onNodeClick }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!statistics || !containerRef.current) return;

    const { activity_distribution, top_transitions } = statistics;

    // Create nodes from activities
    const nodes = [];
    const maxCount = Math.max(...Object.values(activity_distribution));

    // Add START node
    nodes.push({
      id: 'START',
      label: 'START',
      shape: 'circle',
      color: {
        background: '#4CAF50',
        border: '#388E3C',
      },
      font: { color: 'white', size: 14, bold: true },
      size: 30,
      fixed: { x: false, y: false },
    });

    // Add activity nodes
    Object.entries(activity_distribution).forEach(([activity, count]) => {
      const freq = count / maxCount;
      let color;
      if (freq >= 0.7) {
        color = { background: '#2196F3', border: '#1976D2' };
      } else if (freq >= 0.3) {
        color = { background: '#64B5F6', border: '#42A5F5' };
      } else {
        color = { background: '#BBDEFB', border: '#90CAF9' };
      }

      nodes.push({
        id: activity,
        label: `${activity}\n(${count})`,
        shape: 'box',
        color,
        font: { color: 'white', size: 12, multi: true },
        margin: 10,
        borderWidth: 2,
        borderWidthSelected: 3,
        title: `Click to view details for ${activity}`, // Tooltip
      });
    });

    // Add END node
    nodes.push({
      id: 'END',
      label: 'END',
      shape: 'circle',
      color: {
        background: '#F44336',
        border: '#D32F2F',
      },
      font: { color: 'white', size: 14, bold: true },
      size: 30,
      fixed: { x: false, y: false },
    });

    // Create edges from transitions
    const edges = [];
    const maxTransition = top_transitions.length > 0 
      ? Math.max(...top_transitions.map(t => t[1])) 
      : 1;

    // Add START edge to first activity
    const firstActivity = Object.keys(activity_distribution)[0];
    if (firstActivity) {
      edges.push({
        from: 'START',
        to: firstActivity,
        label: '1',
        arrows: 'to',
        color: { color: '#607D8B', highlight: '#455A64' },
        width: 2,
        smooth: {
          enabled: true,
          type: 'curvedCW',
          roundness: 0.2,
        },
        font: { size: 11, color: '#424242', strokeWidth: 0 },
      });
    }

    // Add transition edges
    top_transitions.forEach(([[from, to], count]) => {
      const freq = count / maxTransition;
      let width, color;
      
      if (freq >= 0.7) {
        width = 4;
        color = { color: '#2196F3', highlight: '#1976D2' };
      } else if (freq >= 0.3) {
        width = 2.5;
        color = { color: '#64B5F6', highlight: '#42A5F5' };
      } else {
        width = 1.5;
        color = { color: '#BBDEFB', highlight: '#90CAF9' };
      }

      edges.push({
        from,
        to,
        label: String(count),
        arrows: 'to',
        color,
        width,
        smooth: {
          enabled: true,
          type: 'curvedCW',
          roundness: 0.2,
        },
        font: { size: 11, color: '#424242', strokeWidth: 0 },
      });
    });

    // Add END edge from last activity
    const lastActivity = Object.keys(activity_distribution)[Object.keys(activity_distribution).length - 1];
    if (lastActivity) {
      edges.push({
        from: lastActivity,
        to: 'END',
        label: '1',
        arrows: 'to',
        color: { color: '#607D8B', highlight: '#455A64' },
        width: 2,
        smooth: {
          enabled: true,
          type: 'curvedCW',
          roundness: 0.2,
        },
        font: { size: 11, color: '#424242', strokeWidth: 0 },
      });
    }

    // Create network
    const data = { nodes, edges };
    const options = {
      layout: {
        hierarchical: {
          enabled: true,
          direction: 'LR',
          sortMethod: 'directed',
          levelSeparation: 200,
          nodeSpacing: 150,
          treeSpacing: 200,
        },
      },
      physics: {
        enabled: false,
      },
      interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        hover: true,
        navigationButtons: true,
      },
      edges: {
        smooth: {
          enabled: true,
          type: 'curvedCW',
          roundness: 0.2,
        },
      },
    };

    if (networkRef.current) {
      networkRef.current.destroy();
    }

    networkRef.current = new Network(containerRef.current, data, options);

    // Add click event listener
    networkRef.current.on('click', async (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        
        // Don't show details for START/END nodes
        if (nodeId === 'START' || nodeId === 'END') return;
        
        setSelectedNode(nodeId);
        
        // Fetch activity details
        if (onNodeClick) {
          onNodeClick(nodeId);
        }
      }
    });

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
      }
    };
  }, [statistics, sessionId, apiUrl, token, onNodeClick]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '500px',
        border: '2px solid #e5e7eb',
        borderRadius: '12px',
        background: '#f8f9fa',
        cursor: 'pointer',
      }}
    />
  );
};

export default ProcessFlowDiagram;
