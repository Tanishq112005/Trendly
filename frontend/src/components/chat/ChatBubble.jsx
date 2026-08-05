import React from 'react';
import styles from './ChatBubble.module.css';
import { User, Sparkles } from 'lucide-react';

const ChatBubble = ({ message, isAi }) => {
  return (
    <div className={`${styles.bubbleContainer} ${isAi ? styles.aiContainer : styles.userContainer}`}>
      <div className={styles.avatar}>
        {isAi ? <Sparkles size={20} color="var(--accent-color)" /> : <User size={20} color="var(--text-secondary)" />}
      </div>
      <div className={`${styles.bubble} ${isAi ? styles.aiBubble : styles.userBubble}`}>
        {message}
      </div>
    </div>
  );
};

export default ChatBubble;
