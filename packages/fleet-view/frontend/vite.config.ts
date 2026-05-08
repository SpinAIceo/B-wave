import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    // Split heavy 3rd-party libraries into their own chunks so users
    // re-download only changed code on subsequent visits, and so the main
    // app bundle stays small (= less Vercel CDN bandwidth per first load).
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'mapbox': ['mapbox-gl'],
          'd3': ['d3'],
        },
      },
    },
    chunkSizeWarningLimit: 700,
  },
});
