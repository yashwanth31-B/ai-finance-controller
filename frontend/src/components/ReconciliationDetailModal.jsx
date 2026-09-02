import React from 'react';
import { X, FileSpreadsheet, Landmark, CreditCard, ShieldCheck, CheckCircle, AlertTriangle, HelpCircle } from 'lucide-react';
import StatusBadge from './StatusBadge';

export const ReconciliationDetailModal = ({ item, onClose }) => {
  if (!item) return null;

  const isMatched = item.status === 'MATCHED';
  const isReview = item.status === 'REVIEW';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-mono font-bold text-sm">
              {item.invoice_id}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">{item.customer_name}</h3>
                <StatusBadge
                  label={item.status}
                  variant={isMatched ? 'success' : isReview ? 'warning' : 'danger'}
                  size="sm"
                />
              </div>
              <p className="text-xs text-slate-400">3-Way Multi-Source Match Breakdown</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* Match Explanation Banner */}
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                  Decision Summary ({item.matching_method})
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Confidence Score:</span>
                <span className="font-bold text-white text-sm">{item.overall_confidence_score?.toFixed(1)}%</span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              {item.explanation}
            </p>

            {/* Score Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
              <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase">Bank Score</span>
                <p className="text-xs font-bold text-emerald-400 mt-0.5">{item.bank_score?.toFixed(1)}%</p>
              </div>
              <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase">Gateway Score</span>
                <p className="text-xs font-bold text-violet-400 mt-0.5">{item.gateway_score?.toFixed(1)}%</p>
              </div>
              <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase">Customer Fuzzy</span>
                <p className="text-xs font-bold text-amber-400 mt-0.5">{item.fuzzy_customer_score?.toFixed(1)}%</p>
              </div>
              <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/60">
                <span className="text-[10px] text-slate-400 uppercase">Score Gap</span>
                <p className="text-xs font-bold text-indigo-400 mt-0.5">{item.candidate_score_gap?.toFixed(1)}</p>
              </div>
            </div>

            {/* Matched vs Mismatched Fields */}
            <div className="flex flex-wrap gap-4 text-xs pt-1">
              <div>
                <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                  Matched Fields
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {item.matched_fields?.length > 0 ? (
                    item.matched_fields.map((f) => (
                      <span key={f} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px]">
                        {f}
                      </span>
                    ))
                  ) : (
                    <span className="text-slate-400 text-[11px]">None</span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-semibold text-rose-400 uppercase tracking-wider block mb-1">
                  Mismatched Fields
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {item.mismatched_fields?.length > 0 ? (
                    item.mismatched_fields.map((f) => (
                      <span key={f} className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[11px]">
                        {f}
                      </span>
                    ))
                  ) : (
                    <span className="text-slate-400 text-[11px]">None</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* 3-Source Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Invoice Record */}
            <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-indigo-400 pb-2 border-b border-slate-800">
                <FileSpreadsheet className="w-4 h-4" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Invoice Record</h4>
              </div>
              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px]">Invoice ID</span>
                  <span className="font-mono text-slate-200">{item.invoice_id}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Customer Name</span>
                  <span className="font-medium text-slate-200">{item.customer_name}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Amount</span>
                  <span className="font-bold text-white text-sm">₹{item.invoice_amount?.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Invoice Date</span>
                  <span className="text-slate-300">{item.invoice_date}</span>
                </div>
              </div>
            </div>

            {/* Bank Record */}
            <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 pb-2 border-b border-slate-800">
                <Landmark className="w-4 h-4" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Bank Record</h4>
              </div>
              {item.selected_bank_transaction_id ? (
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Transaction ID</span>
                    <span className="font-mono text-emerald-400 font-semibold">{item.selected_bank_transaction_id}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Description</span>
                    <span className="text-slate-300 truncate block">{item.customer_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Amount</span>
                    <span className="font-bold text-emerald-400 text-sm">₹{item.invoice_amount?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Bank Match Score</span>
                    <span className="text-emerald-400 font-semibold">{item.bank_score?.toFixed(1)}%</span>
                  </div>
                </div>
              ) : (
                <div className="py-6 text-center text-slate-400 text-xs">
                  No bank transaction matched
                </div>
              )}
            </div>

            {/* Gateway Record */}
            <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-violet-400 pb-2 border-b border-slate-800">
                <CreditCard className="w-4 h-4" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Gateway Record</h4>
              </div>
              {item.selected_gateway_payment_id ? (
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Payment ID</span>
                    <span className="font-mono text-violet-400 font-semibold">{item.selected_gateway_payment_id}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Customer / Processor</span>
                    <span className="text-slate-300 truncate block">{item.customer_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Gross Amount</span>
                    <span className="font-bold text-violet-400 text-sm">₹{item.invoice_amount?.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Gateway Match Score</span>
                    <span className="text-violet-400 font-semibold">{item.gateway_score?.toFixed(1)}%</span>
                  </div>
                </div>
              ) : (
                <div className="py-6 text-center text-slate-400 text-xs">
                  No gateway settlement matched
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/50 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
          >
            Close Detail View
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReconciliationDetailModal;
