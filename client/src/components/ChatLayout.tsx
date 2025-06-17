import React from "react";
import { IconButton, Tooltip } from "@mui/material";
import { LightMode, DarkMode, Clear, Refresh } from "@mui/icons-material";
import { motion } from "framer-motion";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import ExportButton from "./ExportButton";
import { Message } from "../App";
import { Theme } from "../utils/theme";
import styles from "./ChatLayout.module.css";

interface ChatLayoutProps {
  messages: Message[];
  loading: boolean;
  error: string | null;
  onSendMessage: (text: string) => void;
  theme: Theme;
  onToggleTheme: () => void;
  onClearError: () => void;
  onClearChat: () => void;
}

const ChatLayout: React.FC<ChatLayoutProps> = ({
  messages,
  loading,
  error,
  onSendMessage,
  theme,
  onToggleTheme,
  onClearError,
  onClearChat,
}) => {
  return (
    <div className={styles.container}>
      <motion.header
        className={styles.header}
        initial={{ y: -60 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className={styles.headerLeft}>
          <motion.h1
            className={styles.title}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            ClimateLens Chat
          </motion.h1>
          {import.meta.env.VITE_DEV_MODE === "true" && (
            <span className={styles.devBadge}>DEV</span>
          )}
        </div>

        <div className={styles.headerActions}>
          <ExportButton messages={messages} />

          {messages.length > 0 && (
            <Tooltip title="Clear chat">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <IconButton
                  onClick={onClearChat}
                  className={styles.actionButton}
                  aria-label="Clear chat history"
                >
                  <Clear />
                </IconButton>
              </motion.div>
            </Tooltip>
          )}

          <Tooltip
            title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <IconButton
                onClick={onToggleTheme}
                className={styles.themeToggle}
                aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: theme === "dark" ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {theme === "light" ? <DarkMode /> : <LightMode />}
                </motion.div>
              </IconButton>
            </motion.div>
          </Tooltip>
        </div>
      </motion.header>

      <main className={styles.content} role="main">
        <MessageList
          messages={messages}
          loading={loading}
          error={error}
          onClearError={onClearError}
        />
        <MessageInput onSend={onSendMessage} disabled={loading} />
      </main>
    </div>
  );
};

export default ChatLayout;
