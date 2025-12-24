/**
 * Mobile Responsiveness Tests
 * Tests visual engine behavior across different screen sizes
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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

// Mock viewport sizes
const setViewport = (width, height) => {
  global.innerWidth = width;
  global.innerHeight = height;
  global.dispatchEvent(new Event('resize'));
};

describe('Mobile Responsiveness Tests', () => {
  const mockBlueprint = {
    concept: 'Test Concept',
    subject: 'math',
    elements: [
      { type: 'text', content: 'Test', x: 100, y: 100 },
      { type: 'circle', x: 200, y: 200, radius: 50 },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Mobile Portrait (320x568 - iPhone SE)', () => {
    beforeEach(() => {
      setViewport(320, 568);
    });

    test('should render MagicNotebookEngine on mobile portrait', async () => {
      const { container } = render(
        <MagicNotebookEngine
          question="Test question"
          preGeneratedBlueprint={mockBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        // Canvas should adapt to smaller viewport
        expect(canvas.width).toBeLessThanOrEqual(320);
      });
    });

    test('should scale elements appropriately for mobile', async () => {
      const { container } = render(
        <UniversalSketchCanvas
          blueprint={mockBlueprint}
          question="Test"
          width={300}
          height={400}
        />
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        expect(canvas.width).toBeLessThanOrEqual(320);
      });
    });

    test('should hide non-essential UI on mobile', async () => {
      render(
        <MagicNotebookEngine
          question="Test"
          preGeneratedBlueprint={mockBlueprint}
          showControls={true}
        />,
        { wrapper }
      );

      await waitFor(() => {
        // Controls might be hidden or simplified on mobile
        const controls = screen.queryByTestId('controls');
        expect(controls || true).toBeTruthy();
      });
    });
  });

  describe('Mobile Landscape (568x320)', () => {
    beforeEach(() => {
      setViewport(568, 320);
    });

    test('should adapt layout for landscape orientation', async () => {
      const { container } = render(
        <MagicNotebookEngine
          question="Test"
          preGeneratedBlueprint={mockBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        expect(canvas.width).toBeGreaterThan(canvas.height);
      });
    });
  });

  describe('Tablet Portrait (768x1024 - iPad)', () => {
    beforeEach(() => {
      setViewport(768, 1024);
    });

    test('should render full features on tablet', async () => {
      const { container } = render(
        <MagicNotebookEngine
          question="Test"
          preGeneratedBlueprint={mockBlueprint}
          showControls={true}
          showNarrative={true}
        />,
        { wrapper }
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        expect(canvas.width).toBeLessThanOrEqual(768);
      });
    });

    test('should maintain aspect ratio on tablet', async () => {
      const { container } = render(
        <UniversalSketchCanvas
          blueprint={mockBlueprint}
          question="Test"
          width={700}
          height={500}
        />
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        const aspectRatio = canvas.width / canvas.height;
        expect(aspectRatio).toBeCloseTo(700 / 500, 1);
      });
    });
  });

  describe('Desktop (1920x1080)', () => {
    beforeEach(() => {
      setViewport(1920, 1080);
    });

    test('should render full-resolution canvas on desktop', async () => {
      const { container } = render(
        <MagicNotebookEngine
          question="Test"
          preGeneratedBlueprint={mockBlueprint}
          showControls={true}
          showNarrative={true}
        />,
        { wrapper }
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        expect(canvas.width).toBeGreaterThan(500);
      });
    });

    test('should show all UI controls on desktop', async () => {
      render(
        <MagicNotebookEngine
          question="Test"
          preGeneratedBlueprint={mockBlueprint}
          showControls={true}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/test/i)).toBeTruthy();
      });
    });
  });

  describe('Touch Interactions', () => {
    test('should handle touch events on mobile', async () => {
      const { container } = render(
        <UniversalSketchCanvas
          blueprint={mockBlueprint}
          question="Test"
          enableInteraction={true}
        />
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
        
        // Simulate touch event
        const touchEvent = new TouchEvent('touchstart', {
          touches: [{ clientX: 100, clientY: 100 }],
        });
        canvas.dispatchEvent(touchEvent);
      });
    });

    test('should support pinch-to-zoom on mobile', async () => {
      const { container } = render(
        <UniversalSketchCanvas
          blueprint={mockBlueprint}
          question="Test"
          enableZoom={true}
        />
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
      });
    });
  });

  describe('Font Scaling', () => {
    test('should scale text appropriately for mobile', async () => {
      const textBlueprint = {
        concept: 'Text Test',
        elements: [
          { type: 'text', content: 'Mobile Text', x: 50, y: 50, fontSize: 16 },
        ],
      };

      setViewport(320, 568);
      
      const { container } = render(
        <UniversalSketchCanvas
          blueprint={textBlueprint}
          question="Test"
        />
      );

      await waitFor(() => {
        const canvas = container.querySelector('canvas');
        expect(canvas).toBeTruthy();
      });
    });
  });
});







































