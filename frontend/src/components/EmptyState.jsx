import React from 'react';
import { Database, Play, Loader2 } from 'lucide-react';

export const EmptyState = ({ onRunReconciliation, isRunning }) => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center flex flex-col items-center justify-center">
    <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mb-4 text-indigo-400">
      <Database className="w-7 h-7" />
    </div>
    <h3 className="text-base font-bold text-white mb-1">No reconciliation results available.</h3>
    <p className="text-xs text-slate-400 max-w-md mb-6 leading-relaxed">
      Execute a batch 3-way reconciliation run across synthetic invoices, bank statement transactions, and payment gateway settlements to generate live match metrics.
    </p>
    {onRunReconciliation && (
      <button
        onClick={onRunReconciliation}
        disabled={isRunning}
        className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition-all"
      >
        {isRunning ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Running reconciliation...</span>
          </>
        ) : (
          <>
            <Play className="w-4 h-4 fill-current" />
            <span>Run Reconciliation</span>
          </>
        )}
      </button>
    )}
  </div>
);

export default EmptyState;
