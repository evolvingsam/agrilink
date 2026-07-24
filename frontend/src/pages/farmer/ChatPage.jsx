import { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { assistantApi } from '../../api';
import { formatDateTime, getErrorMessage } from '../../utils/helpers';
import './ChatPage.css';

export default function ChatPage() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('en');
  const [error, setError] = useState('');
  const bottomRef = useRef();

  // Scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const mutation = useMutation({
    mutationFn: (text) =>
      assistantApi.chat({ message: text, conversation_id: conversationId, language }),
    onSuccess: (res) => {
      const data = res.data;
      if (!conversationId) setConversationId(data.conversation_id);
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: data.reply, timestamp: new Date().toISOString() },
      ]);
      if (data.action_result) {
        setMessages((m) => [
          ...m,
          {
            role: 'system',
            content: `✅ Action: ${JSON.stringify(data.action_result)}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    },
    onError: (err) => setError(getErrorMessage(err)),
  });

  function handleSend() {
    const text = input.trim();
    if (!text) return;
    setError('');
    setMessages((m) => [...m, { role: 'farmer', content: text, timestamp: new Date().toISOString() }]);
    setInput('');
    mutation.mutate(text);
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleNewConversation() {
    setConversationId(null);
    setMessages([]);
    setError('');
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div>
          <h1 className="page-title">AI Farm Assistant</h1>
          <p className="page-subtitle">
            Ask anything — listing help, pricing advice, market info. Speaks Hausa, Yoruba, Igbo, Pidgin & English.
          </p>
        </div>
        <div className="chat-controls">
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="en">English</option>
            <option value="ha">Hausa</option>
            <option value="yo">Yoruba</option>
            <option value="ig">Igbo</option>
            <option value="pcm">Pidgin</option>
          </select>
          <button className="btn btn-secondary btn-sm" onClick={handleNewConversation}>
            + New Chat
          </button>
        </div>
      </div>

      <div className="chat-window">
        {messages.length === 0 && (
          <div className="chat-empty">
            <span style={{ fontSize: '2rem' }}>🤖</span>
            <p>Hello! I'm your AgriLink farm assistant. How can I help you today?</p>
            <p className="text-muted text-sm">You can say things like: "I want to sell 50kg of tomato" or "What is the price of cassava today?"</p>
          </div>
        )}

        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-message-row ${msg.role}`}>
              {msg.role === 'assistant' && <span className="chat-avatar">🤖</span>}
              <div className={`chat-bubble ${msg.role === 'farmer' ? 'chat-bubble-farmer' : msg.role === 'system' ? 'chat-bubble-system' : 'chat-bubble-assistant'}`}>
                {msg.content}
              </div>
              {msg.role === 'farmer' && <span className="chat-avatar">👤</span>}
            </div>
          ))}

          {mutation.isPending && (
            <div className="chat-message-row assistant">
              <span className="chat-avatar">🤖</span>
              <div className="chat-bubble chat-bubble-assistant chat-typing">
                <span className="dot" /><span className="dot" /><span className="dot" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ margin: 'var(--space-2) 0' }}>{error}</div>}

      <div className="chat-input-row">
        <textarea
          className="form-textarea chat-textarea"
          rows={2}
          placeholder="Type your message… (Enter to send)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="btn btn-primary"
          onClick={handleSend}
          disabled={mutation.isPending || !input.trim()}
        >
          Send →
        </button>
      </div>
    </div>
  );
}
