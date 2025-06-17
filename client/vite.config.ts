import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      // Proxy API calls to local server during development
      "/api": {
        target: "http://localhost:3000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [react()],
  define: {
    // Inject environment variables
    "import.meta.env.VITE_API_BASE": JSON.stringify(
      process.env.VITE_API_BASE || "",
    ),
    "import.meta.env.VITE_DEV_MODE": JSON.stringify(
      process.env.VITE_DEV_MODE || "false",
    ),
  },
  build: {
    // Optimize for Cloud Run deployment
    outDir: "dist",
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          mui: ["@mui/material", "@mui/icons-material"],
          katex: ["katex", "react-katex"],
        },
      },
    },
  },
});
