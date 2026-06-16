import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy API calls to the FastAPI backend (default uvicorn port 8000) so the
// frontend can use relative URLs and avoid CORS in development. BACKEND_URL lets
// the Docker container point the proxy at the backend service (http://backend:8000).
const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/books": backendUrl,
    },
  },
});
