import type { NextConfig } from "next";

// `output: "standalone"` was causing Vercel to package every page as a
// serverless function (billed per invocation). Vercel handles its own
// bundling/optimization; standalone is only for self-hosted Node servers.
// Removing it lets Vercel serve static pages directly from CDN.
const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
