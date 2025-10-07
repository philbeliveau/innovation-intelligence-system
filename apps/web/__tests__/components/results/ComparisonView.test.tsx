import { describe, it, expect, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComparisonView } from '@/components/results/ComparisonView';

describe('ComparisonView', () => {
  const mockBrand1Results = {
    runId: 'run-1',
    brandId: 'lactalis-canada',
    brandName: 'Lactalis Canada',
    opportunities: [
      { opportunity_number: 1, title: 'Lactalis Opportunity 1' },
      { opportunity_number: 2, title: 'Lactalis Opportunity 2' },
    ],
    totalCost: 0.42,
  };

  const mockBrand2Results = {
    runId: 'run-2',
    brandId: 'danone',
    brandName: 'Danone',
    opportunities: [
      { opportunity_number: 1, title: 'Danone Opportunity 1' },
      { opportunity_number: 2, title: 'Danone Opportunity 2' },
    ],
    totalCost: 0.38,
  };

  describe('Side-by-Side Layout', () => {
    it('should display both brands side by side', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
        />
      );

      expect(screen.getByText('Lactalis Canada')).toBeInTheDocument();
      expect(screen.getByText('Danone')).toBeInTheDocument();
    });

    it('should show opportunities for both brands', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
        />
      );

      expect(screen.getByText('Lactalis Opportunity 1')).toBeInTheDocument();
      expect(screen.getByText('Danone Opportunity 1')).toBeInTheDocument();
    });

    it('should align opportunities by number', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          alignByNumber
        />
      );

      const opp1Row = screen.getByTestId('opportunity-row-1');
      expect(within(opp1Row).getByText('Lactalis Opportunity 1')).toBeInTheDocument();
      expect(within(opp1Row).getByText('Danone Opportunity 1')).toBeInTheDocument();
    });
  });

  describe('Cost Comparison', () => {
    it('should display costs for both brands', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
        />
      );

      expect(screen.getByText(/\$0\.42/)).toBeInTheDocument();
      expect(screen.getByText(/\$0\.38/)).toBeInTheDocument();
    });

    it('should highlight cheaper brand', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          highlightCheaper
        />
      );

      const brand2Cost = screen.getByTestId('brand-2-cost');
      expect(brand2Cost).toHaveClass('bg-success-light');
    });

    it('should show cost difference', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          showCostDifference
        />
      );

      expect(screen.getByText(/\$0\.04 difference/i)).toBeInTheDocument();
    });
  });

  describe('Filtering and Navigation', () => {
    it('should filter opportunities by keyword', async () => {
      const user = userEvent.setup();
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          searchable
        />
      );

      const searchInput = screen.getByPlaceholderText(/search/i);
      await user.type(searchInput, 'Lactalis');

      expect(screen.getByText('Lactalis Opportunity 1')).toBeInTheDocument();
      expect(screen.queryByText('Danone Opportunity 1')).not.toBeInTheDocument();
    });

    it('should navigate between opportunity pairs', async () => {
      const user = userEvent.setup();
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          navigable
        />
      );

      await user.click(screen.getByRole('button', { name: /next/i }));

      expect(screen.getByText('Lactalis Opportunity 2')).toBeVisible();
      expect(screen.getByText('Danone Opportunity 2')).toBeVisible();
    });
  });

  describe('Export Functionality', () => {
    it('should export comparison as CSV', async () => {
      const mockOnExport = vi.fn();
      const user = userEvent.setup();

      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          onExport={mockOnExport}
        />
      );

      await user.click(screen.getByRole('button', { name: /export/i }));
      await user.click(screen.getByText(/CSV/i));

      expect(mockOnExport).toHaveBeenCalledWith('csv');
    });

    it('should export comparison as PDF', async () => {
      const mockOnExport = vi.fn();
      const user = userEvent.setup();

      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
          onExport={mockOnExport}
        />
      );

      await user.click(screen.getByRole('button', { name: /export/i }));
      await user.click(screen.getByText(/PDF/i));

      expect(mockOnExport).toHaveBeenCalledWith('pdf');
    });
  });

  describe('Responsive Layout', () => {
    it('should stack brands vertically on mobile', () => {
      global.innerWidth = 375;
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
        />
      );

      const container = screen.getByTestId('comparison-container');
      expect(container).toHaveClass('flex-col');
    });
  });

  describe('Accessibility', () => {
    it('should have proper landmark roles', () => {
      render(
        <ComparisonView
          brand1Results={mockBrand1Results}
          brand2Results={mockBrand2Results}
        />
      );

      expect(screen.getByRole('region', { name: /comparison/i })).toBeInTheDocument();
    });
  });
});
