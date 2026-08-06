import React from 'react';
import styles from './ChatBubble.module.css';
import { User, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ChatBubble = ({ message, isAi }) => {
  // Safely ensure message is a string before passing to ReactMarkdown
  const safeMessage = typeof message === 'string' ? message : String(message || '');

  return (
    <div className={`${styles.bubbleContainer} ${isAi ? styles.aiContainer : styles.userContainer}`}>
      <div className={styles.avatar}>
        {isAi ? <Sparkles size={20} color="var(--accent-color)" /> : <User size={20} color="var(--text-secondary)" />}
      </div>
      <div className={`${styles.bubble} ${isAi ? styles.aiBubble : styles.userBubble}`}>
        {isAi ? (
          /* FIX 1: Wrap ReactMarkdown in a div instead of passing className directly */
          <div className={styles.markdownContent}>
            <ReactMarkdown>{safeMessage}</ReactMarkdown>
          </div>
        ) : (
           safeMessage
        )}
      </div>
    </div>
  );
};

export default ChatBubble;