/**
 * Visual Schema Renderer
 * Renders JSON diagram structure as simple SVG
 */
import React from 'react';
import { Maximize2 } from 'lucide-react';

export default function VisualSchema({ schema, onExpand }) {
  if (!schema || !schema.nodes || schema.nodes.length === 0) {
    return null;
  }

  const { diagram_type, title, nodes, edges, caption } = schema;

  // Simple SVG layout based on diagram type
  const renderDiagram = () => {
    const width = 600;
    const height = 400;
    const nodeWidth = 120;
    const nodeHeight = 60;
    const nodeSpacing = 180;

    // Calculate node positions based on diagram type
    const getNodePosition = (index, total) => {
      switch (diagram_type) {
        case 'flow':
        case 'timeline':
          // Horizontal flow
          return {
            x: 50 + (index * nodeSpacing),
            y: height / 2
          };
        
        case 'hierarchy':
          // Tree structure
          const level = Math.floor(index / 2);
          const posInLevel = index % 2;
          return {
            x: 150 + (posInLevel * 250),
            y: 80 + (level * 120)
          };
        
        case 'cycle':
          // Circular arrangement
          const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
          const radius = 150;
          return {
            x: width / 2 + radius * Math.cos(angle),
            y: height / 2 + radius * Math.sin(angle)
          };
        
        case 'comparison':
          // Two columns
          const column = index % 2;
          const row = Math.floor(index / 2);
          return {
            x: 100 + (column * 300),
            y: 80 + (row * 120)
          };
        
        default:
          // Grid layout
          const cols = Math.ceil(Math.sqrt(total));
          const row_default = Math.floor(index / cols);
          const col_default = index % cols;
          return {
            x: 80 + (col_default * 180),
            y: 80 + (row_default * 120)
          };
      }
    };

    const nodePositions = nodes.map((node, i) => ({
      ...node,
      ...getNodePosition(i, nodes.length)
    }));

    return (
      <svg
        width="100%"
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg"
      >
        {/* Draw edges first */}
        {edges.map((edge, i) => {
          const fromNode = nodePositions.find(n => n.id === edge.from);
          const toNode = nodePositions.find(n => n.id === edge.to);
          
          if (!fromNode || !toNode) return null;
          
          return (
            <g key={i}>
              <line
                x1={fromNode.x + nodeWidth / 2}
                y1={fromNode.y + nodeHeight / 2}
                x2={toNode.x + nodeWidth / 2}
                y2={toNode.y + nodeHeight / 2}
                stroke="#6366f1"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
              />
              {edge.label && (
                <text
                  x={(fromNode.x + toNode.x) / 2 + nodeWidth / 2}
                  y={(fromNode.y + toNode.y) / 2 + nodeHeight / 2 - 10}
                  fill="#4f46e5"
                  fontSize="12"
                  textAnchor="middle"
                  className="font-medium"
                >
                  {edge.label}
                </text>
              )}
            </g>
          );
        })}
        
        {/* Arrow marker definition */}
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#6366f1" />
          </marker>
        </defs>
        
        {/* Draw nodes */}
        {nodePositions.map((node) => {
          const bgColor = node.type === 'main' ? '#6366f1' : 
                          node.type === 'result' ? '#10b981' : '#94a3b8';
          const textColor = '#ffffff';
          
          return (
            <g key={node.id}>
              <rect
                x={node.x}
                y={node.y}
                width={nodeWidth}
                height={nodeHeight}
                rx="8"
                fill={bgColor}
                stroke="#ffffff"
                strokeWidth="2"
              />
              <text
                x={node.x + nodeWidth / 2}
                y={node.y + nodeHeight / 2 + 5}
                fill={textColor}
                fontSize="14"
                textAnchor="middle"
                className="font-medium"
              >
                {node.label.length > 15 ? node.label.substring(0, 15) + '...' : node.label}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="bg-white rounded-xl border border-purple-200 p-6 my-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">🧠</span>
          <h3 className="font-semibold text-gray-900">{title || 'Visual Schema'}</h3>
        </div>
        {onExpand && (
          <button
            onClick={onExpand}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Expand diagram"
          >
            <Maximize2 className="h-4 w-4 text-gray-600" />
          </button>
        )}
      </div>
      
      <div className="mb-4">
        {renderDiagram()}
      </div>
      
      {caption && (
        <p className="text-sm text-gray-600 italic text-center">
          {caption}
        </p>
      )}
      
      <div className="mt-2 text-xs text-gray-500 text-center">
        Diagram type: {diagram_type}
      </div>
    </div>
  );
}
