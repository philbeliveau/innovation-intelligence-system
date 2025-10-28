import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import ActionBar from '@/components/pipeline/ActionBar'

describe('ActionBar', () => {
  it('renders both action buttons', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        sparkCount={5}
      />
    )

    expect(screen.getByText(/download all \(5\)/i)).toBeInTheDocument()
    expect(screen.getByText('New Pipeline')).toBeInTheDocument()
  })

  it('calls onDownloadAll when Download button clicked', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        sparkCount={5}
      />
    )

    const downloadButton = screen.getByText(/download all/i)
    fireEvent.click(downloadButton)

    expect(onDownloadAll).toHaveBeenCalledTimes(1)
  })

  it('calls onNewPipeline when New Pipeline button clicked', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        sparkCount={5}
      />
    )

    const newPipelineButton = screen.getByText('New Pipeline')
    fireEvent.click(newPipelineButton)

    expect(onNewPipeline).toHaveBeenCalledTimes(1)
  })

  it('disables download button when sparkCount is 0', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        sparkCount={0}
      />
    )

    const downloadButton = screen.getByText(/download all/i)
    expect(downloadButton).toBeDisabled()
  })

  it('shows loading spinner when isDownloading is true', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        isDownloading={true}
        sparkCount={5}
      />
    )

    expect(screen.getByText('Downloading...')).toBeInTheDocument()
  })

  it('has fixed positioning at bottom', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    const { container } = render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        sparkCount={5}
      />
    )

    const actionBar = container.firstChild as HTMLElement
    expect(actionBar).toHaveClass('fixed')
    expect(actionBar).toHaveClass('bottom-0')
  })

  it('stacks buttons vertically on mobile', () => {
    const onDownloadAll = jest.fn()
    const onNewPipeline = jest.fn()
    const { container } = render(
      <ActionBar
        onDownloadAll={onDownloadAll}
        onNewPipeline={onNewPipeline}
        sparkCount={5}
      />
    )

    const innerContainer = container.querySelector('.flex')
    expect(innerContainer).toHaveClass('flex-col')
    expect(innerContainer).toHaveClass('md:flex-row')
  })
})
