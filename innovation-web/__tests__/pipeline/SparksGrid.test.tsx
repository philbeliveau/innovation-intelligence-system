import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import SparksGrid from '@/components/pipeline/SparksGrid'

const mockSparks = [
  {
    id: 'spark-1',
    title: 'Spark 1',
    summary: 'Summary 1',
    content: 'Content 1',
  },
  {
    id: 'spark-2',
    title: 'Spark 2',
    summary: 'Summary 2',
    content: 'Content 2',
  },
  {
    id: 'spark-3',
    title: 'Spark 3',
    summary: 'Summary 3',
    content: 'Content 3',
  },
  {
    id: 'spark-4',
    title: 'Spark 4',
    summary: 'Summary 4',
    content: 'Content 4',
  },
]

describe('SparksGrid', () => {
  it('renders all sparks in grid', () => {
    const onCardClick = jest.fn()
    render(<SparksGrid sparks={mockSparks} onCardClick={onCardClick} />)

    expect(screen.getByText('Spark 1')).toBeInTheDocument()
    expect(screen.getByText('Spark 2')).toBeInTheDocument()
    expect(screen.getByText('Spark 3')).toBeInTheDocument()
    expect(screen.getByText('Spark 4')).toBeInTheDocument()
  })

  it('renders empty state when no sparks', () => {
    const onCardClick = jest.fn()
    render(<SparksGrid sparks={[]} onCardClick={onCardClick} />)

    expect(screen.getByText('No sparks generated yet.')).toBeInTheDocument()
  })

  it('uses responsive grid classes', () => {
    const onCardClick = jest.fn()
    const { container } = render(<SparksGrid sparks={mockSparks} onCardClick={onCardClick} />)

    const grid = container.querySelector('.grid')
    expect(grid).toHaveClass('grid-cols-1')
    expect(grid).toHaveClass('md:grid-cols-2')
    expect(grid).toHaveClass('lg:grid-cols-2')
  })

  it('assigns correct numbers to sparks', () => {
    const onCardClick = jest.fn()
    render(<SparksGrid sparks={mockSparks} onCardClick={onCardClick} />)

    // SparkCard shows numbers as text content
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('4')).toBeInTheDocument()
  })

  it('applies max-width constraint', () => {
    const onCardClick = jest.fn()
    const { container } = render(<SparksGrid sparks={mockSparks} onCardClick={onCardClick} />)

    const wrapper = container.firstChild as HTMLElement
    expect(wrapper).toHaveClass('max-w-screen-xl')
  })
})
