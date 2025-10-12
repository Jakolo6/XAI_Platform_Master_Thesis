/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Removed 'standalone' output for Netlify compatibility
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL 
          ? `${process.env.NEXT_PUBLIC_API_URL.replace('/api/v1', '')}/:path*`
          : 'http://localhost:8000/api/v1/:path*',
      },
    ]
  },
}

module.exports = nextConfig
