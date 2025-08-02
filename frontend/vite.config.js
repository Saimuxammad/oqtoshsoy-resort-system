import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'https://oqtoshsoy-resort-system-production.up.railway.app',
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  },
  preview: {
    port: process.env.PORT || 3000,
    host: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild',
    target: 'es2015'
  },
  define: {
    'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'https://oqtoshsoy-resort-system-production.up.railway.app')
  }
})