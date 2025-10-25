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
              "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://*.clerk.accounts.dev https://*.clerk.dev https://*.clerk.com", // Clerk scripts
              "worker-src 'self' blob:", // Allow Clerk Web Workers for token polling
              "child-src 'self' blob:", // Fallback for older browsers
              "style-src 'self' 'unsafe-inline'", // unsafe-inline needed for Tailwind/shadcn
              "img-src 'self' data: blob: https://*.clerk.com https://*.clerk.accounts.dev", // Clerk images
              "font-src 'self' data:", // System fonts + data URIs
              "connect-src 'self' blob: https://*.clerk.accounts.dev https://*.clerk.com https://*.clerk.dev https://*.vercel-storage.com https://*.railway.app https://clerk-telemetry.com https://*.clerk-telemetry.com", // Clerk API + telemetry
              "frame-src 'self' blob: https://*.blob.vercel-storage.com https://fdt3gmiqrtfo2acz.public.blob.vercel-storage.com https://*.clerk.accounts.dev https://*.clerk.com", // Clerk iframes + Vercel Blob PDFs
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
