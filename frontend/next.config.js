/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['recharts', 'victory-vendor'],
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      'd3-shape': require.resolve('d3-shape'),
      'd3-scale': require.resolve('d3-scale'),
      'd3-array': require.resolve('d3-array'),
    };
    return config;
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig

