import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import AIReview from '../pages/AIReview';

// Mock API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
  }
}));

describe('AIReview Component', () => {
  it('renders the AI Review header', () => {
    render(<AIReview />);
    expect(screen.getByText('AI Review')).toBeDefined();
  });

  it('renders timeframes buttons', () => {
    render(<AIReview />);
    expect(screen.getByText('daily')).toBeDefined();
    expect(screen.getByText('weekly')).toBeDefined();
    expect(screen.getByText('monthly')).toBeDefined();
  });
});
