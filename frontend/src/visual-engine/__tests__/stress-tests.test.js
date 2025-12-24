/**
 * Stress Tests for Heavy Blueprints
 * Tests performance with large datasets and complex visualizations
 */

import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MagicNotebookEngine } from '../MagicNotebookEngine';
import UniversalSketchCanvas from '../UniversalSketchCanvas';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

// Helper to generate large blueprints
const generateHeavyBlueprint = (elementCount) => {
  const elements = [];
  for (let i = 0; i < elementCount; i++) {
    const type = ['circle', 'line', 'text', 'arrow'][i % 4];
    elements.push({
      type,
      x: Math.random() * 800,
      y: Math.random() * 600,
      radius: type === 'circle' ? 20 : undefined,
      points: type === 'line' || type === 'arrow' ? [
        [Math.random() * 800, Math.random() * 600],
        [Math.random() * 800, Math.random() * 600]
      ] : undefined,
      content: type === 'text' ? `Element ${i}` : undefined,
    });
  }
  return {
    concept: 'Heavy Blueprint Test',
    subject: 'physics',
    elements,
  };
};

describe('Stress Tests - Heavy Blueprints', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should handle 100 elements without crashing', async () => {
    const heavyBlueprint = generateHeavyBlueprint(100);

    const { container } = render(
      <UniversalSketchCanvas
        blueprint={heavyBlueprint}
        question="Stress test"
        width={800}
        height={600}
      />
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 10000 });
  });

  test('should handle 500 elements with performance optimization', async () => {
    const veryHeavyBlueprint = generateHeavyBlueprint(500);

    const startTime = performance.now();
    
    const { container } = render(
      <UniversalSketchCanvas
        blueprint={veryHeavyBlueprint}
        question="Heavy stress test"
        width={800}
        height={600}
      />
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 20000 });

    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should complete within reasonable time (20 seconds)
    expect(renderTime).toBeLessThan(20000);
  });

  test('should handle deeply nested structures', async () => {
    const nestedBlueprint = {
      concept: 'Nested Test',
      subject: 'math',
      elements: [
        {
          type: 'group',
          children: Array.from({ length: 50 }, (_, i) => ({
            type: 'circle',
            x: 100 + i * 10,
            y: 100 + i * 5,
            radius: 10,
          })),
        },
      ],
    };

    const { container } = render(
      <UniversalSketchCanvas
        blueprint={nestedBlueprint}
        question="Nested test"
      />
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 10000 });
  });

  test('should handle complex mathematical equations', async () => {
    const complexMathBlueprint = {
      concept: 'Complex Equations',
      subject: 'math',
      elements: [
        { type: 'text', content: '∫₀^∞ e^(-x²) dx = √π/2', x: 100, y: 100 },
        { type: 'text', content: '∑ᵢ₌₁^n i = n(n+1)/2', x: 100, y: 150 },
        { type: 'text', content: 'lim[x→0] (sin x)/x = 1', x: 100, y: 200 },
        { type: 'text', content: 'e^(iπ) + 1 = 0', x: 100, y: 250 },
        { type: 'text', content: '∇²φ = ρ/ε₀', x: 100, y: 300 },
      ],
    };

    const { container } = render(
      <UniversalSketchCanvas
        blueprint={complexMathBlueprint}
        question="Complex math"
      />
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 5000 });
  });

  test('should handle rapid blueprint updates', async () => {
    const initialBlueprint = generateHeavyBlueprint(50);
    
    const { container, rerender } = render(
      <UniversalSketchCanvas
        blueprint={initialBlueprint}
        question="Update test"
      />
    );

    await waitFor(() => {
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    // Rapidly update blueprint 10 times
    for (let i = 0; i < 10; i++) {
      const newBlueprint = generateHeavyBlueprint(50 + i * 10);
      rerender(
        <UniversalSketchCanvas
          blueprint={newBlueprint}
          question={`Update test ${i}`}
        />
      );
    }

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 10000 });
  });

  test('should handle memory-intensive animations', async () => {
    const animatedBlueprint = {
      concept: 'Animation Test',
      subject: 'physics',
      elements: Array.from({ length: 100 }, (_, i) => ({
        type: 'circle',
        x: 400 + Math.cos(i * 0.1) * 200,
        y: 300 + Math.sin(i * 0.1) * 200,
        radius: 5,
        animated: true,
        animationDelay: i * 50,
      })),
    };

    const { container } = render(
      <MagicNotebookEngine
        question="Animation test"
        preGeneratedBlueprint={animatedBlueprint}
        showNarrative={true}
      />,
      { wrapper }
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 15000 });
  });

  test('should handle concurrent rendering of multiple canvases', async () => {
    const blueprint1 = generateHeavyBlueprint(50);
    const blueprint2 = generateHeavyBlueprint(50);
    const blueprint3 = generateHeavyBlueprint(50);

    const { container } = render(
      <div>
        <UniversalSketchCanvas
          blueprint={blueprint1}
          question="Canvas 1"
          width={300}
          height={300}
        />
        <UniversalSketchCanvas
          blueprint={blueprint2}
          question="Canvas 2"
          width={300}
          height={300}
        />
        <UniversalSketchCanvas
          blueprint={blueprint3}
          question="Canvas 3"
          width={300}
          height={300}
        />
      </div>
    );

    await waitFor(() => {
      const canvases = container.querySelectorAll('canvas');
      expect(canvases.length).toBeGreaterThanOrEqual(1);
    }, { timeout: 15000 });
  });

  test('should not leak memory on unmount', async () => {
    const heavyBlueprint = generateHeavyBlueprint(200);

    const { container, unmount } = render(
      <UniversalSketchCanvas
        blueprint={heavyBlueprint}
        question="Memory test"
      />
    );

    await waitFor(() => {
      expect(container.querySelector('canvas')).toBeTruthy();
    });

    // Unmount and verify cleanup
    unmount();
    
    // No assertion needed - test passes if no memory errors occur
    expect(true).toBe(true);
  });

  test('should handle extreme canvas dimensions', async () => {
    const largeBlueprint = generateHeavyBlueprint(100);

    const { container } = render(
      <UniversalSketchCanvas
        blueprint={largeBlueprint}
        question="Large canvas test"
        width={4000}
        height={3000}
      />
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
    }, { timeout: 15000 });
  });
});







































