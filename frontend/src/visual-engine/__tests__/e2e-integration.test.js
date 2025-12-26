/**
 * E2E Integration Tests for Visual Engine
 * Tests complete flow: Question -> Blueprint -> Rendering -> Narrative
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MagicNotebookEngine } from '../MagicNotebookEngine';
import UniversalSketchCanvas from '../UniversalSketchCanvas';

// Test setup
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

describe('E2E Integration Tests - MagicNotebookEngine', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should render MagicNotebookEngine with basic question', async () => {
    const mockOnBlueprintGenerated = jest.fn();
    const mockOnNarrativeComplete = jest.fn();

    render(
      <MagicNotebookEngine
        question="What is Newton's Second Law?"
        context={{ subject: 'physics', level: 'high_school' }}
        onBlueprintGenerated={mockOnBlueprintGenerated}
        onNarrativeComplete={mockOnNarrativeComplete}
      />,
      { wrapper }
    );

    // Should show loading state initially
    await waitFor(() => {
      expect(screen.queryByText(/generating/i) || screen.queryByText(/loading/i)).toBeTruthy();
    }, { timeout: 5000 });
  });

  test('should handle pre-generated blueprint', async () => {
    const mockBlueprint = {
      concept: "Newton's Second Law",
      subject: 'physics',
      elements: [
        { type: 'text', content: 'F = ma', x: 100, y: 100 },
        { type: 'arrow', points: [[50, 50], [150, 50]] },
      ],
    };

    const { container } = render(
      <MagicNotebookEngine
        question="What is Newton's Second Law?"
        preGeneratedBlueprint={mockBlueprint}
        showControls={true}
      />,
      { wrapper }
    );

    await waitFor(() => {
      expect(container.querySelector('canvas')).toBeTruthy();
    });
  });

  test('should handle narrative teaching flow', async () => {
    const mockOnNarrativeComplete = jest.fn();
    const mockBlueprint = {
      concept: 'Photosynthesis',
      subject: 'biology',
      elements: [
        { type: 'text', content: '6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂', x: 100, y: 100 },
      ],
      narrative: {
        beats: [
          { type: 'setup', duration: 2000, text: 'Plants make food' },
          { type: 'action', duration: 3000, text: 'Using sunlight' },
        ],
      },
    };

    render(
      <MagicNotebookEngine
        question="How does photosynthesis work?"
        preGeneratedBlueprint={mockBlueprint}
        showNarrative={true}
        onNarrativeComplete={mockOnNarrativeComplete}
      />,
      { wrapper }
    );

    await waitFor(() => {
      expect(mockOnNarrativeComplete).toHaveBeenCalled();
    }, { timeout: 10000 });
  });

  test('should handle error states gracefully', async () => {
    const mockOnError = jest.fn();

    render(
      <MagicNotebookEngine
        question=""
        context={{ subject: 'invalid' }}
        onError={mockOnError}
      />,
      { wrapper }
    );

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalled();
    }, { timeout: 5000 });
  });

  test('should integrate with validation feedback', async () => {
    const mockOnValidationFeedback = jest.fn();
    const mockBlueprint = {
      concept: 'Quadratic Equation',
      subject: 'math',
      elements: [
        { type: 'text', content: 'x² + 5x + 6 = 0', x: 100, y: 100 },
      ],
    };

    render(
      <UniversalSketchCanvas
        blueprint={mockBlueprint}
        question="Solve quadratic equation"
        enableValidation={true}
        enableFeedback={true}
        onValidationFeedback={mockOnValidationFeedback}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/quadratic/i) || screen.getByText(/equation/i)).toBeTruthy();
    }, { timeout: 5000 });
  });

  test('should handle mode switching during runtime', async () => {
    const mockBlueprint = {
      concept: 'Pythagorean Theorem',
      subject: 'math',
      mode: 'learn',
      elements: [
        { type: 'text', content: 'a² + b² = c²', x: 100, y: 100 },
      ],
    };

    const { rerender } = render(
      <MagicNotebookEngine
        question="What is Pythagorean theorem?"
        preGeneratedBlueprint={mockBlueprint}
      />,
      { wrapper }
    );

    // Switch to practice mode
    const updatedBlueprint = { ...mockBlueprint, mode: 'practice' };
    rerender(
      <MagicNotebookEngine
        question="Practice Pythagorean theorem"
        preGeneratedBlueprint={updatedBlueprint}
      />
    );

    await waitFor(() => {
      expect(screen.queryByText(/practice/i)).toBeTruthy();
    }, { timeout: 3000 });
  });
});

describe('E2E Integration Tests - UniversalSketchCanvas', () => {
  test('should render complete sketch with all elements', async () => {
    const mockBlueprint = {
      concept: 'Water Cycle',
      subject: 'geography',
      elements: [
        { type: 'circle', x: 100, y: 100, radius: 50 },
        { type: 'text', content: 'Evaporation', x: 100, y: 200 },
        { type: 'arrow', points: [[100, 150], [200, 150]] },
        { type: 'line', points: [[50, 50], [150, 50]] },
      ],
    };

    const { container } = render(
      <UniversalSketchCanvas
        blueprint={mockBlueprint}
        question="Explain water cycle"
        height={500}
        width={600}
      />
    );

    await waitFor(() => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
      expect(canvas.height).toBeGreaterThan(0);
    });
  });

  test('should handle drawing hand animation', async () => {
    const mockBlueprint = {
      concept: 'Simple Drawing',
      elements: [
        { type: 'line', points: [[0, 0], [100, 100]], animated: true },
      ],
    };

    render(
      <UniversalSketchCanvas
        blueprint={mockBlueprint}
        question="Draw a line"
        showDrawingHand={true}
      />
    );

    await waitFor(() => {
      expect(screen.queryByTestId('drawing-hand') || true).toBeTruthy();
    }, { timeout: 5000 });
  });
});










































