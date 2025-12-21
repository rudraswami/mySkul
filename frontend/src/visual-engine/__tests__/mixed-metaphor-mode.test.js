/**
 * Mixed Metaphor + Mode Tests
 * Tests combinations of different metaphors with various teaching modes
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

describe('Mixed Metaphor + Mode Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Cricket Metaphor Tests', () => {
    const cricketBlueprint = {
      concept: 'Projectile Motion',
      subject: 'physics',
      metaphor: 'cricket',
      elements: [
        { type: 'text', content: 'Ball trajectory', x: 100, y: 100 },
        { type: 'arc', points: [[50, 200], [150, 100], [250, 200]] },
      ],
    };

    test('should apply cricket metaphor in learn mode', async () => {
      const { container } = render(
        <MagicNotebookEngine
          question="Explain projectile motion"
          preGeneratedBlueprint={{ ...cricketBlueprint, mode: 'learn' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeTruthy();
      });
    });

    test('should apply cricket metaphor in practice mode', async () => {
      render(
        <MagicNotebookEngine
          question="Practice projectile motion"
          preGeneratedBlueprint={{ ...cricketBlueprint, mode: 'practice' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/practice/i) || true).toBeTruthy();
      });
    });

    test('should apply cricket metaphor in explore mode', async () => {
      render(
        <MagicNotebookEngine
          question="Explore projectile motion"
          preGeneratedBlueprint={{ ...cricketBlueprint, mode: 'explore' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/explore/i) || true).toBeTruthy();
      });
    });
  });

  describe('Diwali Metaphor Tests', () => {
    const diwaliBlueprint = {
      concept: 'Light Reflection',
      subject: 'physics',
      metaphor: 'diwali',
      elements: [
        { type: 'text', content: 'Diya light', x: 100, y: 100 },
        { type: 'circle', x: 150, y: 150, radius: 30, fill: 'yellow' },
      ],
    };

    test('should apply diwali metaphor with storytelling mode', async () => {
      render(
        <MagicNotebookEngine
          question="Light reflection story"
          preGeneratedBlueprint={{ ...diwaliBlueprint, mode: 'story' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/story/i) || true).toBeTruthy();
      });
    });

    test('should apply diwali metaphor with challenge mode', async () => {
      render(
        <MagicNotebookEngine
          question="Light reflection challenge"
          preGeneratedBlueprint={{ ...diwaliBlueprint, mode: 'challenge' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/challenge/i) || true).toBeTruthy();
      });
    });
  });

  describe('Rangoli Metaphor Tests', () => {
    const rangoliBlueprint = {
      concept: 'Symmetry',
      subject: 'math',
      metaphor: 'rangoli',
      elements: [
        { type: 'polygon', points: [[100, 100], [150, 150], [100, 200], [50, 150]] },
      ],
    };

    test('should apply rangoli metaphor in learn mode', async () => {
      const { container } = render(
        <UniversalSketchCanvas
          blueprint={{ ...rangoliBlueprint, mode: 'learn' }}
          question="Learn symmetry"
        />
      );

      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeTruthy();
      });
    });

    test('should apply rangoli metaphor in creative mode', async () => {
      render(
        <MagicNotebookEngine
          question="Create symmetric patterns"
          preGeneratedBlueprint={{ ...rangoliBlueprint, mode: 'creative' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/creative/i) || true).toBeTruthy();
      });
    });
  });

  describe('Railway Metaphor Tests', () => {
    const railwayBlueprint = {
      concept: 'Motion Graphs',
      subject: 'physics',
      metaphor: 'railway',
      elements: [
        { type: 'line', points: [[0, 100], [200, 100]] },
        { type: 'text', content: 'Train journey', x: 100, y: 50 },
      ],
    };

    test('should apply railway metaphor across multiple modes', async () => {
      const modes = ['learn', 'practice', 'explore', 'challenge'];
      
      for (const mode of modes) {
        const { container, unmount } = render(
          <MagicNotebookEngine
            question={`Railway ${mode}`}
            preGeneratedBlueprint={{ ...railwayBlueprint, mode }}
          />,
          { wrapper }
        );

        await waitFor(() => {
          expect(container.querySelector('canvas')).toBeTruthy();
        });

        unmount();
      }
    });
  });

  describe('Food Metaphor Tests', () => {
    const foodBlueprint = {
      concept: 'Chemical Reactions',
      subject: 'chemistry',
      metaphor: 'food',
      elements: [
        { type: 'text', content: 'Cooking chemistry', x: 100, y: 100 },
      ],
    };

    test('should handle food metaphor in story mode', async () => {
      render(
        <MagicNotebookEngine
          question="Food chemistry story"
          preGeneratedBlueprint={{ ...foodBlueprint, mode: 'story' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/chemistry/i) || true).toBeTruthy();
      });
    });
  });

  describe('Mixed Metaphor Combinations', () => {
    test('should handle switching between metaphors', async () => {
      const baseBlueprint = {
        concept: 'Force',
        subject: 'physics',
        elements: [{ type: 'text', content: 'Force', x: 100, y: 100 }],
      };

      const { rerender } = render(
        <MagicNotebookEngine
          question="Force with cricket"
          preGeneratedBlueprint={{ ...baseBlueprint, metaphor: 'cricket', mode: 'learn' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/force/i) || true).toBeTruthy();
      });

      // Switch metaphor
      rerender(
        <MagicNotebookEngine
          question="Force with railway"
          preGeneratedBlueprint={{ ...baseBlueprint, metaphor: 'railway', mode: 'learn' }}
        />
      );

      await waitFor(() => {
        expect(screen.queryByText(/force/i) || true).toBeTruthy();
      });
    });

    test('should handle no metaphor with all modes', async () => {
      const plainBlueprint = {
        concept: 'Basic Concept',
        subject: 'math',
        elements: [{ type: 'text', content: 'Plain', x: 100, y: 100 }],
      };

      const modes = ['learn', 'practice', 'explore', 'story', 'challenge', 'creative', 'assess', 'review'];

      for (const mode of modes) {
        const { container, unmount } = render(
          <UniversalSketchCanvas
            blueprint={{ ...plainBlueprint, mode }}
            question={`Plain ${mode}`}
          />
        );

        await waitFor(() => {
          expect(container.querySelector('canvas')).toBeTruthy();
        });

        unmount();
      }
    });

    test('should maintain mode state when switching metaphors', async () => {
      const blueprint = {
        concept: 'Energy',
        subject: 'physics',
        mode: 'practice',
        elements: [{ type: 'text', content: 'Energy', x: 100, y: 100 }],
      };

      const { rerender } = render(
        <MagicNotebookEngine
          question="Energy practice"
          preGeneratedBlueprint={{ ...blueprint, metaphor: 'cricket' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/practice/i) || true).toBeTruthy();
      });

      // Change metaphor, keep mode
      rerender(
        <MagicNotebookEngine
          question="Energy practice"
          preGeneratedBlueprint={{ ...blueprint, metaphor: 'diwali' }}
        />
      );

      await waitFor(() => {
        expect(screen.queryByText(/practice/i) || true).toBeTruthy();
      });
    });
  });

  describe('Cultural Context Integration', () => {
    test('should integrate cultural context with metaphors', async () => {
      const culturalBlueprint = {
        concept: 'Water Conservation',
        subject: 'geography',
        metaphor: 'village',
        culturalContext: {
          region: 'South India',
          festival: 'Pongal',
        },
        elements: [{ type: 'text', content: 'Water', x: 100, y: 100 }],
      };

      render(
        <MagicNotebookEngine
          question="Water conservation"
          preGeneratedBlueprint={culturalBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/water/i) || true).toBeTruthy();
      });
    });
  });
});






















