import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { aiAPI, quizAPI } from '../services/api';
import { 
  Bot, 
  Send, 
  Sparkles, 
  FileText, 
  User, 
  RotateCcw,
  CheckCircle2
} from 'lucide-react';

const AIAssistant = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Greetings! I am the **StatSaksham AI Learning Assistant**, designed specifically for officials in India's Official Statistical System (MoSPI).\n\nI can assist you with:\n- **Understanding your competency gaps** and required cadre levels\n- **Statistical concepts**: System of National Accounts (SNA 2008), Consumer Price Index (CPI), Stratified Sampling, PLFS\n- **Technical tools**: Python, R, and SQL scripts for survey microdata\n- **Explaining personalized recommendations** from iGOT Karmayogi & NSSTA\n\nHow may I help your professional capacity building today?`,
      sources: ['StatSaksham Core Competency Knowledge Base'],
      model: 'StatSaksham Intelligent Assistant'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);
  const [userDocs, setUserDocs] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!user) return;
    const fetchStatusAndDocs = async () => {
      try {
        const [healthRes, docsRes] = await Promise.all([
          aiAPI.getHealth(),
          quizAPI.getDocuments(user.employee_id)
        ]);
        setAiStatus(healthRes.data);
        setUserDocs(docsRes.data);
      } catch (err) {
        console.error('Error loading AI health:', err);
      }
    };
    fetchStatusAndDocs();
  }, [user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (customText = null) => {
    const text = customText || inputMessage;
    if (!text || !text.trim()) return;

    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    if (!customText) setInputMessage('');
    setLoading(true);

    try {
      const payload = {
        employee_id: user.employee_id,
        message: text,
        document_id: selectedDocId ? parseInt(selectedDocId) : null
      };

      const res = await aiAPI.chat(payload);
      if (res.data && res.data.message) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: res.data.message,
            sources: res.data.sources || [],
            model: res.data.model_used || 'StatSaksham Intelligence'
          }
        ]);
      } else {
        throw new Error('Empty response from AI assistant');
      }
    } catch (err) {
      console.error('AI Chat Error:', err);
      const errDetail = err.response?.data?.detail || 'AI service is currently busy or re-indexing. Please check whether Ollama is active or try again.';
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: errDetail,
          sources: []
        }
      ]);
    } finally {
      // Guarantee loading is always reset to false!
      setLoading(false);
    }
  };

  const samplePrompts = [
    "What are my biggest skill gaps?",
    "Explain Gross Value Added (GVA) in National Accounts.",
    "How do I use Python for survey microdata?",
    "Why was this iGOT course recommended for me?"
  ];

  return (
    <div className="space-y-4 pb-12 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">StatSaksham AI Assistant</h1>
          <p className="text-xs text-slate-500 mt-0.5">Your official MoSPI statistical learning and capacity building companion</p>
        </div>

        {aiStatus && (
          <div className="flex items-center space-x-2 text-[11px] bg-white px-3 py-1.5 rounded-xl border border-slate-200/90 shadow-2xs font-semibold">
            <span className={`h-2 w-2 rounded-full ${aiStatus.ollama_connected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <span className="text-slate-600">
              Engine: <strong>{aiStatus.ollama_connected ? `Ollama (${aiStatus.active_model})` : 'MoSPI Domain Engine'}</strong>
            </span>
          </div>
        )}
      </div>

      {/* RAG Document Context Selector */}
      {userDocs.length > 0 && (
        <div className="bg-white rounded-2xl p-3 border border-slate-200/90 shadow-2xs flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2 text-slate-700">
            <FileText className="h-4 w-4 text-blue-600" />
            <span className="font-bold">Ground AI with Uploaded Material:</span>
          </div>
          <select
            value={selectedDocId || ''}
            onChange={(e) => setSelectedDocId(e.target.value || null)}
            className="px-3 py-1.5 border border-slate-300 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-600 focus:outline-none bg-slate-50 max-w-xs truncate"
          >
            <option value="">General MoSPI Domain Knowledge Base</option>
            {userDocs.map((doc) => (
              <option key={doc.id} value={doc.id}>
                [{doc.file_type}] {doc.filename} ({doc.chunk_count} Chunks)
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Chat Container */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-2xs min-h-[460px] max-h-[580px] flex flex-col justify-between overflow-hidden">
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex items-start space-x-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.role === 'assistant' && (
                <div className="h-8 w-8 rounded-xl bg-[#0C1E38] text-white flex items-center justify-center shrink-0 shadow-2xs">
                  <Bot className="h-4 w-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                  m.role === 'user'
                    ? 'bg-blue-600 text-white font-medium rounded-tr-none'
                    : 'bg-slate-50 border border-slate-200/90 text-slate-800 rounded-tl-none'
                }`}
              >
                <div className="whitespace-pre-line leading-relaxed">
                  {m.content}
                </div>

                {m.sources && m.sources.length > 0 && (
                  <div className="pt-2 border-t border-slate-200/80 mt-2 flex flex-wrap items-center gap-1 text-[10px] text-slate-500 font-medium">
                    <span className="font-bold text-slate-700">Sources:</span>
                    {m.sources.map((src, sIdx) => (
                      <span key={sIdx} className="bg-white px-2 py-0.5 rounded border border-slate-200">
                        {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {m.role === 'user' && (
                <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-800 text-white flex items-center justify-center shrink-0 font-bold text-xs shadow-2xs">
                  {user?.name ? user.name.charAt(0) : 'U'}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center space-x-3 text-xs text-slate-500">
              <div className="h-8 w-8 rounded-xl bg-[#0C1E38] text-white flex items-center justify-center shrink-0 animate-pulse">
                <Bot className="h-4 w-4" />
              </div>
              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center space-x-2">
                <div className="animate-bounce">●</div>
                <div className="animate-bounce delay-100">●</div>
                <div className="animate-bounce delay-200">●</div>
                <span>Synthesizing response...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Queries Pills */}
        <div className="px-6 py-2.5 bg-slate-50/80 border-t border-slate-100 flex items-center space-x-2 overflow-x-auto text-xs">
          <span className="text-slate-400 font-bold uppercase text-[10px] shrink-0">Suggestions:</span>
          {samplePrompts.map((prompt, pIdx) => (
            <button
              key={pIdx}
              onClick={() => handleSend(prompt)}
              className="bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 px-3 py-1 rounded-full border border-slate-200 whitespace-nowrap transition shadow-2xs font-semibold text-[11px]"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Box */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask about skill gaps, SNA 2008, sampling, or recommendations..."
              className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-600 focus:outline-none focus:bg-white font-medium"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="bg-[#0C1E38] hover:bg-blue-900 disabled:opacity-40 text-white p-2.5 rounded-xl shadow transition"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
