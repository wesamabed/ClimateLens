import React, { useState } from "react";
import { IconButton, Collapse } from "@mui/material";
import { ExpandMore, ExpandLess, Link as LinkIcon } from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { Source } from "../api/client";
import styles from "./SourceReferences.module.css";

interface SourceReferencesProps {
  sources: Source[];
}

const SourceReferences: React.FC<SourceReferencesProps> = ({ sources }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  const isValidUrl = (string: string): boolean => {
    try {
      new URL(string);
      return true;
    } catch {
      return false;
    }
  };

  return (
    <div className={styles.container}>
      <motion.button
        className={styles.toggleButton}
        onClick={() => setExpanded(!expanded)}
        whileHover={{ backgroundColor: "var(--primary-color-alpha)" }}
        whileTap={{ scale: 0.98 }}
      >
        <span className={styles.toggleText}>References ({sources.length})</span>
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ExpandMore className={styles.toggleIcon} />
        </motion.div>
      </motion.button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className={styles.sourcesContainer}
          >
            <div className={styles.sourcesList}>
              {sources.map((source, index) => (
                <motion.div
                  key={`${source.id}-${index}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={styles.sourceItem}
                >
                  <div className={styles.sourceNumber}>{index + 1}</div>
                  <div className={styles.sourceContent}>
                    <p className={styles.sourceText}>{source.text}</p>
                    {isValidUrl(source.id) && (
                      <a
                        href={source.id}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.sourceLink}
                        aria-label={`Open source ${index + 1} in new tab`}
                      >
                        <LinkIcon className={styles.linkIcon} />
                        <span>View Source</span>
                      </a>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SourceReferences;
