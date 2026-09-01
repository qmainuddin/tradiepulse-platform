/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/chat/:path*",
        destination: process.env.AI_AGENT_URL || "http://localhost:8000/api/chat/:path*",
      },
      {
        source: "/auth/:path*",
        destination: process.env.AUTH_SERVICE_URL || "http://localhost:8081/auth/:path*",
      },
    ];
  },
};

export default nextConfig;
