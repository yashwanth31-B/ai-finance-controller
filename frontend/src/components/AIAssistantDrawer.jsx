import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Send,
  X,
  Sparkles,
  Loader2,
  Database,
  ArrowRight,
  HelpCircle,
  AlertCircle
} from 'lucide-react';
import { queryAssistant } from '../services/api';

const QUICK_QUESTIONS = [
  'Why is INV091 an exception?',
  'How many exceptions do we have?',
  'Show all duplicate payments.',
  'What is the current match rate?',
  'Which records have the lowest confidence?',
  'Show unresolved amount mismatches.'
];

export const AIAssistantDrawer = () => {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am your AI Finance Assistant. Ask me anything about the current reconciliation batch, exceptions, match rates, or specific invoices.',
      sources: ['reconciliation_database']
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (open) {
      scrollToBottom();
    }
  }, [messages, open]);

  const handleSend = async (questionText) => {
    const q = (questionText || input).trim();
    if (!q) return;

    const userMsg = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: q
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!questionText) setInput('');
    setLoading(true);

    try {
      const res = await queryAssistant(q);
      const assistantMsg = {
        id: `asst-${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        relatedInvoices: res.related_invoice_ids || [],
        sources: res.data_sources_used || []
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: 'I cannot determine that from the current reconciliation data.',
        sources: []
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleInvoiceClick = (invoiceId) => {
    setOpen(false);
    navigate('/exceptions');
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-40 inline-flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-bold shadow-2xl shadow-indigo-600/40 border border-indigo-400/30 transition-all transform hover:scale-105"
      >
        <Bot className="w-5 h-5 animate-pulse text-indigo-200" />
        <span>Ask Finance AI</span>
      </button>

      {/* Drawer Overlay */}
      {open && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/60 backdrop-blur-xs">
          <div className="w-full max-w-lg bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
            {/* Header */}
            <div className="p-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    AI Finance Assistant
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Grounded strictly on live batch reconciliation data
                  </p>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Chips Banner */}
            <div className="px-4 py-2.5 bg-slate-950/40 border-b border-slate-800/80 overflow-x-auto whitespace-nowrap space-x-2 scrollbar-none">
              <span className="text-[10px] uppercase font-bold text-slate-400 mr-1">Suggested:</span>
              {QUICK_QUESTIONS.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(chip)}
                  disabled={loading}
                  className="inline-block px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium border border-slate-700 transition-colors disabled:opacity-50"
                >
                  {chip}
                </button>
              ))}
            </div>

            {/* Messages Log */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20'
                        : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none shadow-md'
                    }`}
                  >
                    <p>{msg.text}</p>

                    {/* Invoice Links */}
                    {msg.relatedInvoices && msg.relatedInvoices.length > 0 && (
                      <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] text-slate-400 font-semibold">Related Invoices:</span>
                        {msg.relatedInvoices.map((inv) => (
                          <button
                            key={inv}
                            onClick={() => handleInvoiceClick(inv)}
                            className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800 flex items-center gap-1 transition-colors"
                          >
                            <span>{inv}</span>
                            <ArrowRight className="w-2.5 h-2.5" />
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Data Source Badge */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-2 text-[9px] font-mono text-slate-400 flex items-center gap-1">
                        <Database className="w-3 h-3" />
                        <span>Data source: {msg.sources.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex items-center gap-2 text-xs text-indigo-400 font-mono italic p-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Querying reconciliation engine data...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Footer */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="p-3 border-t border-slate-800 bg-slate-950 flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about match rate, INV091, duplicate payments..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all shadow-md shadow-indigo-600/20"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AIAssistantDrawer;
