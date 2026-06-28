/** @type {import('next').NextConfig} */
// Local dev convenience: proxy /api to the backend so you don't need CORS.
// In production set NEXT_PUBLIC_API_BASE to your Render URL and this is bypassed.
const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";
const nextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${BACKEND}/api/:path*` }];
  },
};
module.exports = nextConfig;
