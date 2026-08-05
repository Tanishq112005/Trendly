import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import ChatBubble from '../components/chat/ChatBubble';
import ChatInput from '../components/chat/ChatInput';
import { useChatStore } from '../store/chatStore';
import styles from './ChatPage.module.css';
import { Sparkles, Trash2, Shield } from 'lucide-react';

const ChatPage = () => {
  const { sessionId, messages, addMessage, clearMessages } = useChatStore();
  const [isLoading, setIsLoading] = useState(false);
  const [hitlPending, setHitlPending] = useState(false);
  const [ticketDetails, setTicketDetails] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, hitlPending]);

  const handleSendMessage = async (text, hitlAction = null) => {
    if (!hitlAction) {
      addMessage({ text, isAi: false });
    }
    
    setIsLoading(true);

    try {
      const payload = {
        session_id: sessionId,
      };
      
      if (hitlAction) {
        payload.hitl_action = hitlAction;
        if (hitlAction === 'confirm') {
          payload.ticket_details = ticketDetails;
        }
        addMessage({ 
          text: `[User ${hitlAction === 'confirm' ? 'confirmed' : 'cancelled'} ticket creation]`, 
          isAi: false 
        });
        setHitlPending(false);
      } else {
        payload.message = text;
      }

      const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/chat/`, payload);

      if (response.data.hitl_pending) {
        setHitlPending(true);
        setTicketDetails(response.data.ticket_details);
      } else {
        setTicketDetails(null);
      }
      
      if (response.data.response) {
        addMessage({ text: response.data.response, isAi: true });
      }

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
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={() => window.location.href = '/admin'} className={styles.clearBtn} title="Admin Dashboard">
            <Shield size={18} />
          </button>
          <button onClick={clearMessages} className={styles.clearBtn} title="Clear Chat">
            <Trash2 size={18} />
          </button>
        </div>
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
            
            {hitlPending && (
              <div className={styles.hitlModal}>
                <div className={styles.hitlContent}>
                  <h3>Confirmation Required</h3>
                  <p>Are you sure you want to create a support ticket?</p>
                  {ticketDetails && (
                    <div className={styles.ticketSummary}>
                      <strong>Order ID:</strong> {ticketDetails.order_id}<br/>
                      <strong>Reason:</strong> {ticketDetails.reason}
                    </div>
                  )}
                  <div className={styles.hitlActions}>
                    <button onClick={() => handleSendMessage(null, 'confirm')} className={styles.confirmBtn}>Yes, Create Ticket</button>
                    <button onClick={() => handleSendMessage(null, 'cancel')} className={styles.cancelBtn}>No, Cancel</button>
                  </div>
                </div>
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
