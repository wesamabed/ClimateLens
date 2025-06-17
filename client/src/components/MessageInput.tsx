import React, { useState, useRef, useEffect } from "react";
import { IconButton, Tooltip } from "@mui/material";
import { Send, Stop } from "@mui/icons-material";
import { motion } from "framer-motion";
import styles from "./MessageInput.module.css";

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmedInput = input.trim();
    if (trimmedInput && !disabled) {
      onSend(trimmedInput);
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  // Focus on mount for better UX
  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const hasInput = input.trim().length > 0;

  return (
    <motion.div
      className={styles.container}
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className={styles.inputWrapper} data-focused={isFocused}>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Ask about weather, historical CO₂ emissions, or IPCC report insights… (e.g. “What were CO₂ emissions in 2019 for Germany?”)"
          className={styles.textarea}
          disabled={disabled}
          rows={1}
          aria-label="Message input"
          maxLength={4000}
        />

        <div className={styles.inputActions}>
          {input.length > 0 && (
            <motion.div
              className={styles.charCount}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2 }}
            >
              {input.length}/4000
            </motion.div>
          )}

          <Tooltip
            title={
              disabled
                ? "Processing message..."
                : hasInput
                  ? "Send message (Enter)"
                  : "Type a message to send"
            }
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <IconButton
                onClick={handleSend}
                disabled={disabled || !hasInput}
                className={`${styles.sendButton} ${hasInput ? styles.hasInput : ""}`}
                aria-label={disabled ? "Processing" : "Send message"}
              >
                <motion.div
                  animate={{ rotate: disabled ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {disabled ? <Stop /> : <Send />}
                </motion.div>
              </IconButton>
            </motion.div>
          </Tooltip>
        </div>
      </div>

      <div className={styles.hints}>
        <span className={styles.hint}>
          Press Enter to send, Shift+Enter for new line
        </span>
        <span className={styles.hint}>•</span>
        <span className={styles.hint}>Weather, emissions & climate reports</span>
      </div>
    </motion.div>
  );
};

export default MessageInput;
