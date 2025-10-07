import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { OpportunityCard } from '@/components/results/OpportunityCard';

describe('OpportunityCard', () => {
  const mockOpportunity = {
    opportunity_number: 1,
    title: 'AI-Powered Personalized Nutrition Platform',
    strategic_rationale: 'Addresses growing consumer demand for personalized health solutions',
    implementation_approach: 'Partner with nutrition science labs, develop ML models',
    success_metrics: 'User engagement +40%, retention +25%',
    risks_and_mitigations: 'Data privacy concerns - implement GDPR compliance',
    estimated_timeline: '12-18 months',
    estimated_investment: '$2.5M - $4.0M',
  };

  describe('Rendering', () => {
    it('should display opportunity title', () => {
      render(<OpportunityCard opportunity={mockOpportunity} />);
      expect(screen.getByText(mockOpportunity.title)).toBeInTheDocument();
    });

    it('should show opportunity number', () => {
      render(<OpportunityCard opportunity={mockOpportunity} />);
      expect(screen.getByText(/Opportunity #1/)).toBeInTheDocument();
    });

    it('should display all sections', () => {
      render(<OpportunityCard opportunity={mockOpportunity} />);

      expect(screen.getByText(/Strategic Rationale/i)).toBeInTheDocument();
      expect(screen.getByText(/Implementation Approach/i)).toBeInTheDocument();
      expect(screen.getByText(/Success Metrics/i)).toBeInTheDocument();
      expect(screen.getByText(/Risks/i)).toBeInTheDocument();
      expect(screen.getByText(/Timeline/i)).toBeInTheDocument();
      expect(screen.getByText(/Investment/i)).toBeInTheDocument();
    });

    it('should render content from markdown', () => {
      render(<OpportunityCard opportunity={mockOpportunity} />);
      expect(screen.getByText(/personalized health solutions/i)).toBeInTheDocument();
    });
  });

  describe('Expand/Collapse', () => {
    it('should start collapsed by default', () => {
      render(<OpportunityCard opportunity={mockOpportunity} defaultExpanded={false} />);

      expect(screen.queryByText(/Implementation Approach/i)).not.toBeVisible();
    });

    it('should expand when clicked', async () => {
      const user = userEvent.setup();
      render(<OpportunityCard opportunity={mockOpportunity} defaultExpanded={false} />);

      await user.click(screen.getByRole('button', { name: /expand/i }));

      expect(screen.getByText(/Implementation Approach/i)).toBeVisible();
    });

    it('should collapse when clicked again', async () => {
      const user = userEvent.setup();
      render(<OpportunityCard opportunity={mockOpportunity} defaultExpanded={true} />);

      await user.click(screen.getByRole('button', { name: /collapse/i }));

      expect(screen.queryByText(/Implementation Approach/i)).not.toBeVisible();
    });
  });

  describe('Actions', () => {
    it('should show export button', () => {
      render(<OpportunityCard opportunity={mockOpportunity} showActions />);
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
    });

    it('should call onExport when export clicked', async () => {
      const mockOnExport = vi.fn();
      const user = userEvent.setup();

      render(
        <OpportunityCard opportunity={mockOpportunity} onExport={mockOnExport} showActions />
      );

      await user.click(screen.getByRole('button', { name: /export/i }));
      expect(mockOnExport).toHaveBeenCalledWith(mockOpportunity);
    });

    it('should show share button', () => {
      render(<OpportunityCard opportunity={mockOpportunity} showActions />);
      expect(screen.getByRole('button', { name: /share/i })).toBeInTheDocument();
    });

    it('should show favorite button', () => {
      render(<OpportunityCard opportunity={mockOpportunity} showActions />);
      expect(screen.getByRole('button', { name: /favorite/i })).toBeInTheDocument();
    });
  });

  describe('Visual Styling', () => {
    it('should apply highlight styling', () => {
      render(<OpportunityCard opportunity={mockOpportunity} highlighted />);

      const card = screen.getByTestId('opportunity-card');
      expect(card).toHaveClass('border-primary');
    });

    it('should show badge for high-value opportunities', () => {
      const highValueOpp = {
        ...mockOpportunity,
        estimated_investment: '$5M+',
      };

      render(<OpportunityCard opportunity={highValueOpp} showValueBadge />);
      expect(screen.getByText(/High Value/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<OpportunityCard opportunity={mockOpportunity} />);

      expect(screen.getByRole('article')).toHaveAttribute(
        'aria-label',
        expect.stringContaining(mockOpportunity.title)
      );
    });
  });
});
