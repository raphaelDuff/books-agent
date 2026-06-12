import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy API calls to the FastAPI backend (default uvicorn port 8000) so the
// frontend can use relative URLs and avoid CORS in development.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/books": "http://localhost:8000",
    },
  },
});
