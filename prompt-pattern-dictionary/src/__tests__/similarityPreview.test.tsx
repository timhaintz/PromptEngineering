import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ORIENTATION_SECTIONS } from '../app/orientation/data/sections';
// Mock MermaidDiagram to silence act() warnings triggered by async rendering in tests
jest.mock('../components/diagram/MermaidDiagram', () => ({ __esModule: true, default: () => <div data-testid="mermaid-mock" /> }));

describe('SimilarityPreview orientation section', () => {
  it('renders sample similarity table with three rows and link to comparison view', () => {
    const section = ORIENTATION_SECTIONS.find(s => s.slug === 'similarity-preview');
    expect(section).toBeTruthy();
    const { container } = render(<>{section!.component}</>);
    const rows = container.querySelectorAll('table tbody tr');
    expect(rows.length).toBe(3);
    rows.forEach(row => {
      const scoreCell = row.querySelector('td:nth-child(2)');
      expect(scoreCell).toBeTruthy();
      expect(/\d\.\d{2}/.test(scoreCell!.textContent || '')).toBe(true);
    });
    const link = screen.getByRole('link', { name: /Open comparison view/i });
    expect(link).toBeInTheDocument();
  });

  it('includes accessible description element for preview table', () => {
    const section = ORIENTATION_SECTIONS.find(s => s.slug === 'similarity-preview');
    const { container } = render(<>{section!.component}</>);
    const alt = container.querySelector('#similarity-preview-alt');
    expect(alt).toBeTruthy();
    expect(alt!.textContent).toMatch(/Three sample patterns/);
  });
});
