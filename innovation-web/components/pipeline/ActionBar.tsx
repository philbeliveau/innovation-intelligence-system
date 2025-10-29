import { Download, Loader2 } from 'lucide-react'

interface ActionBarProps {
  onDownloadAll: () => void
  onNewPipeline: () => void
  isDownloading?: boolean
  sparkCount: number
}

export default function ActionBar({
  onDownloadAll,
  onNewPipeline,
  isDownloading = false,
  sparkCount,
}: ActionBarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 safe-bottom">
      <div className="max-w-screen-xl mx-auto px-4 md:px-6 py-3 md:py-4 flex flex-col md:flex-row justify-between items-center gap-3 md:gap-4">
        <button
          onClick={onDownloadAll}
          disabled={isDownloading || sparkCount === 0}
          className="
            flex items-center gap-2 px-6 py-3
            bg-[#5B9A99] text-white rounded-lg
            hover:bg-[#4A7F7E] active:bg-[#3A6F6E]
            transition-colors disabled:opacity-50 disabled:cursor-not-allowed
            w-full md:w-auto justify-center
            min-h-[44px]
          "
          aria-label={`Download all ${sparkCount} sparks`}
        >
          {isDownloading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Downloading...
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              Download All ({sparkCount})
            </>
          )}
        </button>

        <button
          onClick={onNewPipeline}
          className="
            px-6 py-3
            bg-white border-2 border-[#5B9A99] text-[#5B9A99] rounded-lg
            hover:bg-[#5B9A99] hover:text-white
            active:bg-[#4A7F7E] active:border-[#4A7F7E]
            transition-colors
            w-full md:w-auto justify-center
            min-h-[44px]
          "
          aria-label="Start new pipeline"
        >
          New Pipeline
        </button>
      </div>
    </div>
  )
}
