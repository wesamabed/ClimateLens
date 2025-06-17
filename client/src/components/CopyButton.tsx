import React, { useState } from "react";
import { IconButton, Tooltip } from "@mui/material";
import { ContentCopy, Check } from "@mui/icons-material";
import { motion } from "framer-motion";
import { copyToClipboard } from "../utils/export";
import styles from "./CopyButton.module.css";

interface CopyButtonProps {
  text: string;
  size?: "small" | "medium";
  className?: string;
}

const CopyButton: React.FC<CopyButtonProps> = ({
  text,
  size = "small",
  className,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Tooltip title={copied ? "Copied!" : "Copy to clipboard"}>
      <motion.div
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        className={className}
      >
        <IconButton
          onClick={handleCopy}
          size={size}
          className={styles.copyButton}
          aria-label="Copy message to clipboard"
        >
          <motion.div
            initial={false}
            animate={{ rotate: copied ? 360 : 0 }}
            transition={{ duration: 0.3 }}
          >
            {copied ? (
              <Check className={styles.successIcon} />
            ) : (
              <ContentCopy />
            )}
          </motion.div>
        </IconButton>
      </motion.div>
    </Tooltip>
  );
};

export default CopyButton;
