import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import IconNavigation from '@/components/pipeline/IconNavigation'

describe('IconNavigation', () => {
  it('renders all three icons with labels', () => {
    const onNavigate = jest.fn()
    render(<IconNavigation activeSection="sparks" onNavigate={onNavigate} />)

    expect(screen.getByText('Signals')).toBeInTheDocument()
    expect(screen.getByText('Insights')).toBeInTheDocument()
    expect(screen.getByText('Sparks')).toBeInTheDocument()
  })

  it('highlights active section with teal color', () => {
    const onNavigate = jest.fn()
    const { container } = render(<IconNavigation activeSection="sparks" onNavigate={onNavigate} />)

    const sparksButton = screen.getByRole('button', { name: /navigate to sparks/i })
    expect(sparksButton).toHaveClass('text-[#5B9A99]')
  })

  it('shows inactive sections in gray', () => {
    const onNavigate = jest.fn()
    render(<IconNavigation activeSection="sparks" onNavigate={onNavigate} />)

    const signalsButton = screen.getByRole('button', { name: /navigate to signals/i })
    const insightsButton = screen.getByRole('button', { name: /navigate to insights/i })

    expect(signalsButton).toHaveClass('text-gray-400')
    expect(insightsButton).toHaveClass('text-gray-400')
  })

  it('calls onNavigate when icon clicked', () => {
    const onNavigate = jest.fn()
    render(<IconNavigation activeSection="sparks" onNavigate={onNavigate} />)

    const signalsButton = screen.getByRole('button', { name: /navigate to signals/i })
    fireEvent.click(signalsButton)

    expect(onNavigate).toHaveBeenCalledWith('signals')
  })

  it('renders with center alignment', () => {
    const onNavigate = jest.fn()
    const { container } = render(<IconNavigation activeSection="sparks" onNavigate={onNavigate} />)

    const wrapper = container.firstChild as HTMLElement
    expect(wrapper).toHaveClass('justify-center')
  })
})
