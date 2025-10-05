import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    https: process.env.VITE_HTTPS === 'true' ? {
      key: fs.readFileSync(path.resolve(__dirname, '../certificates/key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, '../certificates/cert.pem')),
    } : false,
    host: true,
    port: 5173,
  },
})
