import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Support both .jsx and .tsx files
  esbuild: {
    loader: 'tsx',
    include: /src\/.*\.[tj]sx?$/,
  },
})
