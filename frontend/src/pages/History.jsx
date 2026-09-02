import React from 'react';
import { History as HistoryIcon, Clock, Database, CheckCircle, FileText } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import PlaceholderCard from '../components/PlaceholderCard';

export const History = () => {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Reconciliation Run History"
        description="Historical audit log of all batch runs, match metrics, throughput, and exception reports."
        badge={<StatusBadge label="Phase 1: Foundation" variant="indigo" size="md" />}
      />

      {/* Audit Log Table Placeholder */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Batch Execution Logs
          </div>
          <span className="text-xs text-slate-400">
            0 Completed Batches
          </span>
        </div>

        <div className="p-12 text-center">
          <HistoryIcon className="w-10 h-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-white">No Reconciliation Runs Yet</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Once reconciliation batches are executed in Phase 2, detailed performance metrics and logs will be indexed here.
          </p>
        </div>
      </div>

      <PlaceholderCard
        title="Audit Trail & Batch Archive"
        description="Every reconciliation batch run records end-to-end metrics: match rate, verified accuracy, throughput (records/sec), and links to unresolved exception records for forensic auditing."
        phase="Phase 1: Foundation"
        icon={HistoryIcon}
        nextSteps={[
          'Complete historical record of batch reconciliation runs',
          'Exportable audit reports (PDF / Excel / CSV)',
          'Performance metric trend tracking across batches',
          'Immutable compliance audit logging',
        ]}
      />
    </div>
  );
};

export default History;
