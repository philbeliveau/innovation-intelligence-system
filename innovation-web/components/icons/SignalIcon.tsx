export const SignalIcon: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    aria-hidden="true"
  >
    <path
      d="M12 2L12 22M6 8L12 2L18 8M6 16L12 22L18 16"
      stroke="#5B9A99"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)
