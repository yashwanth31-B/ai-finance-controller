import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorBanner = ({ message = 'Unable to connect to the reconciliation service.', onRetry }) => (
  <div className="bg-rose-950/40 border border-rose-800/40 rounded-xl p-5 text-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-center shrink-0">
        <AlertCircle className="w-5 h-5 text-rose-400" />
      </div>
      <div>
        <h4 className="text-sm font-semibold text-rose-300">Connection Error</h4>
        <p className="text-xs text-rose-200/80 mt-0.5">{message}</p>
      </div>
    </div>
    {onRetry && (
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-rose-900/40 hover:bg-rose-900/60 border border-rose-700/50 text-rose-200 text-xs font-semibold transition-colors shrink-0"
      >
        <RefreshCw className="w-3.5 h-3.5" />
        <span>Retry Connection</span>
      </button>
    )}
  </div>
);

export default ErrorBanner;
