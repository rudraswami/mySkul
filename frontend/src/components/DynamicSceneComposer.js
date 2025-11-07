import React from 'react';
import VoiceOverlay from './VoiceOverlay'; // Importing the VoiceOverlay component

/**
 * DynamicSceneComposer - Composes a dynamic scene with elements, arrows, motion lines, and symbolic tags
 */
const DynamicSceneComposer = ({ visualData }) => {
  // Example of how to dynamically create elements based on visualData
  const renderElements = () => {
    return visualData.elements.map((element, index) => (
      <div key={index} className="absolute" style={{ left: element.x, top: element.y }}>
        <img src={element.image} alt={element.label} className="w-16 h-16" />
        <span className="text-xs">{element.label}</span>
      </div>
    ));
  };

  const renderArrows = () => {
    return visualData.arrows.map((arrow, index) => (
      <svg key={index} className="absolute" style={{ left: arrow.startX, top: arrow.startY }}>
        <line x1={0} y1={0} x2={arrow.endX} y2={arrow.endY} stroke="red" strokeWidth="2" />
        <text x={arrow.endX / 2} y={arrow.endY / 2} fill="black" fontSize="10">
          Force
        </text>
      </svg>
    ));
  };

  const renderMotionLines = () => {
    return visualData.motionLines.map((line, index) => (
      <svg key={index} className="absolute" style={{ left: line.startX, top: line.startY }}>
        <line x1={0} y1={0} x2={line.endX} y2={line.endY} stroke="blue" strokeWidth="1" strokeDasharray="5,5" />
        <text x={line.endX / 2} y={line.endY / 2} fill="black" fontSize="10">
          Inertia
        </text>
      </svg>
    ));
  };

  return (
    <div className="relative w-full h-64">
      {renderElements()}
      {renderArrows()}
      {renderMotionLines()}
      {/* Add symbolic tags as needed */}
      {visualData.symbolicTags.map((law, index) => (
        <VoiceOverlay key={index} law={law} /> // Adding VoiceOverlay for each law
      ))}
    </div>
  );
};

export default DynamicSceneComposer;
