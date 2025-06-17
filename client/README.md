# ClimateLens Chat Client

A production-ready, chat interface for climate science and environmental data, built with React 19.1.0, TypeScript, and modern web technologies.

## 🌟 Features

### Core Features

- **ChatGPT-Style Interface**: Clean, modern chat UI with user and assistant message bubbles
- **Real-time API Integration**: Connects to RAG (Retrieval-Augmented Generation) backend
- **Dark/Light Theme**: Persistent theme switching with smooth transitions
- **Message Persistence**: Chat history saved in localStorage
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### Advanced Features

- **LaTeX Math Rendering**: Support for inline (`$E = mc^2$`) and block (`$$formula$$`) math equations using KaTeX
- **Source References**: Collapsible source citations with clickable links
- **Copy to Clipboard**: One-click copy functionality for assistant messages
- **Chat Export**: Export conversations as text or JSON with multiple options
- **Enhanced Animations**: Smooth transitions and micro-interactions using Framer Motion
- **Accessibility**: Full keyboard navigation, screen reader support, and ARIA attributes
- **Error Handling**: Graceful error states with retry functionality

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Local Development

1. **Clone and install dependencies:**

   ```bash
   npm install
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   ```

3. **Configure your environment** (`.env`):

   ```env
   # For local development with backend server running on port 3000
   VITE_API_BASE=

   # Enable development features
   VITE_DEV_MODE=true
   ```

4. **Start the development server:**

   ```bash
   npm run dev
   ```

5. **Visit the application:**
   - Open http://localhost:8080
   - The dev server includes a proxy that forwards `/api/*` requests to `http://localhost:3000`

### API Integration

The client expects your backend server to provide:

- **POST /api/ask**: Main chat endpoint

  ```typescript
  // Request
  { question: string }

  // Response
  { answer: string, sources: Array<{ id: string, text: string }> }
  ```

- **GET /api/health**: Health check endpoint (optional)

## ☁️ Cloud Run Deployment

### Environment Configuration

For Google Cloud Run deployment, set these environment variables:

```env
# Production API base URL
VITE_API_BASE=https://your-cloud-run-service-url

# Disable development features
VITE_DEV_MODE=false
```

### Build Process

1. **Build for production:**

   ```bash
   npm run build
   ```

2. **The `dist/` folder contains** optimized static files ready for deployment

### Cloud Run Deployment Options

#### Option 1: Static File Serving (Recommended)

Serve the built files using a lightweight web server:

```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
```

#### Option 2: Express Server Integration

Serve alongside your API server:

```javascript
// In your Express app
app.use(express.static("client/dist"));
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "client/dist/index.html"));
});
```

### CORS Configuration

Ensure your backend server has CORS properly configured:

```javascript
// Express.js example
app.use(
  cors({
    origin: process.env.CLIENT_URL || "http://localhost:8080",
    methods: ["GET", "POST"],
    allowedHeaders: ["Content-Type", "Authorization"],
  }),
);
```

## 🛠️ Scripts

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run typecheck` - Run TypeScript type checking
- `npm run test` - Run tests
- `npm run format.fix` - Format code with Prettier

## 🏗️ Architecture

### Project Structure

```
src/
├── components/           # UI components
│   ├── ChatLayout.tsx   # Main layout with header
│   ├── MessageList.tsx  # Message container with auto-scroll
│   ├── MessageBubble.tsx # Individual message display
│   ├── MessageInput.tsx # Message input with auto-resize
│   ├── TypingIndicator.tsx # Loading animation
│   ├── CopyButton.tsx   # Reusable copy functionality
│   ├── SourceReferences.tsx # Collapsible source display
│   └── ExportButton.tsx # Chat export menu
├── hooks/
│   └── useChat.ts       # Chat state management
├── utils/
│   ├── theme.ts         # Theme system and CSS variables
│   └── export.ts        # Chat export utilities
├── api/
│   └── client.ts        # API integration layer
└── App.tsx              # Root component
```

### Key Technologies

- **React 19.1.0**: Latest React with modern hooks
- **TypeScript**: Type safety and developer experience
- **Vite**: Fast build tool and dev server
- **Framer Motion**: Smooth animations and transitions
- **Material-UI**: Icons and some UI components
- **KaTeX**: LaTeX math rendering
- **CSS Modules**: Scoped styling system

### State Management

- **useChat Hook**: Centralized chat logic with localStorage persistence
- **Theme System**: CSS variables with TypeScript utilities
- **Error Handling**: Graceful error states with user-friendly messages

## 🎨 Customization

### Theme Customization

Modify theme colors in `src/utils/theme.ts`:

```typescript
export const lightTheme: ThemeColors = {
  primary: "#059669", // Change primary color
  // ... other theme properties
};
```

### Component Styling

Each component uses CSS Modules for isolated styling:

- Modify `.module.css` files for component-specific styles
- Update `src/index.css` for global styles and CSS variables

## 🔒 Security Considerations

- **Environment Variables**: Only `VITE_*` variables are exposed to the client
- **CORS**: Properly configure backend CORS for production domains
- **Content Security Policy**: Consider adding CSP headers for enhanced security
- **Input Validation**: Client validates message length (4000 char limit)

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Fails:**

   - Check `VITE_API_BASE` environment variable
   - Verify backend server is running and accessible
   - Check browser network tab for CORS errors

2. **Math Rendering Issues:**

   - Ensure KaTeX CSS is properly loaded
   - Check console for LaTeX syntax errors
   - Verify math expressions use correct delimiters (`$` or `$$`)

3. **Build Failures:**
   - Run `npm run typecheck` to identify TypeScript errors
   - Clear `node_modules` and reinstall dependencies
   - Check for missing environment variables

### Development Tips

- Use browser DevTools to inspect CSS variables and theme switching
- Monitor Network tab for API request/response debugging
- Use React DevTools for component state inspection
- Check browser console for any JavaScript errors

## 📄 License

This project is part of the ClimateLens hackathon submission. See project documentation for licensing details.

---

## 🤝 Contributing

This is a hackathon project, but improvements are welcome:

1. Follow the existing code style and TypeScript patterns
2. Ensure all features work across different screen sizes
3. Test theme switching and persistence
4. Verify accessibility with keyboard navigation
5. Test math rendering with various LaTeX expressions

For questions or issues, please refer to the project documentation or create an issue in the repository.
