import React, { useState } from 'react';
import styles from './ChatInput.module.css';
import { SendHorizonal } from 'lucide-react';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className={styles.inputContainer}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Trendly support..."
          className={styles.inputField}
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className={`${styles.sendButton} ${input.trim() ? styles.active : ''}`}
          disabled={isLoading || !input.trim()}
        >
          <SendHorizonal size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
