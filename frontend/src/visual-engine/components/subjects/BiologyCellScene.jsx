/**
 * Biology - Cell Structure Scene
 * Interactive cell with organelles
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Maximize2, ChevronDown, ChevronUp, Info } from 'lucide-react';

const BiologyCellScene = ({ embedded = true }) => {
  const [selectedOrganelle, setSelectedOrganelle] = useState(null);
  const [showControls, setShowControls] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [cellType, setCellType] = useState('animal'); // animal or plant

  const organelles = {
    nucleus: { name: 'Nucleus', color: '#9C27B0', info: 'Contains DNA, controls cell activities' },
    mitochondria: { name: 'Mitochondria', color: '#FF5722', info: 'Powerhouse - produces ATP energy' },
    ribosome: { name: 'Ribosome', color: '#795548', info: 'Protein synthesis' },
    er: { name: 'Endoplasmic Reticulum', color: '#2196F3', info: 'Transport network' },
    golgi: { name: 'Golgi Body', color: '#FFC107', info: 'Packaging & shipping proteins' },
    lysosome: { name: 'Lysosome', color: '#4CAF50', info: 'Digestion & waste removal' },
    vacuole: { name: 'Vacuole', color: '#00BCD4', info: 'Storage (large in plant cells)' },
    chloroplast: { name: 'Chloroplast', color: '#8BC34A', info: 'Photosynthesis (plant only)' },
  };

  return (
    <motion.div
      className={`rounded-xl overflow-hidden shadow-lg border border-gray-200 bg-white ${isExpanded ? 'fixed inset-8 z-50' : ''}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {isExpanded && <div className="fixed inset-0 bg-black/80 -z-10" onClick={() => setIsExpanded(false)} />}

      {/* Scene */}
      <div className="relative bg-gradient-to-br from-green-50 to-teal-100" style={{ height: isExpanded ? '60vh' : '260px' }}>
        <svg viewBox="0 0 400 220" className="w-full h-full">
          <defs>
            <filter id="cellGlow">
              <feGaussianBlur stdDeviation="1.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Cell Wall (plant only) */}
          {cellType === 'plant' && (
            <rect x="30" y="20" width="340" height="180" rx="20" fill="none" stroke="#8BC34A" strokeWidth="8" />
          )}

          {/* Cell Membrane */}
          <ellipse
            cx="200" cy="110"
            rx={cellType === 'plant' ? 155 : 165}
            ry={cellType === 'plant' ? 75 : 85}
            fill="#FFF9C4"
            stroke="#FFE082"
            strokeWidth="4"
          />

          {/* Cytoplasm texture */}
          {[...Array(20)].map((_, i) => (
            <circle
              key={i}
              cx={80 + Math.random() * 240}
              cy={50 + Math.random() * 120}
              r={2 + Math.random() * 3}
              fill="rgba(255, 236, 179, 0.5)"
            />
          ))}

          {/* Nucleus */}
          <g 
            onClick={() => setSelectedOrganelle('nucleus')}
            style={{ cursor: 'pointer' }}
          >
            <ellipse cx="200" cy="110" rx="45" ry="35" fill="#E1BEE7" stroke="#9C27B0" strokeWidth="2" />
            <ellipse cx="200" cy="110" rx="15" ry="12" fill="#9C27B0" opacity="0.7" />
            <text x="200" y="155" textAnchor="middle" fontSize="9" fill="#7B1FA2">Nucleus</text>
            {selectedOrganelle === 'nucleus' && (
              <ellipse cx="200" cy="110" rx="48" ry="38" fill="none" stroke="#9C27B0" strokeWidth="2" strokeDasharray="4">
                <animate attributeName="stroke-dashoffset" from="0" to="16" dur="0.5s" repeatCount="indefinite" />
              </ellipse>
            )}
          </g>

          {/* Mitochondria */}
          {[{ x: 100, y: 80 }, { x: 290, y: 130 }, { x: 130, y: 140 }].map((pos, i) => (
            <g key={i} onClick={() => setSelectedOrganelle('mitochondria')} style={{ cursor: 'pointer' }}>
              <ellipse cx={pos.x} cy={pos.y} rx="22" ry="10" fill="#FFCCBC" stroke="#FF5722" strokeWidth="1.5" transform={`rotate(${30 + i * 40} ${pos.x} ${pos.y})`} />
              <path d={`M ${pos.x - 15} ${pos.y} Q ${pos.x - 8} ${pos.y - 5} ${pos.x} ${pos.y} Q ${pos.x + 8} ${pos.y + 5} ${pos.x + 15} ${pos.y}`} stroke="#FF5722" strokeWidth="1" fill="none" transform={`rotate(${30 + i * 40} ${pos.x} ${pos.y})`} />
            </g>
          ))}
          <text x="100" y="100" textAnchor="middle" fontSize="8" fill="#E64A19">Mitochondria</text>

          {/* Endoplasmic Reticulum */}
          <g onClick={() => setSelectedOrganelle('er')} style={{ cursor: 'pointer' }}>
            <path d="M 250 70 Q 270 75 265 90 Q 260 105 280 100 Q 300 95 295 110 Q 290 125 310 120" fill="none" stroke="#2196F3" strokeWidth="6" opacity="0.6" />
            <path d="M 250 70 Q 270 75 265 90 Q 260 105 280 100 Q 300 95 295 110 Q 290 125 310 120" fill="none" stroke="#1565C0" strokeWidth="2" strokeDasharray="3 2" />
            <text x="280" y="65" fontSize="8" fill="#1565C0">ER</text>
          </g>

          {/* Golgi Body */}
          <g onClick={() => setSelectedOrganelle('golgi')} style={{ cursor: 'pointer' }} transform="translate(70, 100)">
            {[0, 8, 16, 24].map((y, i) => (
              <ellipse key={i} cx="0" cy={y} rx={20 - i * 2} ry="4" fill="#FFF59D" stroke="#FFC107" strokeWidth="1" />
            ))}
            <text x="0" y="38" textAnchor="middle" fontSize="8" fill="#F57F17">Golgi</text>
          </g>

          {/* Ribosomes */}
          {[...Array(15)].map((_, i) => (
            <circle key={i} cx={120 + (i % 5) * 40 + Math.random() * 20} cy={60 + Math.floor(i / 5) * 50 + Math.random() * 20} r="3" fill="#795548" onClick={() => setSelectedOrganelle('ribosome')} style={{ cursor: 'pointer' }} />
          ))}

          {/* Vacuole (larger for plant) */}
          <ellipse
            cx={cellType === 'plant' ? 200 : 320}
            cy={cellType === 'plant' ? 110 : 80}
            rx={cellType === 'plant' ? 80 : 20}
            ry={cellType === 'plant' ? 50 : 15}
            fill="rgba(0, 188, 212, 0.3)"
            stroke="#00BCD4"
            strokeWidth="1.5"
            onClick={() => setSelectedOrganelle('vacuole')}
            style={{ cursor: 'pointer' }}
          />
          <text x={cellType === 'plant' ? 200 : 320} y={cellType === 'plant' ? 110 : 80} textAnchor="middle" fontSize="9" fill="#00838F">Vacuole</text>

          {/* Chloroplast (plant only) */}
          {cellType === 'plant' && [{ x: 320, y: 70 }, { x: 80, y: 60 }, { x: 310, y: 150 }].map((pos, i) => (
            <g key={i} onClick={() => setSelectedOrganelle('chloroplast')} style={{ cursor: 'pointer' }}>
              <ellipse cx={pos.x} cy={pos.y} rx="18" ry="10" fill="#C5E1A5" stroke="#8BC34A" strokeWidth="1.5" />
              <line x1={pos.x - 12} y1={pos.y} x2={pos.x + 12} y2={pos.y} stroke="#689F38" strokeWidth="1" />
              <line x1={pos.x - 10} y1={pos.y - 4} x2={pos.x + 10} y2={pos.y - 4} stroke="#689F38" strokeWidth="0.5" />
              <line x1={pos.x - 10} y1={pos.y + 4} x2={pos.x + 10} y2={pos.y + 4} stroke="#689F38" strokeWidth="0.5" />
            </g>
          ))}
          {cellType === 'plant' && <text x="320" y="90" fontSize="8" fill="#558B2F">Chloroplast</text>}

        </svg>

        {/* Top UI */}
        <div className="absolute top-2 left-2 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-1.5">
          <div className="text-lg font-bold text-gray-800">{cellType === 'plant' ? 'Plant' : 'Animal'} Cell</div>
        </div>

        <div className="absolute top-2 right-2">
          <button onClick={() => setIsExpanded(!isExpanded)} className="p-1.5 bg-white/90 rounded-lg hover:bg-white">
            <Maximize2 className="w-4 h-4 text-gray-600" />
          </button>
        </div>

        {/* Info popup */}
        <AnimatePresence>
          {selectedOrganelle && (
            <motion.div
              className="absolute bottom-2 left-2 right-2 bg-white rounded-lg p-3 shadow-lg border"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-gray-800">{organelles[selectedOrganelle]?.name}</h4>
                  <p className="text-sm text-gray-600">{organelles[selectedOrganelle]?.info}</p>
                </div>
                <button onClick={() => setSelectedOrganelle(null)} className="text-gray-400 hover:text-gray-600">✕</button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Controls */}
      <div className="bg-gray-50 border-t border-gray-100">
        <button 
          onClick={() => setShowControls(!showControls)}
          className="w-full py-1.5 flex items-center justify-center text-gray-500 hover:bg-gray-100 text-sm"
        >
          {showControls ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          <span className="ml-1">{showControls ? 'Hide' : 'Show'} Controls</span>
        </button>

        {showControls && (
          <div className="px-4 pb-3">
            <div className="flex justify-center space-x-2">
              <button
                onClick={() => setCellType('animal')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${cellType === 'animal' ? 'bg-orange-500 text-white' : 'bg-gray-200 text-gray-700'}`}
              >
                🐾 Animal Cell
              </button>
              <button
                onClick={() => setCellType('plant')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${cellType === 'plant' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'}`}
              >
                🌱 Plant Cell
              </button>
            </div>
            <p className="text-center text-xs text-gray-500 mt-2">Tap organelles to learn more!</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default BiologyCellScene;









