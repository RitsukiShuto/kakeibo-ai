import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MonthSelector from '../MonthSelector';

describe('MonthSelector', () => {
  it('displays current month and triggers change', () => {
    const onChange = vi.fn();
    render(<MonthSelector currentMonth="2026-06" onChange={onChange} />);
    expect(screen.getByText('2026年 6月')).toBeInTheDocument();
    fireEvent.click(screen.getByText('◀'));
    expect(onChange).toHaveBeenCalled();
  });
});
