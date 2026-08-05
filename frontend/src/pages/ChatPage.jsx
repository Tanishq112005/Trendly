import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import ChatBubble from '../components/chat/ChatBubble';
import ChatInput from '../components/chat/ChatInput';
import { useChatStore } from '../store/chatStore';
import styles from './ChatPage.module.css';
import { Sparkles, Trash2 } from 'lucide-react';

const ChatPage = () => {
  const { sessionId, messages, addMessage, clearMessages } = useChatStore();
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (text) => {
    // 1. Add user message to UI
    addMessage({ text, isAi: false });
    setIsLoading(true);

    try {
      // 2. Call FastAPI backend
      const response = await axios.post('http://localhost:8000/api/chat/', {
        session_id: sessionId,
        message: text,
      });

      // 3. Add AI response to UI
      addMessage({ text: response.data.response, isAi: true });
    } catch (error) {
      console.error("Chat error:", error);
      addMessage({ 
        text: "Sorry, I am having trouble connecting to the server. Please try again.", 
        isAi: true 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <div className={styles.logo}>
          <Sparkles size={24} color="var(--accent-color)" />
          <span>Trendly AI</span>
        </div>
        <button onClick={clearMessages} className={styles.clearBtn} title="Clear Chat">
          <Trash2 size={18} />
        </button>
      </header>

      <main className={styles.chatArea}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <h2>How can I help you today?</h2>
            <p>Ask me about your orders, returns, or Trendly policies.</p>
          </div>
        ) : (
          <div className={styles.messagesList}>
            {messages.map((msg, index) => (
              <ChatBubble key={index} message={msg.text} isAi={msg.isAi} />
            ))}
            {isLoading && (
              <div className={styles.loadingBubble}>
                <Sparkles size={16} className={styles.spin} color="var(--accent-color)" />
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <footer className={styles.footer}>
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        <p className={styles.disclaimer}>Trendly AI can make mistakes. Check important info.</p>
      </footer>
    </div>
  );
};

export default ChatPage;
