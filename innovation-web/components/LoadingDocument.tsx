'use client'

// Innovation Intelligence System - Document Loading Animation
// Browser-style loading animation with animated trace flows

export default function LoadingDocument() {
  return (
    <div className="flex justify-center items-center h-full w-full overflow-hidden">
      <div className="w-full h-full">
        <svg
          id="browser"
          viewBox="0 0 800 600"
          className="w-full h-full"
          style={{ overflow: 'hidden' }}
        >
          {/* Gradient Definitions for Trace Flows */}
          <defs>
            <linearGradient id="traceGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00ccff" stopOpacity="0" />
              <stop offset="50%" stopColor="#00ccff" stopOpacity="1" />
              <stop offset="100%" stopColor="#00ccff" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="traceGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00ffcc" stopOpacity="0" />
              <stop offset="50%" stopColor="#00ffcc" stopOpacity="1" />
              <stop offset="100%" stopColor="#00ffcc" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="traceGradient3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0099ff" stopOpacity="0" />
              <stop offset="50%" stopColor="#0099ff" stopOpacity="1" />
              <stop offset="100%" stopColor="#0099ff" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="traceGradient4" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#33ccff" stopOpacity="0" />
              <stop offset="50%" stopColor="#33ccff" stopOpacity="1" />
              <stop offset="100%" stopColor="#33ccff" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Grid Background */}
          <g id="grid">
            {Array.from({ length: 20 }).map((_, i) => (
              <line
                key={`v-${i}`}
                className="grid-line"
                x1={i * 40}
                y1="0"
                x2={i * 40}
                y2="600"
              />
            ))}
            {Array.from({ length: 15 }).map((_, i) => (
              <line
                key={`h-${i}`}
                className="grid-line"
                x1="0"
                y1={i * 40}
                x2="800"
                y2={i * 40}
              />
            ))}
          </g>

          {/* Browser Frame */}
          <rect
            className="browser-frame"
            x="100"
            y="100"
            width="600"
            height="400"
            rx="8"
          />

          {/* Browser Top Bar */}
          <rect
            className="browser-top"
            x="100"
            y="100"
            width="600"
            height="40"
            rx="8"
          />
          <rect
            className="browser-top"
            x="100"
            y="132"
            width="600"
            height="8"
          />

          {/* Browser Dots */}
          <circle cx="120" cy="120" r="6" fill="#FF5F56" />
          <circle cx="140" cy="120" r="6" fill="#FFBD2E" />
          <circle cx="160" cy="120" r="6" fill="#27C93F" />

          {/* Loading Text */}
          <text className="loading-text" x="400" y="125" textAnchor="middle">
            Analyzing document...
          </text>

          {/* Document Skeleton Content */}
          <g id="skeleton-content">
            {/* Title skeleton */}
            <rect className="skeleton" x="130" y="170" width="400" height="20" />

            {/* Paragraph skeletons */}
            <rect className="skeleton" x="130" y="210" width="540" height="12" />
            <rect className="skeleton" x="130" y="230" width="520" height="12" />
            <rect className="skeleton" x="130" y="250" width="500" height="12" />

            {/* Section skeleton */}
            <rect className="skeleton" x="130" y="290" width="300" height="16" />
            <rect className="skeleton" x="130" y="320" width="540" height="12" />
            <rect className="skeleton" x="130" y="340" width="530" height="12" />

            {/* Image placeholder skeleton */}
            <rect className="skeleton" x="130" y="380" width="250" height="100" />

            {/* More text skeletons */}
            <rect className="skeleton" x="400" y="380" width="270" height="12" />
            <rect className="skeleton" x="400" y="400" width="260" height="12" />
            <rect className="skeleton" x="400" y="420" width="270" height="12" />
          </g>

          {/* Animated Trace Flows */}
          <g id="trace-flows">
            <path
              className="trace-flow"
              d="M 50,150 L 100,150 L 100,300"
            />
            <path
              className="trace-flow"
              d="M 700,200 L 750,200 L 750,400"
              style={{ animationDelay: '1s' }}
            />
            <path
              className="trace-flow"
              d="M 100,500 L 300,500 L 300,520"
              style={{ animationDelay: '2s' }}
            />
            <path
              className="trace-flow"
              d="M 500,520 L 700,520 L 700,500"
              style={{ animationDelay: '0.5s' }}
            />
          </g>
        </svg>

        <style jsx>{`
          .grid-line {
            stroke: #E5E5E5;
            stroke-width: 0.5;
          }

          .browser-frame {
            fill: #FFFFFF;
            stroke: #CCCCCC;
            stroke-width: 1;
            filter: drop-shadow(0 0 10px rgba(0, 0, 0, 0.08));
          }

          .browser-top {
            fill: #F5F5F5;
          }

          .loading-text {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            fill: #333333;
            font-weight: 500;
          }

          .skeleton {
            fill: #E0E0E0;
            rx: 4;
            ry: 4;
            animation: pulse 1.8s ease-in-out infinite;
            filter: drop-shadow(0 0 3px rgba(0, 0, 0, 0.03));
          }

          @keyframes pulse {
            0% {
              fill: #E0E0E0;
            }
            50% {
              fill: #F5F5F5;
            }
            100% {
              fill: #E0E0E0;
            }
          }

          .trace-flow {
            stroke-width: 1;
            fill: none;
            stroke-dasharray: 120 600;
            stroke-dashoffset: 720;
            animation: flow 5s linear infinite;
            opacity: 0.95;
            stroke-linejoin: round;
            filter: drop-shadow(0 0 8px currentColor) blur(0.5px);
          }

          .trace-flow:nth-child(1) {
            stroke: url(#traceGradient1);
          }
          .trace-flow:nth-child(2) {
            stroke: url(#traceGradient2);
          }
          .trace-flow:nth-child(3) {
            stroke: url(#traceGradient3);
          }
          .trace-flow:nth-child(4) {
            stroke: url(#traceGradient4);
          }

          @keyframes flow {
            from {
              stroke-dashoffset: 720;
            }
            to {
              stroke-dashoffset: 0;
            }
          }
        `}</style>
      </div>
    </div>
  )
}
