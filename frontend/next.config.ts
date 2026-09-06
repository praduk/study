import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export',
  deploymentId: 'study-frontend',
  generateBuildId: async () => 'study-frontend',
};

export default nextConfig;
