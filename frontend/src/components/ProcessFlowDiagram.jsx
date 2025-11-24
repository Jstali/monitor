import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.css';

const ProcessFlowDiagram = ({ statistics, timeline, sessionId, apiUrl, token, onNodeClick }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  // Default to aggregated view as requested ("application name need to show one time only")
  const [viewMode, setViewMode] = useState('aggregated'); 

  useEffect(() => {
    if (!containerRef.current) return;

    let data = { nodes: [], edges: [] };
    let options = {};

    if (statistics) {
      // --- AGGREGATED VIEW (Professional Process Map) ---
      const { activity_distribution, transition_sequence } = statistics;
      const nodes = [];
      const edges = [];
      const maxCount = Math.max(...Object.values(activity_distribution));

      // Add START node
      nodes.push({
        id: 'START',
        label: 'START',
        shape: 'circle',
        color: { background: '#4CAF50', border: '#388E3C' },
        font: { color: 'white', size: 14, bold: true },
        size: 25,
        shadow: true,
      });

      // Add activity nodes (Unique Applications)
      Object.entries(activity_distribution).forEach(([activity, count]) => {
        const freq = count / maxCount;
        // Color gradient based on frequency
        let color = freq >= 0.7 ? { background: '#1E88E5', border: '#1565C0' } : // Darker Blue
                   freq >= 0.3 ? { background: '#42A5F5', border: '#1E88E5' } : // Medium Blue
                                 { background: '#90CAF9', border: '#42A5F5' }; // Light Blue

        nodes.push({
          id: activity,
          label: `${activity}\n(${count})`,
          shape: 'box',
          color: { ...color, hover: { background: '#FFC107', border: '#FFA000' } },
          font: { color: 'white', size: 14, face: 'arial' },
          margin: 12,
          borderWidth: 2,
          shadow: true,
          title: `Click to view details for ${activity}`,
        });
      });

      // Add END node
      nodes.push({
        id: 'END',
        label: 'END',
        shape: 'circle',
        color: { background: '#F44336', border: '#D32F2F' },
        font: { color: 'white', size: 14, bold: true },
        size: 25,
        shadow: true,
      });

      // Add START edge to first activity
      if (transition_sequence && transition_sequence.length > 0) {
        const firstActivity = transition_sequence[0].from;
        edges.push({
          from: 'START',
          to: firstActivity,
          label: '1',
          arrows: { to: { enabled: true, scaleFactor: 1.0 } },
          color: { color: '#78909C' },
          width: 2,
          dashes: true,
        });
      }

      // Add INDIVIDUAL transitions (Multiple arrows for repeated transitions)
      if (transition_sequence && transition_sequence.length > 0) {
        // Count how many times each transition pair occurs to adjust curve
        const transitionCounts = {};
        const transitionIndices = {};
        
        transition_sequence.forEach((trans) => {
          const key = `${trans.from}->${trans.to}`;
          transitionCounts[key] = (transitionCounts[key] || 0) + 1;
          transitionIndices[key] = transitionIndices[key] || [];
        });

        transition_sequence.forEach((trans, index) => {
          const key = `${trans.from}->${trans.to}`;
          const occurrenceIndex = transitionIndices[key].length;
          transitionIndices[key].push(index);
          
          const totalOccurrences = transitionCounts[key];
          
          // Self-loop handling
          const isSelfLoop = trans.from === trans.to;
          
          // Calculate roundness to spread multiple arrows
          // If there are multiple arrows between same nodes, vary the roundness
          let roundness = 0.2;
          if (totalOccurrences > 1) {
            // Spread arrows: -0.5, -0.3, 0, 0.3, 0.5, etc.
            roundness = (occurrenceIndex - (totalOccurrences - 1) / 2) * 0.3;
          }

          edges.push({
            id: `edge_${index}`, // Unique ID for each arrow
            from: trans.from,
            to: trans.to,
            label: `${trans.sequence}`, // Show sequence number
            arrows: { to: { enabled: true, scaleFactor: 1.0 } },
            color: { color: '#1E88E5', highlight: '#FFC107' },
            width: 2,
            smooth: { 
              enabled: true, 
              type: isSelfLoop ? 'curvedCW' : 'curvedCW', 
              roundness: roundness
            },
            font: { align: 'middle', size: 11, background: 'white', strokeWidth: 0 },
          });
        });
      }

      // Add END edge from last activity
      if (transition_sequence && transition_sequence.length > 0) {
        const lastActivity = transition_sequence[transition_sequence.length - 1].to;
        edges.push({
          from: lastActivity,
          to: 'END',
          label: 'End',
          arrows: { to: { enabled: true, scaleFactor: 1.0 } },
          color: { color: '#78909C' },
          width: 2,
          dashes: true,
        });
      }

      data = { nodes, edges };
      options = {
        // Use hierarchical layout for clearer left-to-right flow
        layout: {
          hierarchical: {
            enabled: true,
            direction: 'LR',
            sortMethod: 'directed',
            levelSeparation: 200,
            nodeSpacing: 150,
          },
        },
        physics: {
          enabled: false, // Disable physics for stable hierarchical layout
        },
        interaction: {
          dragNodes: true,
          dragView: true,
          zoomView: false,
          hover: true,
          navigationButtons: true,
          tooltipDelay: 200,
        },
        edges: {
          smooth: {
            enabled: true,
            type: 'curvedCW',
          },
        },
      };
    }

    if (networkRef.current) {
      networkRef.current.destroy();
    }

    networkRef.current = new Network(containerRef.current, data, options);

    networkRef.current.on('click', async (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        if (nodeId === 'START' || nodeId === 'END') return;
        
        setSelectedNode(nodeId);
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
  }, [statistics, timeline, sessionId, apiUrl, token, onNodeClick, viewMode]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '700px',
        border: '2px solid #e5e7eb',
        borderRadius: '12px',
        background: '#f8f9fa',
        cursor: 'pointer',
      }}
    />
  );
};

export default ProcessFlowDiagram;
