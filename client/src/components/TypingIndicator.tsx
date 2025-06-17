import React from "react";
import { motion, Easing } from "framer-motion";
import styles from "./TypingIndicator.module.css";

const TypingIndicator: React.FC = () => {
  const dotVariants = {
    start: { y: 0 },
    end: { y: -8 },
  };

  const dotTransition = {
    duration: 0.5,
    yoyo: Infinity,
    ease: "easeInOut" as Easing,
  };

  return (
    <motion.div
      className={styles.container}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.2 }}
    >
      <div className={styles.bubble}>
        <div className={styles.dots}>
          <motion.div
            className={styles.dot}
            variants={dotVariants}
            initial="start"
            animate="end"
            transition={{ ...dotTransition, delay: 0 }}
          />
          <motion.div
            className={styles.dot}
            variants={dotVariants}
            initial="start"
            animate="end"
            transition={{ ...dotTransition, delay: 0.1 }}
          />
          <motion.div
            className={styles.dot}
            variants={dotVariants}
            initial="start"
            animate="end"
            transition={{ ...dotTransition, delay: 0.2 }}
          />
        </div>
        <span className={styles.text}>ClimateLens is thinking...</span>
      </div>
    </motion.div>
  );
};

export default TypingIndicator;
