import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import KPICard from '../KPICard';

describe('KPICard', () => {
  it('renders title and value', () => {
    render(<KPICard title="Total Expense" value="¥10,000" />);
    expect(screen.getByText('Total Expense')).toBeInTheDocument();
    expect(screen.getByText('¥10,000')).toBeInTheDocument();
  });

  it('renders trend when provided', () => {
    render(<KPICard title="Total Expense" value="¥10,000" trend="+¥1,000" trendType="negative" />);
    expect(screen.getByText('+¥1,000')).toBeInTheDocument();
    expect(screen.getByText('+¥1,000')).toHaveClass('negative');
  });

  it('renders positive trend class', () => {
    render(<KPICard title="Net Income" value="¥50,000" trend="+¥5,000" trendType="positive" />);
    expect(screen.getByText('+¥5,000')).toHaveClass('positive');
  });
});
