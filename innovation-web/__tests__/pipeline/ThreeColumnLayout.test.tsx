import { render, screen } from '@testing-library/react'
import { ThreeColumnLayout } from '@/components/pipeline/ThreeColumnLayout'

describe('ThreeColumnLayout', () => {
  it('renders children correctly', () => {
    render(
      <ThreeColumnLayout>
        <div data-testid="child-1">Column 1</div>
        <div data-testid="child-2">Column 2</div>
        <div data-testid="child-3">Column 3</div>
      </ThreeColumnLayout>
    )

    expect(screen.getByTestId('child-1')).toBeInTheDocument()
    expect(screen.getByTestId('child-2')).toBeInTheDocument()
    expect(screen.getByTestId('child-3')).toBeInTheDocument()
  })

  it('applies correct grid and gap classes', () => {
    const { container } = render(
      <ThreeColumnLayout>
        <div>Column 1</div>
      </ThreeColumnLayout>
    )

    const layoutDiv = container.firstChild as HTMLElement
    expect(layoutDiv.className).toMatch(/grid/)
    expect(layoutDiv.className).toMatch(/grid-cols-1/)
    expect(layoutDiv.className).toMatch(/md:grid-cols-3/)
    expect(layoutDiv.className).toMatch(/lg:grid-cols-3/)
    expect(layoutDiv.className).toMatch(/gap-4/)
    expect(layoutDiv.className).toMatch(/bg-gray-50/)
  })

  it('applies custom className when provided', () => {
    const { container } = render(
      <ThreeColumnLayout className="custom-class">
        <div>Column 1</div>
      </ThreeColumnLayout>
    )

    const layoutDiv = container.firstChild as HTMLElement
    expect(layoutDiv.className).toMatch(/custom-class/)
  })

  it('includes transition animation classes', () => {
    const { container } = render(
      <ThreeColumnLayout>
        <div>Column 1</div>
      </ThreeColumnLayout>
    )

    const layoutDiv = container.firstChild as HTMLElement
    expect(layoutDiv.className).toMatch(/transition-all/)
    expect(layoutDiv.className).toMatch(/duration-800/)
    expect(layoutDiv.className).toMatch(/ease-in-out/)
  })
})
