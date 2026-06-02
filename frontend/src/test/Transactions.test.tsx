import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Transactions from '../pages/Transactions';

// Mock API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
}));

describe('Transactions Component', () => {
  it('renders the transactions header', () => {
    render(<Transactions />);
    expect(screen.getByText('Transactions')).toBeDefined();
  });

  it('renders search input', () => {
    render(<Transactions />);
    const searchInput = screen.getByPlaceholderText('明細を検索...');
    expect(searchInput).toBeDefined();
  });
});
