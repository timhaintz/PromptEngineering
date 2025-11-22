import React from 'react';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import OrientationLayout from '@/app/orientation/layout';
import OrientationNav from '@/app/orientation/components/OrientationNav';

// Smoke test for Orientation P0 accessibility additions.
// Ensures skip links & provenance badge render without critical axe violations.

describe('Orientation accessibility baseline', () => {
  it('renders layout with skip links and passes axe (no serious violations)', async () => {
    const { container } = render(
      <OrientationLayout>
        <h1>Orientation</h1>
        <OrientationNav />
        <p>Sample content block.</p>
      </OrientationLayout>
    );
    const results = await axe(container);
    // Filter out moderate/minor; we fail if serious/critical are present.
    const serious = results.violations.filter(v => ['serious','critical'].includes(v.impact || ''));
    expect(serious).toHaveLength(0);
  });
});
