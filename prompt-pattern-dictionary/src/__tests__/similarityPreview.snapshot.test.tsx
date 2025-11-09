import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ORIENTATION_SECTIONS } from '../app/orientation/data/sections';

// Mock MermaidDiagram to silence act warnings & reduce noise
jest.mock('../components/diagram/MermaidDiagram', () => ({ __esModule: true, default: () => <div data-testid="mermaid-mock" /> }));

describe('SimilarityPreview snapshot', () => {
  it('matches snapshot structure (table + optional graph container)', () => {
    const section = ORIENTATION_SECTIONS.find(s => s.slug === 'similarity-preview');
    const { container } = render(<>{section!.component}</>);
    expect(container.firstChild).toMatchSnapshot();
  });
});
