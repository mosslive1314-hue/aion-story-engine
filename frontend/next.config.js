/** @type {import('next').NextConfig} */
const nextConfig = {
  // React 严格模式
  reactStrictMode: true,

  // 压缩优化
  compress: true,

  // 图片优化
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    domains: [],
    unoptimized: false,
  },

  // 实验性功能
  experimental: {
    serverActions: true,
    // 优化包导入
    optimizePackageImports: ['lucide-react', '@tanstack/react-query'],
  },

  // 环境变量
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Webpack 配置
  webpack: (config, { dev, isServer }) => {
    // 生产环境优化
    if (!dev && !isServer) {
      // 代码分割
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // 公共代码
            commons: {
              name: 'commons',
              chunks: 'all',
              minChunks: 2,
            },
            // React 核心库
            react: {
              name: 'react',
              chunks: 'all',
              test: /react|react-dom/,
              priority: 20,
            },
            // UI 组件
            ui: {
              name: 'ui',
              chunks: 'all',
              test: /@\/components/,
              priority: 10,
            },
            // 工具库
            lib: {
              name: 'lib',
              chunks: 'all',
              test: /node_modules/,
              priority: 5,
            },
          },
        },
      }
    }

    return config
  },

  // 输出配置
  output: 'standalone',

  // 生产环境 source map（关闭以提升性能）
  productionBrowserSourceMaps: false,

  // 响应头优化
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          }
        ]
      }
    ]
  },
}

module.exports = nextConfig
