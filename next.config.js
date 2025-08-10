/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: {
      rules: {
        '*.css': {
          loaders: ['@tailwindcss/vite'],
          as: 'css',
        },
      },
    },
  },
};

module.exports = nextConfig;
