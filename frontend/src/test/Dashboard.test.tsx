import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import client from '../api/client';
import { describe, it, expect, beforeEach, vi } from 'vitest';

vi.mock('../api/client', () => {
  return {
    default: {
      get: vi.fn(),
    },
  };
});

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders loading state initially', () => {
    (client.get as any).mockImplementation(() => new Promise(() => {})); // Never resolves
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders dashboard content after fetching data', async () => {
    (client.get as any).mockImplementation((url: string) => {
      if (url.includes('/api/kpi')) {
        return Promise.resolve({ data: { budget: 300000, actual: 185400, remaining: 114600, total_assets: 4500200 } });
      }
      if (url.includes('/api/budget-actual')) {
        return Promise.resolve({ data: [
          { category: '食費', budget: 60000, actual: 45000, pace_limit: 50000 },
          { category: '家賃', budget: 80000, actual: 80000, pace_limit: 80000 }
        ] });
      }
      if (url.includes('/api/assets')) {
        return Promise.resolve({ data: [] });
      }
      if (url.includes('/api/stats/flow')) {
        return Promise.resolve({ data: { nodes: [{id:0, name:"給与"}], links: [] } });
      }
      if (url.includes('/api/analysis-history/latest-summary')) {
        return Promise.resolve({ data: { summary: "順調です。" } });
      }
      if (url.includes('/api/analysis-history/form')) {
        return Promise.resolve({ data: ["W", "L", "W", "W"] });
      }
      if (url.includes('/api/transactions')) {
        return Promise.resolve({ data: [] });
      }
      if (url.includes('/api/reimbursements/pending')) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: {} });
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Kakeibo-ai')).toBeInTheDocument();
    });

    // Overview KPIs
    expect(screen.getByText('合計支出')).toBeInTheDocument();
    expect(screen.getByText('¥185,400')).toBeInTheDocument();

    // AI Insights
    expect(screen.getByText('順調です。')).toBeInTheDocument();

    // Operations
    expect(screen.getByText('Operations')).toBeInTheDocument();
    expect(screen.getByText('変動費の予実管理')).toBeInTheDocument();
    expect(screen.getByText('食費')).toBeInTheDocument();

    // Sankey section title
    expect(screen.getByText('Cash Flow Analysis')).toBeInTheDocument();
  });
});
