import React, { useState } from 'react';
import { X, AlertTriangle, Lightbulb, ShieldAlert, Sparkles, Loader2, CheckCircle2, ShieldCheck } from 'lucide-react';
import { SEVERITY_COLORS } from '../utils/constants';
import { analyzeExceptionWithAI } from '../services/api';

export const ExceptionDetailModal = ({ exception, onClose }) => {
  if (!exception) return null;

  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiError, setAiError] = useState(null);

  const sevStyle = SEVERITY_COLORS[exception.severity] || SEVERITY_COLORS.MEDIUM;

  const handleRunAIAnalysis = async () => {
    try {
      setAnalyzing(true);
      setAiError(null);
      const data = await analyzeExceptionWithAI({
        exception_id: exception.exception_id,
        invoice_id: exception.invoice_id,
      });
      setAiAnalysis(data);
    } catch (err) {
      console.error('AI Analysis failed:', err);
      setAiError('Failed to trigger AI exception analysis.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 font-mono font-bold text-xs">
              {exception.exception_id}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">{exception.exception_type}</h3>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${sevStyle.bg} ${sevStyle.border} ${sevStyle.text}`}>
                  {exception.severity}
                </span>
              </div>
              <p className="text-xs text-slate-400">Invoice: <span className="font-mono text-slate-300">{exception.invoice_id}</span></p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1 text-xs">
          {/* AI Analysis Trigger Button */}
          <div className="flex items-center justify-between bg-gradient-to-r from-indigo-950/40 via-violet-950/40 to-slate-900 border border-indigo-500/30 rounded-xl p-4">
            <div>
              <h4 className="text-xs font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span>AI Exception Assistant</span>
              </h4>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Generate root-cause insights, confidence ratings, and recommended human review actions.
              </p>
            </div>

            <button
              onClick={handleRunAIAnalysis}
              disabled={analyzing}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-indigo-600/20 transition-all shrink-0"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Analyze with AI</span>
                </>
              )}
            </button>
          </div>

          {/* AI Error Alert */}
          {aiError && (
            <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{aiError}</span>
            </div>
          )}

          {/* AI Analysis Results Card */}
          {aiAnalysis && (
            <div className="bg-indigo-950/30 border border-indigo-500/40 rounded-xl p-4 space-y-3 animate-fade-in">
              <div className="flex items-center justify-between border-b border-indigo-900/50 pb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4" />
                  <span>AI Root-Cause Diagnosis ({aiAnalysis.ai_provider_used})</span>
                </span>
                <span className="text-[11px] font-bold text-emerald-400 bg-emerald-950/60 px-2.5 py-0.5 rounded border border-emerald-800">
                  Confidence: {aiAnalysis.confidence_score?.toFixed(1)}%
                </span>
              </div>

              <div className="space-y-2">
                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-semibold block">Root Cause Summary</span>
                  <p className="text-slate-200 leading-relaxed font-sans">{aiAnalysis.root_cause_summary}</p>
                </div>

                <div>
                  <span className="text-slate-400 text-[10px] uppercase font-semibold block">Financial Impact</span>
                  <p className="text-indigo-200 leading-relaxed font-sans">{aiAnalysis.financial_impact_explanation}</p>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <div>
                    <span className="text-slate-400 text-[10px] uppercase font-semibold block">Recommended Action</span>
                    <span className="font-bold text-amber-400 font-mono text-xs">{aiAnalysis.recommended_action}</span>
                  </div>

                  <div className="text-right">
                    <span className="text-slate-400 text-[10px] uppercase font-semibold block">Suggested Audit Note</span>
                    <span className="text-slate-300 font-mono text-[11px]">"{aiAnalysis.suggested_audit_note}"</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Reason Section */}
          <div className="bg-rose-950/20 border border-rose-800/40 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-rose-400 font-semibold uppercase tracking-wider text-[11px]">
              <ShieldAlert className="w-4 h-4" />
              <span>Root Cause Analysis</span>
            </div>
            <p className="text-slate-200 leading-relaxed font-sans">{exception.reason}</p>
          </div>

          {/* Suggested Action Section */}
          <div className="bg-indigo-950/30 border border-indigo-800/40 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold uppercase tracking-wider text-[11px]">
              <Lightbulb className="w-4 h-4" />
              <span>Suggested Remediation</span>
            </div>
            <p className="text-indigo-200 leading-relaxed font-sans">{exception.suggested_action}</p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 block text-[10px]">Confidence Score</span>
              <span className="font-bold text-white text-sm">{exception.confidence_score?.toFixed(1)}%</span>
            </div>

            <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 block text-[10px]">Status</span>
              <span className="font-bold text-amber-400 text-sm">{exception.status}</span>
            </div>

            {exception.amount_difference !== null && exception.amount_difference !== undefined && (
              <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Amount Discrepancy</span>
                <span className="font-bold text-rose-400 text-sm">₹{exception.amount_difference?.toLocaleString()}</span>
              </div>
            )}

            {exception.percentage_difference !== null && exception.percentage_difference !== undefined && (
              <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Percentage Discrepancy</span>
                <span className="font-bold text-rose-400 text-sm">{exception.percentage_difference?.toFixed(2)}%</span>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/50 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
          >
            Close Exception Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExceptionDetailModal;
