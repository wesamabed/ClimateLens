import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { easeOut, easeInOut } from "framer-motion";
import { IconButton, Alert, Collapse } from "@mui/material";
import { Close } from "@mui/icons-material";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import { Message } from "../App";
import styles from "./MessageList.module.css";

interface MessageListProps {
  messages: Message[];
  loading: boolean;
  error?: string | null;
  onClearError?: () => void;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  loading,
  error,
  onClearError,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: "smooth",
        block: "end",
      });
    }
  }, [messages, loading]);

  const welcomeVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: easeOut,
      },
    },
  };

  return (
    <div
      className={styles.container}
      ref={scrollRef}
      aria-live="polite"
      aria-label="Chat messages"
    >
      <Collapse in={!!error}>
        <Alert
          severity="error"
          className={styles.errorAlert}
          action={
            onClearError && (
              <IconButton
                aria-label="close error"
                color="inherit"
                size="small"
                onClick={onClearError}
              >
                <Close fontSize="inherit" />
              </IconButton>
            )
          }
        >
          {error}
        </Alert>
      </Collapse>

      <div className={styles.messagesList}>
        <AnimatePresence>
          {messages.length === 0 && !loading && (
            <motion.div
              className={styles.welcomeMessage}
              variants={welcomeVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
            >
              <motion.div
                className={styles.logoContainer}
                animate={{
                  rotate: [0, 5, -5, 0],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: easeInOut,
                }}
              >
                🌍
              </motion.div>
              <h2>Welcome to ClimateLens Chat</h2>
              <p>
                I'm your AI assistant for climate science and environmental
                data. Ask me about:
              </p>
              <ul className={styles.exampleList}>
                <li>Climate change trends and data</li>
                <li>Environmental research and studies</li>
                <li>Sustainability practices</li>
                <li>Weather patterns and forecasting</li>
                <li>Carbon emissions and mitigation</li>
              </ul>
              <p className={styles.mathNote}>
                💡 Ask me about weather, CO₂ emissions, climate trends, and more!
              </p>
            </motion.div>
          )}

          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <MessageBubble
                role={message.role}
                text={message.text}
                sources={message.sources}
                loading={message.loading}
                error={message.error}
              />
            </motion.div>
          ))}

          {loading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.2 }}
            >
              <TypingIndicator />
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;
