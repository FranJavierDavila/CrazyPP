import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  /* config options here */
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  async rewrites() {
    return {
      beforeFiles: [
        // Sirve el juego WebXR v2 (pala GLB real + saque con mano libre) en la raíz
        { source: "/", destination: "/game.html" },
      ],
      afterFiles: [],
      fallback: [],
    };
  },
};

export default nextConfig;
