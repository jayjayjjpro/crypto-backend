import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],  // Enable React plugin
  server: {
    port: 5173,  // Dev server port
    proxy: {
      "/api": {
        target: "http://app:8000",  // Proxy API calls to backend container
        changeOrigin: true,  // Modify origin header to match target
        rewrite: (path) => path.replace(/^\/api/, ""),  // Remove '/api' prefix
      },
    },
  },
});
