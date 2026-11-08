import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import apiClient from '../api/client';
import { useFilters } from '../context/FilterContext';
import { Network, AlertCircle, X, ShieldAlert, Globe, Users, Info } from 'lucide-react';

const TYPE_COLORS = {
  'Actor': { bg: '#2b1016', border: '#ff3333', text: '#ff6666' },
  'Crime Type': { bg: '#08253a', border: '#00d4ff', text: '#38bdf8' },
  'Region': { bg: '#0d2818', border: '#39ff14', text: '#86efac' },
  'Entity': { bg: '#2d1804', border: '#ff9500', text: '#fde047' }
};

export const NetworkGraph = () => {
  const { filters } = useFilters();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [minConnections, setMinConnections] = useState(2);
  const [loading, setLoading] = useState(true);

  const fetchNetwork = useCallback(async () => {
    try {
      setLoading(true);
      const reg = filters.region && filters.region !== 'All' ? filters.region : '';
      const res = await apiClient.get(
        `/api/network?region=${encodeURIComponent(reg)}&min_connections=${minConnections}`
      );
      if (res.data) {
        const { nodes: rawNodes, edges: rawEdges } = res.data;

        // Position nodes in an organic circular layout
        const total = rawNodes.length;
        const centerX = 380;
        const centerY = 280;
        const radius = total > 25 ? 280 : 190;

        const flowNodes = rawNodes.map((n, i) => {
          const angle = (2 * Math.PI * i) / (total || 1);
          const jitter = (i % 3) * 35;
          const r = radius + jitter;
          const x = centerX + r * Math.cos(angle);
          const y = centerY + r * Math.sin(angle);

          const centrality = n.centrality || 0;
          const nType = n.crime_type || n.node_type || 'Entity';
          const theme = TYPE_COLORS[nType] || TYPE_COLORS['Entity'];

          return {
            id: n.id,
            position: { x, y },
            data: {
              label: n.label,
              centrality: n.centrality,
              degree_centrality: n.degree_centrality,
              node_type: nType
            },
            style: {
              background: theme.bg,
              borderColor: theme.border,
              borderWidth: 2,
              borderRadius: '8px',
              color: theme.text,
              fontFamily: 'Share Tech Mono',
              fontSize: '11px',
              padding: '8px 12px',
              boxShadow: `0 0 14px ${theme.border}40`,
              width: 'auto',
              minWidth: '90px',
              textAlign: 'center',
              cursor: 'pointer'
            }
          };
        });

        const flowEdges = rawEdges.map((e, idx) => {
          const weight = e.weight || 1;
          const strokeWidth = Math.max(1.2, Math.min(5, Math.log10(weight + 1) * 2));
          return {
            id: `e-${e.source}-${e.target}-${idx}`,
            source: e.source,
            target: e.target,
            animated: true,
            style: {
              stroke: 'rgba(0, 212, 255, 0.45)',
              strokeWidth
            },
            data: { weight }
          };
        });

        setNodes(flowNodes);
        setEdges(flowEdges);
      }
    } catch (err) {
      console.error('Failed to fetch network graph:', err);
    } finally {
      setLoading(false);
    }
  }, [filters.region, minConnections, setNodes, setEdges]);

  useEffect(() => {
    fetchNetwork();
  }, [fetchNetwork]);

  const onNodeClick = (_, node) => {
    setSelectedNode(node);

    setEdges(prevEdges =>
      prevEdges.map(edge => {
        const isConnected = edge.source === node.id || edge.target === node.id;
        return {
          ...edge,
          style: {
            stroke: isConnected ? '#39ff14' : 'rgba(0, 212, 255, 0.15)',
            strokeWidth: isConnected ? 3.5 : 1
          }
        };
      })
    );
  };

  const clearSelection = () => {
    setSelectedNode(null);
    setEdges(prevEdges =>
      prevEdges.map(edge => ({
        ...edge,
        style: {
          stroke: 'rgba(0, 212, 255, 0.45)',
          strokeWidth: Math.max(1.2, Math.min(5, Math.log10((edge.data?.weight || 1) + 1) * 2))
        }
      }))
    );
  };

  return (
    <div className="space-y-4">
      {/* Explicit Coverage Limit Documentation Banner */}
      <div className="p-3.5 rounded bg-[#0d1b2a] border border-[#ff9500]/40 text-[#ff9500] text-xs font-share-tech flex items-start space-x-2.5">
        <Info size={16} className="flex-shrink-0 mt-0.5 text-[#ff9500]" />
        <div>
          <span className="font-orbitron font-bold">ACTOR GRAPH COVERAGE LIMITATION:</span>
          <p className="text-[#cbd5e1] mt-0.5 leading-relaxed">
            Actor nodes represent named insurgencies, extremist syndicates, and cartels derived from the Global Terrorism Database (GTD, 1970–2020) and Cartel tracker. ACLED disorder classifications (e.g. "Political violence", "Demonstrations") have been excluded to avoid misidentifying generic incident types as organized actor groups.
          </p>
        </div>
      </div>

      <div className="scifi-panel relative w-full h-[620px] overflow-hidden border border-[#00d4ff]/30">
        {/* Top Floating Controls */}
        <div className="absolute top-4 left-4 z-20 flex flex-wrap items-center gap-3 backdrop-blur-md bg-[#0d1b2a]/90 p-2.5 rounded-lg border border-[#00d4ff]/30 shadow-md">
          <div className="flex items-center space-x-1.5 text-xs font-orbitron text-[#e2e8f0]">
            <Network size={16} className="text-[#00d4ff]" />
            <span>ORGANIZED SYNDICATE CO-OCCURRENCE NETWORK</span>
          </div>

          <div className="flex items-center space-x-2 pl-3 border-l border-[#00d4ff]/20 text-xs font-share-tech">
            <span className="text-[#94a3b8]">MIN CO-OCCURRENCES:</span>
            <input
              type="range"
              min="1"
              max="10"
              value={minConnections}
              onChange={(e) => setMinConnections(parseInt(e.target.value, 10))}
              className="w-20 accent-[#00d4ff] cursor-pointer"
            />
            <span className="text-[#00d4ff] font-bold">≥ {minConnections}</span>
          </div>
        </div>

        {/* Legend */}
        <div className="absolute top-4 right-4 z-20 hidden sm:flex items-center space-x-3 backdrop-blur-md bg-[#0d1b2a]/90 px-3 py-1.5 rounded-lg border border-[#00d4ff]/30 text-xs font-share-tech">
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#ff3333]"></span>
            <span className="text-[#94a3b8]">Named Actor Group (GTD/Cartel)</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#00d4ff]"></span>
            <span className="text-[#94a3b8]">Threat Category</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#39ff14]"></span>
            <span className="text-[#94a3b8]">Region</span>
          </div>
        </div>

        {/* React Flow Canvas */}
        <div className="w-full h-full bg-[#0a0f1e]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#00d4ff" gap={30} size={1} style={{ opacity: 0.08 }} />
            <Controls
              style={{
                background: '#0d1b2a',
                borderColor: 'rgba(0, 212, 255, 0.4)',
                borderRadius: '6px',
                fill: '#00d4ff'
              }}
            />
            <MiniMap
              nodeColor={(n) => {
                const nType = n.data?.node_type;
                if (nType === 'Actor') return '#ff3333';
                if (nType === 'Crime Type') return '#00d4ff';
                if (nType === 'Region') return '#39ff14';
                return '#ff9500';
              }}
              maskColor="rgba(10, 15, 30, 0.85)"
              style={{
                background: '#0d1b2a',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: '6px'
              }}
            />
          </ReactFlow>
        </div>

        {/* Selected Node Detail Sliding Panel */}
        {selectedNode && (
          <div className="absolute bottom-4 right-4 z-30 w-84 bg-[#0d1b2a]/95 backdrop-blur-md border border-[#00d4ff]/40 rounded-lg p-4 shadow-[0_0_20px_rgba(0,212,255,0.25)]">
            <div className="flex items-center justify-between pb-2 border-b border-[#00d4ff]/20 mb-3">
              <span className="text-xs font-orbitron font-semibold text-[#00d4ff]">
                ORGANIZATIONAL METRICS
              </span>
              <button
                onClick={clearSelection}
                className="text-[#94a3b8] hover:text-[#ff3333] transition-all cursor-pointer"
              >
                <X size={15} />
              </button>
            </div>

            <div className="space-y-2 text-xs font-share-tech">
              <div>
                <span className="text-[#94a3b8] block text-[10px] font-orbitron">IDENTIFIED GROUP</span>
                <span className="font-bold text-sm text-[#e2e8f0]">{selectedNode.data.label}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div className="p-2 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                  <span className="text-[10px] text-[#94a3b8] block">TYPE</span>
                  <span className="text-[#00d4ff] font-bold">{selectedNode.data.node_type}</span>
                </div>
                <div className="p-2 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                  <span className="text-[10px] text-[#94a3b8] block">BETWEENNESS</span>
                  <span className="text-[#39ff14] font-bold">
                    {(selectedNode.data.centrality || 0).toFixed(4)}
                  </span>
                </div>
              </div>

              <div className="p-2 rounded bg-[#0a0f1e] border border-[#00d4ff]/20">
                <span className="text-[10px] text-[#94a3b8] block">DEGREE CENTRALITY</span>
                <span className="text-[#ff9500] font-bold">
                  {(selectedNode.data.degree_centrality || 0).toFixed(4)}
                </span>
              </div>

              <p className="text-[10px] text-[#94a3b8] leading-relaxed pt-1">
                High betweenness centrality reflects a key organizational node connecting operations across multiple geographic theaters and tactical domains.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NetworkGraph;
