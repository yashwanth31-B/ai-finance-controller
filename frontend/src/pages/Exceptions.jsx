import React from 'react';
import { AlertTriangle, Filter, CheckCircle, Clock, ShieldAlert } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import PlaceholderCard from '../components/PlaceholderCard';

export const Exceptions = () => {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Unresolved Exceptions"
        description="Audit, analyze, and resolve multi-source discrepancies and unreconciled records."
        badge={<StatusBadge label="Phase 1: Foundation" variant="indigo" size="md" />}
      />

      {/* Exception Categories Placeholder Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase mb-1">Amount Mismatches</div>
          <div className="text-2xl font-bold font-mono text-white">0</div>
          <p className="text-xs text-slate-400 mt-2">Variance in fee deductions or tax</p>
        </div>
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase mb-1">Timing Differences</div>
          <div className="text-2xl font-bold font-mono text-white">0</div>
          <p className="text-xs text-slate-400 mt-2">Cut-off date settlements in transit</p>
        </div>
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase mb-1">Missing Counterpart</div>
          <div className="text-2xl font-bold font-mono text-white">0</div>
          <p className="text-xs text-slate-400 mt-2">Unmatched single-sided records</p>
        </div>
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5">
          <div className="text-xs font-semibold text-slate-400 uppercase mb-1">Manual Action Required</div>
          <div className="text-2xl font-bold font-mono text-white">0</div>
          <p className="text-xs text-slate-400 mt-2">Exceptions awaiting controller review</p>
        </div>
      </div>

      <PlaceholderCard
        title="Exception Resolution Workbench"
        description="This module tracks and classifies all unreconciled transactions discovered during batch reconciliation runs. Controllers can review discrepancy reasons, inspect source payloads, and apply manual or AI-assisted resolutions."
        phase="Phase 1: Foundation"
        icon={AlertTriangle}
        nextSteps={[
          'Detailed exception classification and root cause analysis',
          'Side-by-side transaction discrepancy comparison viewer',
          'Resolution workflow (Approve adjustment, Flag fraudulent record, Re-queue batch)',
          'Automated audit logging of all manual interventions',
        ]}
      />
    </div>
  );
};

export default Exceptions;
