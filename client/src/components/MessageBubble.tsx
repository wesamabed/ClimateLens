import React from "react";
import { motion } from "framer-motion";
import "katex/dist/katex.min.css";
import { InlineMath, BlockMath } from "react-katex";
import CopyButton from "./CopyButton";
import SourceReferences from "./SourceReferences";
import { Source } from "../api/client";
import styles from "./MessageBubble.module.css";

interface MessageBubbleProps {
  role: "user" | "assistant";
  text: string;
  sources?: Source[];
  loading?: boolean;
  error?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  text,
  sources,
  loading,
  error,
}) => {
  const renderTextWithMath = (content: string) => {
    if (!content) return "";

    // Split by LaTeX blocks (display math)
    const blockParts = content.split(/(\$\$[^$]+\$\$)/);

    return blockParts.map((part, blockIndex) => {
      if (part.startsWith("$$") && part.endsWith("$$")) {
        const mathContent = part.slice(2, -2);
        try {
          return (
            <div key={blockIndex} className={styles.mathBlock}>
              <BlockMath math={mathContent} />
            </div>
          );
        } catch {
          return (
            <span key={blockIndex} className={styles.mathError}>
              [Math Error: {mathContent}]
            </span>
          );
        }
      }

      // Split by inline math
      const inlineParts = part.split(/(\$[^$]+\$)/);

      return inlineParts.map((inlinePart, inlineIndex) => {
        if (inlinePart.startsWith("$") && inlinePart.endsWith("$")) {
          const mathContent = inlinePart.slice(1, -1);
          try {
            return (
              <InlineMath
                key={`${blockIndex}-${inlineIndex}`}
                math={mathContent}
              />
            );
          } catch {
            return (
              <span
                key={`${blockIndex}-${inlineIndex}`}
                className={styles.mathError}
              >
                [Math Error: {mathContent}]
              </span>
            );
          }
        }
        return inlinePart;
      });
    });
  };

  return (
    <motion.div
      className={`${styles.container} ${styles[role]} ${error ? styles.error : ""}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className={`${styles.bubble} ${styles[`${role}Bubble`]}`}>
        <div className={styles.content}>
          <div className={styles.textContainer}>
            <p className={styles.text}>
              {text ? renderTextWithMath(text) : ""}
            </p>
            {role === "assistant" && text && !loading && (
              <div className={styles.actions}>
                <CopyButton text={text} className={styles.copyButton} />
              </div>
            )}
          </div>
        </div>

        {role === "assistant" && sources && sources.length > 0 && (
          <SourceReferences sources={sources} />
        )}
      </div>
    </motion.div>
  );
};

export default MessageBubble;
