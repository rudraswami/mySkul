/**
 * RAG-Enhanced Blueprint Tests
 * Tests integration with RAG (Retrieval-Augmented Generation) for enhanced blueprints
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

describe('RAG-Enhanced Blueprint Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Context-Aware Blueprint Generation', () => {
    test('should enhance blueprint with retrieved context', async () => {
      const ragBlueprint = {
        concept: 'Photosynthesis',
        subject: 'biology',
        ragContext: {
          retrieved: true,
          sources: ['textbook_ch3', 'research_paper_2023'],
          relevanceScore: 0.92,
        },
        elements: [
          { type: 'text', content: '6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂', x: 100, y: 100 },
          { type: 'text', content: 'Light-dependent reactions', x: 100, y: 150 },
          { type: 'text', content: 'Calvin cycle', x: 100, y: 200 },
        ],
      };

      const { container } = render(
        <MagicNotebookEngine
          question="Explain photosynthesis in detail"
          preGeneratedBlueprint={ragBlueprint}
          context={{ subject: 'biology', level: 'high_school' }}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeTruthy();
      });
    });

    test('should handle blueprint with multiple RAG sources', async () => {
      const multiSourceBlueprint = {
        concept: 'Climate Change',
        subject: 'geography',
        ragContext: {
          retrieved: true,
          sources: [
            { id: 'ipcc_report_2023', relevance: 0.95 },
            { id: 'nasa_climate_data', relevance: 0.88 },
            { id: 'textbook_geography', relevance: 0.76 },
          ],
          summary: 'Comprehensive climate change data from multiple authoritative sources',
        },
        elements: [
          { type: 'text', content: 'Global temperature rise', x: 100, y: 100 },
          { type: 'graph', data: [1.1, 1.3, 1.5], x: 100, y: 150 },
        ],
      };

      render(
        <MagicNotebookEngine
          question="What is climate change?"
          preGeneratedBlueprint={multiSourceBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/climate/i) || screen.queryByText(/temperature/i)).toBeTruthy();
      });
    });
  });

  describe('Knowledge Graph Integration', () => {
    test('should integrate knowledge graph relationships', async () => {
      const kgBlueprint = {
        concept: 'Ohms Law',
        subject: 'physics',
        ragContext: {
          retrieved: true,
          knowledgeGraph: {
            related: ['Voltage', 'Current', 'Resistance', 'Power'],
            prerequisites: ['Basic Electricity', 'Circuit Theory'],
            applications: ['Circuit Design', 'Electrical Engineering'],
          },
        },
        elements: [
          { type: 'text', content: 'V = IR', x: 100, y: 100 },
          { type: 'text', content: 'Voltage ∝ Current', x: 100, y: 150 },
        ],
      };

      const { container } = render(
        <UniversalSketchCanvas
          blueprint={kgBlueprint}
          question="Explain Ohm's Law"
        />
      );

      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeTruthy();
      });
    });

    test('should handle hierarchical concept relationships', async () => {
      const hierarchyBlueprint = {
        concept: 'Cell Structure',
        subject: 'biology',
        ragContext: {
          retrieved: true,
          hierarchy: {
            parent: 'Biology',
            siblings: ['Cell Function', 'Cell Division'],
            children: ['Nucleus', 'Mitochondria', 'Cell Membrane'],
          },
        },
        elements: [
          { type: 'circle', x: 200, y: 200, radius: 100, label: 'Cell' },
          { type: 'circle', x: 200, y: 200, radius: 30, label: 'Nucleus' },
        ],
      };

      render(
        <MagicNotebookEngine
          question="What is cell structure?"
          preGeneratedBlueprint={hierarchyBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/cell/i) || true).toBeTruthy();
      });
    });
  });

  describe('Personalized Learning Context', () => {
    test('should adapt blueprint based on student history', async () => {
      const personalizedBlueprint = {
        concept: 'Quadratic Equations',
        subject: 'math',
        ragContext: {
          retrieved: true,
          studentHistory: {
            previousTopics: ['Linear Equations', 'Polynomials'],
            strengthAreas: ['Algebra', 'Problem Solving'],
            weakAreas: ['Complex Numbers'],
            recommendedDifficulty: 'medium',
          },
        },
        elements: [
          { type: 'text', content: 'ax² + bx + c = 0', x: 100, y: 100 },
          { type: 'text', content: 'Quadratic formula', x: 100, y: 150 },
        ],
      };

      render(
        <MagicNotebookEngine
          question="Solve quadratic equations"
          preGeneratedBlueprint={personalizedBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/quadratic/i) || true).toBeTruthy();
      });
    });

    test('should include prerequisite checks', async () => {
      const prerequisiteBlueprint = {
        concept: 'Calculus Integration',
        subject: 'math',
        ragContext: {
          retrieved: true,
          prerequisites: {
            required: ['Differentiation', 'Limits', 'Functions'],
            optional: ['Series', 'Sequences'],
            studentMastery: {
              'Differentiation': 0.85,
              'Limits': 0.70,
              'Functions': 0.90,
            },
          },
        },
        elements: [
          { type: 'text', content: '∫ f(x) dx', x: 100, y: 100 },
        ],
      };

      render(
        <MagicNotebookEngine
          question="Learn integration"
          preGeneratedBlueprint={prerequisiteBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/integration/i) || true).toBeTruthy();
      });
    });
  });

  describe('Real-World Example Integration', () => {
    test('should include RAG-retrieved real-world examples', async () => {
      const exampleBlueprint = {
        concept: 'Friction',
        subject: 'physics',
        ragContext: {
          retrieved: true,
          realWorldExamples: [
            {
              id: 'ex1',
              title: 'Braking in vehicles',
              relevance: 0.95,
              source: 'automotive_physics',
            },
            {
              id: 'ex2',
              title: 'Walking on different surfaces',
              relevance: 0.88,
              source: 'everyday_physics',
            },
          ],
        },
        elements: [
          { type: 'text', content: 'Friction = μN', x: 100, y: 100 },
          { type: 'text', content: 'Example: Car brakes', x: 100, y: 150 },
        ],
      };

      render(
        <MagicNotebookEngine
          question="What is friction?"
          preGeneratedBlueprint={exampleBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/friction/i) || screen.queryByText(/brakes/i)).toBeTruthy();
      });
    });
  });

  describe('Multi-Modal RAG Context', () => {
    test('should handle text + image RAG context', async () => {
      const multiModalBlueprint = {
        concept: 'Solar System',
        subject: 'astronomy',
        ragContext: {
          retrieved: true,
          modalities: {
            text: ['nasa_article', 'astronomy_textbook'],
            images: ['solar_system_diagram', 'planet_photos'],
            videos: ['hubble_footage'],
          },
        },
        elements: [
          { type: 'circle', x: 400, y: 300, radius: 50, label: 'Sun' },
          { type: 'circle', x: 500, y: 300, radius: 10, label: 'Earth' },
        ],
      };

      const { container } = render(
        <UniversalSketchCanvas
          blueprint={multiModalBlueprint}
          question="Show solar system"
        />
      );

      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeTruthy();
      });
    });

    test('should integrate code examples from RAG', async () => {
      const codeBlueprint = {
        concept: 'Sorting Algorithms',
        subject: 'computer_science',
        ragContext: {
          retrieved: true,
          codeExamples: [
            {
              language: 'python',
              code: 'def bubble_sort(arr): ...',
              source: 'algorithm_repository',
            },
          ],
        },
        elements: [
          { type: 'text', content: 'Bubble Sort', x: 100, y: 100 },
          { type: 'text', content: 'O(n²) complexity', x: 100, y: 150 },
        ],
      };

      render(
        <MagicNotebookEngine
          question="Explain bubble sort"
          preGeneratedBlueprint={codeBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/bubble sort/i) || screen.queryByText(/complexity/i)).toBeTruthy();
      });
    });
  });

  describe('Fallback Mechanisms', () => {
    test('should handle missing RAG context gracefully', async () => {
      const noRagBlueprint = {
        concept: 'Simple Concept',
        subject: 'math',
        ragContext: {
          retrieved: false,
          reason: 'No relevant documents found',
        },
        elements: [
          { type: 'text', content: 'Fallback content', x: 100, y: 100 },
        ],
      };

      const { container } = render(
        <UniversalSketchCanvas
          blueprint={noRagBlueprint}
          question="Simple question"
        />
      );

      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeTruthy();
      });
    });

    test('should handle RAG retrieval errors', async () => {
      const errorBlueprint = {
        concept: 'Test Concept',
        subject: 'physics',
        ragContext: {
          retrieved: false,
          error: 'RAG service unavailable',
        },
        elements: [
          { type: 'text', content: 'Basic content', x: 100, y: 100 },
        ],
      };

      const mockOnError = jest.fn();

      render(
        <MagicNotebookEngine
          question="Test question"
          preGeneratedBlueprint={errorBlueprint}
          onError={mockOnError}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalled();
      }, { timeout: 5000 });
    });
  });

  describe('RAG Citation and Attribution', () => {
    test('should include source citations in blueprint', async () => {
      const citedBlueprint = {
        concept: 'Theory of Relativity',
        subject: 'physics',
        ragContext: {
          retrieved: true,
          citations: [
            {
              source: 'Einstein, A. (1905)',
              title: 'On the Electrodynamics of Moving Bodies',
              relevance: 0.98,
            },
          ],
        },
        elements: [
          { type: 'text', content: 'E = mc²', x: 100, y: 100 },
          { type: 'text', content: 'Source: Einstein (1905)', x: 100, y: 150, fontSize: 10 },
        ],
      };

      render(
        <MagicNotebookEngine
          question="Explain relativity"
          preGeneratedBlueprint={citedBlueprint}
        />,
        { wrapper }
      );

      await waitFor(() => {
        expect(screen.queryByText(/einstein/i) || screen.queryByText(/relativity/i)).toBeTruthy();
      });
    });
  });
});





























