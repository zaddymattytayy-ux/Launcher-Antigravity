import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',  // Use relative paths for production build (required for QWebEngineView local file loading)
  server: {
    port: 5175,
  },
})
