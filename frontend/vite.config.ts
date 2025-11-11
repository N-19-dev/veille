import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// IMPORTANT: base = '/veille/' (le nom EXACT du repo)
export default defineConfig({
  plugins: [react()],
  base: '/veille/',
})