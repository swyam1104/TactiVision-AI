/** @type {import('next').NextConfig} */
const rawBackendUrl = process.env.BACKEND_URL ||
  (process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8000' : 'https://tactivision-ai-1.onrender.com');
const backendUrl = rawBackendUrl.replace(/\/$/, '');

const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
}

module.exports = nextConfig
