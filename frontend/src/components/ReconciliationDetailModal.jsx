import React, { useState, useEffect } from 'react';
import {
  X,
  FileSpreadsheet,
  Landmark,
  CreditCard,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  UserCheck,
  Clock,
  Send,
  Loader2,
  HelpCircle,
  CheckCircle2,
  XCircle,
  RotateCcw
} from 'lucide-react';
import StatusBadge from './StatusBadge';
import { submitReviewAction, getInvoiceReviews } from '../services/api';

export const ReconciliationDetailModal = ({ item, onClose, onRefresh }) => {
  if (!item) return null;

  const isMatched = item.status === 'MATCHED';
  const isReview = item.status === 'REVIEW';

  // Review Form States
  const [reviewerName, setReviewerName] = useState('Finance Reviewer');
  const [reviewNote, setReviewNote] = useState('');
  const [selectedAction, setSelectedAction] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reviewError, setReviewError] = useState(null);
  const [reviewSuccess, setReviewSuccess] = useState(null);

  // Review History State
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Fetch Review History on Mount
  const fetchHistory = async () => {
    try {
      setLoadingHistory(true);
      const data = await getInvoiceReviews(item.invoice_id);
      setHistory(data || []);
    } catch (err) {
      console.error('Failed to fetch review history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [item.invoice_id]);

  // Initiate Action Confirmation
  const handleActionClick = (action) => {
    setReviewError(null);
    setReviewSuccess(null);
    setSelectedAction(action);
    setShowConfirmModal(true);
  };

  // Submit Review Action
  const handleConfirmSubmit = async () => {
    if (!selectedAction) return;

    try {
      setIsSubmitting(true);
      setReviewError(null);

      const payload = {
        invoice_id: item.invoice_id,
        action: selectedAction,
        reviewer_name: reviewerName || 'Finance Reviewer',
        note: reviewNote,
      };

      await submitReviewAction(payload);

      setReviewSuccess(`Successfully recorded action '${selectedAction}' for ${item.invoice_id}.`);
      setShowConfirmModal(false);
      setReviewNote('');
      setSelectedAction(null);

      // Refresh local review history & trigger parent refresh
      fetchHistory();
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Submit review error:', err);
      setReviewError(err?.response?.data?.detail || 'Failed to submit review decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getActionLabel = (act) => {
    switch (act) {
      case 'APPROVE_MATCH': return 'Approve Match';
      case 'REJECT_MATCH': return 'Reject Match';
      case 'MARK_RESOLVED': return 'Mark Resolved';
      case 'KEEP_UNDER_REVIEW': return 'Keep Under Review';
      default: return act;
    }
  };

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
                  label={item.final_status || item.status}
                  variant={isMatched ? 'success' : isReview ? 'warning' : 'danger'}
                  size="sm"
                />
              </div>
              <p className="text-xs text-slate-400">3-Way Multi-Source Match Breakdown & Human Audit</p>
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
          {/* Success Banner */}
          {reviewSuccess && (
            <div className="bg-emerald-950/40 border border-emerald-800/40 rounded-xl p-3.5 text-xs text-emerald-300 flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{reviewSuccess}</span>
            </div>
          )}

          {/* Error Banner */}
          {reviewError && (
            <div className="bg-rose-950/40 border border-rose-800/40 rounded-xl p-3.5 text-xs text-rose-300 flex items-center gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{reviewError}</span>
            </div>
          )}

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

          {/* HUMAN REVIEW WORKBENCH SECTION */}
          <div className="bg-slate-950/70 border border-indigo-900/40 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-indigo-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-white">Human Review Workbench</h4>
              </div>

              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Current Status:</span>
                <span className="font-semibold text-slate-200 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                  {item.human_review_status || 'NOT_REVIEWED'}
                </span>
              </div>
            </div>

            {/* Inputs & Action Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1">Reviewer Identity</label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  placeholder="e.g. Finance Reviewer"
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-400 mb-1">Review Note / Audit Comment</label>
                <textarea
                  value={reviewNote}
                  onChange={(e) => setReviewNote(e.target.value)}
                  placeholder="Enter audit rationale, bank reference checks, or notes..."
                  rows={2}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>
            </div>

            {/* Review Action Buttons */}
            <div className="flex flex-wrap gap-2.5 pt-2">
              <button
                onClick={() => handleActionClick('APPROVE_MATCH')}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-colors"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Approve Match</span>
              </button>

              <button
                onClick={() => handleActionClick('REJECT_MATCH')}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md transition-colors"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject Match</span>
              </button>

              <button
                onClick={() => handleActionClick('MARK_RESOLVED')}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Mark Resolved</span>
              </button>

              <button
                onClick={() => handleActionClick('KEEP_UNDER_REVIEW')}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Keep Under Review</span>
              </button>
            </div>
          </div>

          {/* REVIEW HISTORY TIMELINE */}
          <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-slate-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">Review History Timeline</h4>
              </div>
              <span className="text-[11px] text-slate-400">{history.length} Audit Entries</span>
            </div>

            {loadingHistory ? (
              <div className="py-4 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                <span>Loading history...</span>
              </div>
            ) : history.length > 0 ? (
              <div className="space-y-3 font-sans">
                {history.map((rev) => (
                  <div key={rev.review_id} className="bg-slate-900/70 border border-slate-800/80 rounded-lg p-3 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-200">{rev.reviewer_name}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          {getActionLabel(rev.review_action)}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(rev.created_at).toLocaleString()}
                      </span>
                    </div>

                    {rev.reviewer_note && (
                      <p className="text-slate-300 italic text-[11px] bg-slate-950/40 p-2 rounded border border-slate-800/60">
                        "{rev.reviewer_note}"
                      </p>
                    )}

                    <div className="text-[10px] text-slate-400 flex items-center gap-2">
                      <span>Status transition:</span>
                      <span className="font-mono text-slate-300">{rev.previous_final_status}</span>
                      <span>→</span>
                      <span className="font-mono text-emerald-400 font-bold">{rev.new_final_status}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-4 text-center text-xs text-slate-400">
                No human review actions recorded yet for this invoice.
              </div>
            )}
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

      {/* Action Confirmation Dialog Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-400">
              <AlertTriangle className="w-6 h-6 shrink-0" />
              <h4 className="text-base font-bold text-white">Confirm Review Action</h4>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Are you sure you want to execute <strong className="text-white">{getActionLabel(selectedAction)}</strong> for invoice{' '}
              <strong className="font-mono text-indigo-400">{item.invoice_id}</strong>?
            </p>

            {reviewNote && (
              <div className="text-xs bg-slate-950 p-3 rounded-lg border border-slate-800 text-slate-300 italic">
                "{reviewNote}"
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmSubmit}
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-indigo-600/20 transition-all"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Submitting...</span>
                  </>
                ) : (
                  <span>Confirm Action</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReconciliationDetailModal;
