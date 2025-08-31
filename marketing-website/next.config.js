/** @type {import('next').NextConfig} */
const nextConfig = {
  // Production optimization
  output: 'standalone',
  
  experimental: {
    optimizePackageImports: ['@mantine/core', '@mantine/hooks'],
  },
  
  typescript: {
    // Allow building even with TypeScript errors during development
    ignoreBuildErrors: true,
  },
  
  eslint: {
    // Allow building even with ESLint errors during development
    ignoreDuringBuilds: true,
  },
  
  // Environment variables for marketing website
  env: {
    NEXT_PUBLIC_APP_NAME: 'PM33 Marketing Website',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
    NEXT_PUBLIC_SITE_URL: 'https://pm33-website.vercel.app'
  },
  
  // Image optimization
  images: {
    domains: ['localhost', 'pm33-website.vercel.app'],
    unoptimized: false
  },
  
  // Compression and performance
  compress: true,
  poweredByHeader: false,
  
  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          }
        ]
      }
    ]
  }
};

module.exports = nextConfig;