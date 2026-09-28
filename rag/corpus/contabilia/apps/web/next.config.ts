import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  transpilePackages: ['@contabilia/shared-types'],
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts', '@radix-ui/react-*'],
  },
};

export default nextConfig;
