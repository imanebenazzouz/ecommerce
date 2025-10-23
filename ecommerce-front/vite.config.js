import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true, // Échoue si le port est occupé au lieu de chercher un autre port
    host: true // Écoute sur toutes les interfaces
  }
})
