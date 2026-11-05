import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import type { MetricStatus } from '../../lib/types';
import { StatusBadge } from './status-badge';

const CASES: { status: MetricStatus; label: string; colour: string }[] = [
  { status: 'typical', label: 'Typical', colour: 'green' },
  { status: 'above', label: 'Above typical', colour: 'amber' },
  { status: 'below', label: 'Below typical', colour: 'red' },
  { status: 'insufficient_data', label: 'Insufficient data', colour: 'slate' },
];

describe('StatusBadge', () => {
  it.each(CASES)('renders $status as a $colour badge labelled $label', ({ status, label, colour }) => {
    render(<StatusBadge status={status} />);

    const badge = screen.getByText(label);
    expect(badge).toHaveClass(`bg-${colour}-100`);
    expect(badge).toHaveClass(`text-${colour}-${status === 'insufficient_data' ? 600 : 800}`);
  });

  it('does not use the red of a problem for a surge above typical', () => {
    render(<StatusBadge status='above' />);

    expect(screen.getByText('Above typical').className).not.toMatch(/red/);
  });
});
