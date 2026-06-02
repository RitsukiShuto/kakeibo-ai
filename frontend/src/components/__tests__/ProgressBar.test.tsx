import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ProgressBar from '../ProgressBar';

describe('ProgressBar', () => {
  it('renders label and values correctly', () => {
    render(<ProgressBar label="Food" actual={30000} budget={50000} />);
    expect(screen.getByText('Food')).toBeInTheDocument();
    expect(screen.getByText(/¥30,000/)).toBeInTheDocument();
    expect(screen.getByText(/¥50,000/)).toBeInTheDocument();
  });

  it('calculates width correctly', () => {
    const { container } = render(<ProgressBar label="Food" actual={25000} budget={50000} />);
    const progressBar = container.querySelector('.progress-bar') as HTMLElement;
    expect(progressBar.style.width).toBe('50%');
  });

  it('shows over-pace color when actual > paceLimit', () => {
    const { container } = render(<ProgressBar label="Food" actual={16000} budget={30000} paceLimit={15000} />);
    const progressBar = container.querySelector('.progress-bar');
    expect(progressBar).toHaveClass('warning');
  });

  it('shows normal color when actual <= paceLimit', () => {
    const { container } = render(<ProgressBar label="Food" actual={14000} budget={30000} paceLimit={15000} />);
    const progressBar = container.querySelector('.progress-bar');
    expect(progressBar).not.toHaveClass('warning');
  });

  it('handles zero budget correctly', () => {
    const { container } = render(<ProgressBar label="Food" actual={1000} budget={0} />);
    const progressBar = container.querySelector('.progress-bar') as HTMLElement;
    expect(progressBar.style.width).toBe('0%');
  });

  it('renders pace marker and difference when provided', () => {
    render(<ProgressBar label="Food" actual={18000} budget={30000} paceLimit={15000} showDiff={true} />);
    // Note: The code produces +¥3,000 for excess
    expect(screen.getByText('+¥3,000')).toBeInTheDocument(); 
    const marker = document.querySelector('.pace-marker');
    expect(marker).toBeInTheDocument();
  });
});
