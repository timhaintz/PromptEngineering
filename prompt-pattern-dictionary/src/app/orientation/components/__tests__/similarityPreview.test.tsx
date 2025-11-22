import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Import the sections and locate the SimilarityPreview section for rendering its component
import { ORIENTATION_SECTIONS } from '../../data/sections';

describe('SimilarityPreview orientation section', () => {
  it('renders sample similarity table with three rows and link to comparison view', () => {
    const section = ORIENTATION_SECTIONS.find(s => s.slug === 'similarity-preview');
    expect(section).toBeTruthy();
    const { container } = render(<>{section!.component}</>);
    // Table rows (header + 3 samples)
    const rows = container.querySelectorAll('table tbody tr');
    expect(rows.length).toBe(3);
    // Check score formatting (two decimals)
    rows.forEach(row => {
      const scoreCell = row.querySelector('td:nth-child(2)');
      expect(scoreCell).toBeTruthy();
      expect(/\d\.\d{2}/.test(scoreCell!.textContent || '')).toBe(true);
    });
    // Comparison link
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
