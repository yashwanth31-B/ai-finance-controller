import React from 'react';
import { X, AlertTriangle, Lightbulb, ShieldAlert, DollarSign, Calendar } from 'lucide-react';
import { SEVERITY_COLORS } from '../utils/constants';

export const ExceptionDetailModal = ({ exception, onClose }) => {
  if (!exception) return null;

  const sevStyle = SEVERITY_COLORS[exception.severity] || SEVERITY_COLORS.MEDIUM;

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

          {/* Additional Financial Metrics (e.g. Gateway Fee breakdown) */}
          {(exception.gross_amount || exception.fee || exception.net_amount) && (
            <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800 space-y-2">
              <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider block">
                Financial Breakdown
              </span>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Gross Amount</span>
                  <span className="font-semibold text-slate-200">₹{exception.gross_amount?.toLocaleString()}</span>
                </div>
                <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Fee Deducted</span>
                  <span className="font-semibold text-amber-400">₹{exception.fee?.toLocaleString()}</span>
                </div>
                <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Net Amount</span>
                  <span className="font-semibold text-emerald-400">₹{exception.net_amount?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* Candidate IDs */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
              Evaluated Candidates
            </span>
            <div className="flex flex-wrap gap-2">
              {exception.candidate_bank_transaction_ids?.map((id) => (
                <span key={id} className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[11px]">
                  Bank: {id}
                </span>
              ))}
              {exception.candidate_gateway_payment_ids?.map((id) => (
                <span key={id} className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[11px]">
                  Gateway: {id}
                </span>
              ))}
            </div>
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
