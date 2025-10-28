export const SignalsColumnSkeleton = () => (
  <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
    <div className="flex items-center gap-2 mb-4">
      <div className="w-6 h-6 bg-gray-200 rounded"></div>
      <div className="h-5 bg-gray-200 rounded w-20"></div>
    </div>
    <div className="mb-4 rounded-lg overflow-hidden">
      <div className="w-full aspect-video bg-gray-200"></div>
    </div>
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
  </div>
)

export const TransferableInsightsColumnSkeleton = () => (
  <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
    <div className="flex items-center gap-2 mb-4">
      <div className="w-6 h-6 bg-gray-200 rounded"></div>
      <div className="h-5 bg-gray-200 rounded w-40"></div>
    </div>
    <div className="space-y-4">
      <div>
        <div className="h-3 bg-gray-200 rounded w-24 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-full mb-1"></div>
        <div className="h-3 bg-gray-200 rounded w-5/6"></div>
      </div>
      <div>
        <div className="h-3 bg-gray-200 rounded w-28 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-full mb-1"></div>
        <div className="h-3 bg-gray-200 rounded w-4/5"></div>
      </div>
      <div>
        <div className="h-3 bg-gray-200 rounded w-32 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-3/4 mb-1"></div>
        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      </div>
    </div>
  </div>
)

export const SparksPreviewColumnSkeleton = () => (
  <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
    <div className="flex items-center gap-2 mb-4">
      <div className="w-6 h-6 bg-gray-200 rounded"></div>
      <div className="h-5 bg-gray-200 rounded w-16"></div>
    </div>
    <div className="space-y-4">
      {[1, 2].map((i) => (
        <div key={i} className="bg-gray-50 rounded-lg overflow-hidden">
          <div className="aspect-video bg-gray-200"></div>
          <div className="p-3">
            <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-full mb-1"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      ))}
    </div>
  </div>
)
