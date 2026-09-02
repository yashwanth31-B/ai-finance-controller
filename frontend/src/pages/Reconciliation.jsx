import React from 'react';
import { GitCompare, Play, SlidersHorizontal, CheckSquare, Sparkles, AlertCircle } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import PlaceholderCard from '../components/PlaceholderCard';

export const Reconciliation = () => {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Multi-Source Reconciliation"
        description="Automated 3-way matching between Invoice systems, Bank transactions, and Payment gateways."
        badge={<StatusBadge label="Phase 1: Foundation" variant="indigo" size="md" />}
        actions={
          <button
            disabled
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-400 text-xs font-semibold cursor-not-allowed border border-slate-700/60"
            title="Reconciliation logic will be enabled in Phase 2"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Execute Reconciliation (Phase 2)</span>
          </button>
        }
      />

      {/* 3-Way Match Architecture Preview */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-6">
          3-Way Reconciliation Pipeline
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-indigo-400 uppercase">Source A</span>
              <StatusBadge label="Ledger Feed" variant="neutral" size="sm" />
            </div>
            <h3 className="text-sm font-semibold text-white">Invoice Systems</h3>
            <p className="text-xs text-slate-400 mt-1">
              ERP Accounts Receivable, Billing systems & issued invoice records.
            </p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-emerald-400 uppercase">Source B</span>
              <StatusBadge label="Settlement Feed" variant="neutral" size="sm" />
            </div>
            <h3 className="text-sm font-semibold text-white">Bank Transactions</h3>
            <p className="text-xs text-slate-400 mt-1">
              Direct bank feeds, credit confirmations & account statements.
            </p>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-blue-400 uppercase">Source C</span>
              <StatusBadge label="Gateway Feed" variant="neutral" size="sm" />
            </div>
            <h3 className="text-sm font-semibold text-white">Payment Gateways</h3>
            <p className="text-xs text-slate-400 mt-1">
              Payment processor settlement reports, fees, and chargeback logs.
            </p>
          </div>
        </div>
      </div>

      {/* Placeholder Details */}
      <PlaceholderCard
        title="Reconciliation Matching Engine"
        description="This module will execute deterministic and fuzzy 3-way matching across 50+ batch records. It computes match rate, verified accuracy, throughput, and categorizes exceptions."
        phase="Phase 1: Foundation"
        icon={GitCompare}
        nextSteps={[
          'Exact match on Transaction ID, Invoice Number & Reference Tokens',
          'Tolerance matching for bank transaction processing fees and date windows',
          'Multi-way reconciliation matrix generation',
          'Detailed reconciliation reports with confidence scores',
        ]}
      />
    </div>
  );
};

export default Reconciliation;
