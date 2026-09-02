import React, { useState, useEffect } from 'react';
import { History as HistoryIcon, ShieldCheck, Search, Filter, RefreshCw, Loader2, User, Clock, FileText } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import ErrorBanner from '../components/ErrorBanner';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { getAuditTrail } from '../services/api';

export const History = () => {
  const [auditEvents, setAuditEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter States
  const [searchInvoiceId, setSearchInvoiceId] = useState('');
  const [filterActor, setFilterActor] = useState('ALL');
  const [filterEventType, setFilterEventType] = useState('ALL');

  const fetchAuditEvents = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {};
      if (searchInvoiceId.trim()) params.invoice_id = searchInvoiceId.trim();
      if (filterActor !== 'ALL') params.actor = filterActor;
      if (filterEventType !== 'ALL') params.event_type = filterEventType;

      const data = await getAuditTrail(params);
      setAuditEvents(data || []);
    } catch (err) {
      console.error('Fetch audit trail error:', err);
      setError('Unable to connect to the reconciliation audit service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditEvents();
  }, [searchInvoiceId, filterActor, filterEventType]);

  const getEventTypeBadgeVariant = (evtType) => {
    switch (evtType) {
      case 'REVIEW_APPROVED': return 'success';
      case 'REVIEW_REJECTED': return 'danger';
      case 'REVIEW_MARKED_RESOLVED': return 'indigo';
      case 'REVIEW_RETURNED_TO_REVIEW': return 'warning';
      default: return 'neutral';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <PageHeader
        title="Reconciliation Audit Trail & Compliance Log"
        description="Immutable compliance audit log recording every human review action, status transition, and audit note."
        badge={<StatusBadge label="Phase 10: Human Review & Audit" variant="indigo" size="md" />}
      />

      {/* Filter Toolbar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          {/* Invoice Search Input */}
          <div className="relative min-w-[220px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchInvoiceId}
              onChange={(e) => setSearchInvoiceId(e.target.value)}
              placeholder="Search Invoice ID..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Event Type Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterEventType}
              onChange={(e) => setFilterEventType(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Event Types</option>
              <option value="REVIEW_APPROVED">Review Approved</option>
              <option value="REVIEW_REJECTED">Review Rejected</option>
              <option value="REVIEW_MARKED_RESOLVED">Marked Resolved</option>
              <option value="REVIEW_RETURNED_TO_REVIEW">Returned to Review</option>
            </select>
          </div>
        </div>

        {/* Refresh Button */}
        <button
          onClick={fetchAuditEvents}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Log</span>
        </button>
      </div>

      {/* Error Alert */}
      {error && <ErrorBanner message={error} onRetry={fetchAuditEvents} />}

      {/* Audit Log Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <span>Immutable Audit Trail ({auditEvents.length} Events)</span>
          </div>
        </div>

        {loading ? (
          <div className="p-6">
            <LoadingSkeleton type="table" rows={6} />
          </div>
        ) : auditEvents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-[11px] text-slate-400 border-b border-slate-800 bg-slate-950/60 uppercase tracking-wider">
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Invoice ID</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Event Type</th>
                  <th className="py-3 px-4">State Transition</th>
                  <th className="py-3 px-4">Audit Note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {auditEvents.map((evt) => (
                  <tr key={evt.audit_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                      {new Date(evt.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-indigo-400 whitespace-nowrap">
                      {evt.invoice_id}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-200 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5 text-slate-400" />
                        <span>{evt.actor}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <StatusBadge
                        label={evt.event_type.replace('REVIEW_', '')}
                        variant={getEventTypeBadgeVariant(evt.event_type)}
                        size="sm"
                      />
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-mono text-[11px] whitespace-nowrap">
                      <span>{evt.previous_state}</span>
                      <span className="mx-1 text-slate-500">→</span>
                      <span className="font-bold text-emerald-400">{evt.new_state}</span>
                    </td>
                    <td className="py-3 px-4 text-slate-300 max-w-xs truncate">
                      {evt.note ? `"${evt.note}"` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center">
            <HistoryIcon className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-white">No Audit Events Found</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Submit human review decisions on the Reconciliation page to generate immutable audit log entries.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
