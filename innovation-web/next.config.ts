import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
};

export default nextConfig;
