import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Loader2, MessageSquare } from 'lucide-react';
import client from '../api/client';
import TopHeader from '../components/TopHeader';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [availableModels, setAvailableModels] = useState<any[]>([]);
  const [activeModel, setActiveModel] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchModels = async () => {
    try {
      const res = await client.get('/api/settings/ai-models');
      setAvailableModels(res.data.available_models || []);
      setActiveModel(res.data.active_model || '');
    } catch (error) {
      console.error('Failed to fetch models', error);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // 履歴をAIに渡す（最大直近10件程度）
      const history = messages.slice(-10).map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        content: m.content
      }));

      const res = await client.post('/api/chat', {
        message: input,
        history: history,
        model: activeModel // モデルを指定
      });

      const assistantMessage: Message = { role: 'assistant', content: res.data.response };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'エラーが発生したよ。もう一度試してみてね！' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <TopHeader title="AI チャット相談" onRefresh={() => setMessages([])} />
      
      <div className="page-content flex flex-col" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
        <div className="flex justify-end mb-2">
          <div className="flex items-center gap-2 bg-card-bg p-2 rounded-lg border border-border">
            <Bot size={16} className="text-primary" />
            <select 
              className="form-control form-control-sm" 
              style={{ width: 'auto', background: 'transparent', border: 'none', padding: '0 4px', fontSize: '0.8rem' }}
              value={activeModel}
              onChange={(e) => setActiveModel(e.target.value)}
            >
              {availableModels.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="card flex-1 flex flex-col mb-4 overflow-hidden" style={{ display: 'flex', flexDirection: 'column', flex: 1, marginBottom: '1rem', overflow: 'hidden' }}>
          <div className="card-header">
            <h3><MessageSquare size={20} /> AIと家計の相談</h3>
          </div>
          <div className="card-body overflow-y-auto p-4 flex-1" style={{ overflowY: 'auto', padding: '1rem', flex: 1 }}>
            {messages.length === 0 && (
              <div className="text-center py-10 text-muted">
                <Bot size={48} className="mx-auto mb-4 opacity-20" />
                <p>家計について気になることを聞いてみてね！<br/>「今月使いすぎかな？」「どうやって節約すればいい？」などなど✨</p>
              </div>
            )}
            <div className="chat-messages flex flex-col gap-4" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {messages.map((msg, idx) => (
                <div key={idx} className={`chat-bubble-container ${msg.role === 'user' ? 'user-msg' : 'ai-msg'}`} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div className="flex gap-3 max-w-[80%]" style={{ display: 'flex', gap: '0.75rem', maxWidth: '80%', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                    <div className="avatar" style={{ flexShrink: 0 }}>
                      {msg.role === 'user' ? <User size={32} className="p-1 rounded-full bg-primary text-white" /> : <Bot size={32} className="p-1 rounded-full bg-success text-white" />}
                    </div>
                    <div className={`chat-bubble ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-card-bg'}`} style={{ 
                      padding: '0.75rem 1rem', 
                      borderRadius: '12px', 
                      fontSize: '0.95rem', 
                      lineHeight: '1.5',
                      background: msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                      color: msg.role === 'user' ? 'white' : 'var(--text-main)',
                      whiteSpace: 'pre-wrap',
                      border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none'
                    }}>
                      {msg.content}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="chat-bubble-container ai-msg" style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div className="flex gap-3" style={{ display: 'flex', gap: '0.75rem' }}>
                    <div className="avatar"><Bot size={32} className="p-1 rounded-full bg-success text-white" /></div>
                    <div className="chat-bubble" style={{ padding: '0.75rem 1rem', borderRadius: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)' }}>
                      <Loader2 size={20} className="animate-spin" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
          
          <div className="p-4 bg-black/20 border-t border-border" style={{ padding: '1rem', background: 'rgba(0,0,0,0.2)', borderTop: '1px solid var(--border)' }}>
            <div className="flex gap-2" style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="text" 
                className="form-control flex-1" 
                placeholder="AIに相談する..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                style={{ flex: 1 }}
              />
              <button className="btn-primary" onClick={handleSend} disabled={loading || !input.trim()}>
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .chat-bubble {
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

export default AIChat;
