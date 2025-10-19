import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Set Turbopack root explicitly to avoid workspace root inference issues
  turbopack: {
    root: __dirname,
  },

  // Exclude parent directories from file watching to avoid symlink issues
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.watchOptions = {
        ...config.watchOptions,
        ignored: ['**/venv/**', '**/node_modules/**', '../**'],
      };
    }
    return config;
  },

  // Content Security Policy headers for XSS protection (SEC-001)
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // unsafe-inline needed for Next.js dev mode
              "style-src 'self' 'unsafe-inline'", // unsafe-inline needed for Tailwind/shadcn
              "img-src 'self' data: blob:",
              "font-src 'self' data:",
              "connect-src 'self' blob:",
              "frame-src 'self' blob: https://*.blob.vercel-storage.com",
              "object-src 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join('; '),
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
