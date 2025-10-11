"""
SVG concept visualization generator for AI Tutor 2.0
Generates simple, educational SVG illustrations for mathematical and scientific concepts
"""
import re
from typing import Dict, Any, Optional


class SVGGenerator:
    """Generate educational SVG visualizations"""
    
    def generate_concept_visual(self, concept: str, subject: str, topic: str = "") -> Optional[str]:
        """Generate SVG based on detected concept"""
        concept_lower = concept.lower()
        subject_lower = subject.lower()
        
        # Mathematics concepts
        if 'quadratic' in concept_lower or 'parabola' in concept_lower:
            return self._generate_parabola()
        elif 'circle' in concept_lower or 'circular' in concept_lower:
            return self._generate_circle()
        elif 'triangle' in concept_lower:
            return self._generate_triangle()
        elif 'function' in concept_lower or 'graph' in concept_lower:
            return self._generate_function_graph()
        
        # Physics concepts
        elif 'force' in concept_lower or 'vector' in concept_lower:
            return self._generate_force_vector()
        elif 'wave' in concept_lower or 'oscillation' in concept_lower:
            return self._generate_wave()
        elif 'circuit' in concept_lower or 'electric' in concept_lower:
            return self._generate_circuit()
        
        # Chemistry concepts
        elif 'molecule' in concept_lower or 'bond' in concept_lower:
            return self._generate_molecule()
        elif 'atom' in concept_lower:
            return self._generate_atom()
        
        # Default: Generic concept illustration
        return self._generate_generic_concept()
    
    def _generate_parabola(self) -> str:
        """Generate a parabola SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="parabolaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#8B5CF6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3B82F6;stop-opacity:1" />
    </linearGradient>
  </defs>
  <g transform="translate(100,180)">
    <line x1="-90" y1="0" x2="90" y2="0" stroke="#E5E7EB" stroke-width="2"/>
    <line x1="0" y1="10" x2="0" y2="-170" stroke="#E5E7EB" stroke-width="2"/>
    <path d="M -80,160 Q 0,-100 80,160" fill="none" stroke="url(#parabolaGrad)" stroke-width="3"/>
    <circle cx="0" cy="-100" r="4" fill="#8B5CF6"/>
    <text x="85" y="15" font-size="12" fill="#6B7280">x</text>
    <text x="-10" y="-165" font-size="12" fill="#6B7280">y</text>
  </g>
</svg>'''
    
    def _generate_circle(self) -> str:
        """Generate a circle SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="circleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#22C55E;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#10B981;stop-opacity:0.3" />
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="70" fill="url(#circleGrad)" stroke="#22C55E" stroke-width="3"/>
  <circle cx="100" cy="100" r="3" fill="#22C55E"/>
  <line x1="100" y1="100" x2="170" y2="100" stroke="#6B7280" stroke-width="2" stroke-dasharray="4"/>
  <text x="128" y="105" font-size="14" fill="#22C55E" font-weight="bold">r</text>
</svg>'''
    
    def _generate_triangle(self) -> str:
        """Generate a triangle SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="triGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#F59E0B;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#EF4444;stop-opacity:0.3" />
    </linearGradient>
  </defs>
  <polygon points="100,40 40,160 160,160" fill="url(#triGrad)" stroke="#F59E0B" stroke-width="3"/>
  <circle cx="100" cy="40" r="4" fill="#F59E0B"/>
  <circle cx="40" cy="160" r="4" fill="#F59E0B"/>
  <circle cx="160" cy="160" r="4" fill="#F59E0B"/>
  <text x="90" y="25" font-size="14" fill="#F59E0B" font-weight="bold">A</text>
  <text x="25" y="170" font-size="14" fill="#F59E0B" font-weight="bold">B</text>
  <text x="170" y="170" font-size="14" fill="#F59E0B" font-weight="bold">C</text>
</svg>'''
    
    def _generate_function_graph(self) -> str:
        """Generate a function graph SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="funcGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:1" />
    </linearGradient>
  </defs>
  <g transform="translate(20,20)">
    <line x1="0" y1="140" x2="160" y2="140" stroke="#E5E7EB" stroke-width="2"/>
    <line x1="20" y1="0" x2="20" y2="160" stroke="#E5E7EB" stroke-width="2"/>
    <path d="M 0,140 Q 40,60 80,80 T 160,40" fill="none" stroke="url(#funcGrad)" stroke-width="3"/>
    <text x="155" y="155" font-size="12" fill="#6B7280">x</text>
    <text x="5" y="10" font-size="12" fill="#6B7280">f(x)</text>
  </g>
</svg>'''
    
    def _generate_force_vector(self) -> str:
        """Generate a force vector SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#EF4444" />
    </marker>
  </defs>
  <circle cx="50" cy="100" r="20" fill="#F3F4F6" stroke="#6B7280" stroke-width="2"/>
  <line x1="70" y1="100" x2="150" y2="100" stroke="#EF4444" stroke-width="3" marker-end="url(#arrowhead)"/>
  <text x="95" y="85" font-size="14" fill="#EF4444" font-weight="bold">F</text>
</svg>'''
    
    def _generate_wave(self) -> str:
        """Generate a wave SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="waveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#06B6D4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3B82F6;stop-opacity:1" />
    </linearGradient>
  </defs>
  <line x1="20" y1="100" x2="180" y2="100" stroke="#E5E7EB" stroke-width="1" stroke-dasharray="4"/>
  <path d="M 20,100 Q 40,60 60,100 T 100,100 T 140,100 T 180,100" 
        fill="none" stroke="url(#waveGrad)" stroke-width="3"/>
  <line x1="60" y1="60" x2="60" y2="140" stroke="#F59E0B" stroke-width="1" stroke-dasharray="2"/>
  <text x="45" y="50" font-size="12" fill="#F59E0B">λ</text>
</svg>'''
    
    def _generate_circuit(self) -> str:
        """Generate a simple circuit SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <line x1="50" y1="100" x2="150" y2="100" stroke="#3B82F6" stroke-width="3"/>
  <circle cx="100" cy="100" r="15" fill="none" stroke="#3B82F6" stroke-width="3"/>
  <line x1="95" y1="100" x2="105" y2="100" stroke="#3B82F6" stroke-width="2"/>
  <rect x="130" y="90" width="5" height="20" fill="#EF4444"/>
  <rect x="135" y="95" width="5" height="10" fill="#EF4444"/>
  <text x="140" y="105" font-size="12" fill="#6B7280">+</text>
</svg>'''
    
    def _generate_molecule(self) -> str:
        """Generate a molecule SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <line x1="70" y1="100" x2="130" y2="100" stroke="#6B7280" stroke-width="2"/>
  <line x1="100" y1="70" x2="100" y2="130" stroke="#6B7280" stroke-width="2"/>
  <circle cx="100" cy="100" r="20" fill="#3B82F6" stroke="#1E40AF" stroke-width="2"/>
  <circle cx="70" cy="100" r="15" fill="#EF4444" stroke="#B91C1C" stroke-width="2"/>
  <circle cx="130" cy="100" r="15" fill="#EF4444" stroke="#B91C1C" stroke-width="2"/>
  <circle cx="100" cy="70" r="12" fill="#10B981" stroke="#059669" stroke-width="2"/>
  <circle cx="100" cy="130" r="12" fill="#10B981" stroke="#059669" stroke-width="2"/>
</svg>'''
    
    def _generate_atom(self) -> str:
        """Generate an atom SVG"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="8" fill="#EF4444"/>
  <ellipse cx="100" cy="100" rx="70" ry="30" fill="none" stroke="#3B82F6" stroke-width="2"/>
  <ellipse cx="100" cy="100" rx="30" ry="70" fill="none" stroke="#22C55E" stroke-width="2"/>
  <ellipse cx="100" cy="100" rx="70" ry="70" fill="none" stroke="#F59E0B" stroke-width="2" transform="rotate(45 100 100)"/>
  <circle cx="170" cy="100" r="6" fill="#3B82F6"/>
  <circle cx="100" cy="170" r="6" fill="#22C55E"/>
  <circle cx="149" cy="149" r="6" fill="#F59E0B"/>
</svg>'''
    
    def _generate_generic_concept(self) -> str:
        """Generate a generic concept illustration"""
        return '''<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="genGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#8B5CF6;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#3B82F6;stop-opacity:0.3" />
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="60" fill="url(#genGrad)" stroke="#8B5CF6" stroke-width="3"/>
  <path d="M 100,60 L 120,80 L 100,100 L 80,80 Z" fill="#8B5CF6"/>
  <circle cx="100" cy="140" r="8" fill="#3B82F6"/>
  <circle cx="60" cy="100" r="8" fill="#3B82F6"/>
  <circle cx="140" cy="100" r="8" fill="#3B82F6"/>
</svg>'''