import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import ChatLayout from "./components/ChatLayout";
import { useChat } from "./hooks/useChat";
import { applyTheme, getStoredTheme, storeTheme, Theme } from "./utils/theme";
import { Source } from "./api/client";

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: number;
  sources?: Source[];
  loading?: boolean;
  error?: boolean;
}

const App = () => {
  const [theme, setTheme] = useState<Theme>(() => getStoredTheme());
  const { messages, loading, error, sendUserMessage, clearError, clearChat } =
    useChat();

  // Apply theme on mount and theme changes
  useEffect(() => {
    applyTheme(theme);
    storeTheme(theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <motion.div
      className="app"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      data-theme={theme}
    >
      <ChatLayout
        messages={messages}
        loading={loading}
        error={error}
        onSendMessage={sendUserMessage}
        theme={theme}
        onToggleTheme={toggleTheme}
        onClearError={clearError}
        onClearChat={clearChat}
      />
    </motion.div>
  );
};

export default App;
