import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    reactStrictMode: true,

    // API rewrites for backend
    async rewrites() {
        return [
            {
                source: "/api/v1/:path*",
                destination: `${process.env.NEXT_PUBLIC_API_URL || "https://edi-production.up.railway.app"}/api/v1/:path*`,
            },
        ];
    },

    // Security headers
    async headers() {
        return [
            {
                source: "/:path*",
                headers: [
                    {
                        key: "X-Content-Type-Options",
                        value: "nosniff",
                    },
                    {
                        key: "X-Frame-Options",
                        value: "DENY",
                    },
                    {
                        key: "X-XSS-Protection",
                        value: "1; mode=block",
                    },
                ],
            },
        ];
    },
};

export default nextConfig;
