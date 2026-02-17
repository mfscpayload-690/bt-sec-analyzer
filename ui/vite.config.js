import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
    svelte(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8745',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8745',
        ws: true,
      },
    },
  },
})
