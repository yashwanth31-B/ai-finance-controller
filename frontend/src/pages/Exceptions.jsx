import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, Eye, ChevronLeft, ChevronRight, RefreshCw, AlertTriangle, ShieldAlert } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import { TableSkeleton } from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import ExceptionDetailModal from '../components/ExceptionDetailModal';
import { getExceptions } from '../services/api';
import { SEVERITY_COLORS } from '../utils/constants';

export const Exceptions = () => {
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Modal State
  const [selectedException, setSelectedException] = useState(null);

  const fetchExceptionsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getExceptions();
      setExceptions(data || []);
    } catch (err) {
      console.error('Failed to fetch exceptions:', err);
      setError('Unable to connect to the reconciliation service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExceptionsData();
  }, []);

  // Filtered Exception List
  const filteredExceptions = useMemo(() => {
    return exceptions.filter((exc) => {
      // 1. Search Query
      const q = searchQuery.toLowerCase().trim();
      const matchQuery =
        !q ||
        exc.exception_id?.toLowerCase().includes(q) ||
        exc.invoice_id?.toLowerCase().includes(q) ||
        exc.reason?.toLowerCase().includes(q) ||
        exc.suggested_action?.toLowerCase().includes(q);

      // 2. Type Filter
      const matchType = typeFilter === 'ALL' || exc.exception_type === typeFilter;

      // 3. Severity Filter
      const matchSeverity = severityFilter === 'ALL' || exc.severity === severityFilter;

      // 4. Status Filter
      const matchStatus = statusFilter === 'ALL' || exc.status === statusFilter;

      return matchQuery && matchType && matchSeverity && matchStatus;
    });
  }, [exceptions, searchQuery, typeFilter, severityFilter, statusFilter]);

  // Pagination Logic
  const totalPages = Math.ceil(filteredExceptions.length / pageSize) || 1;
  const paginatedExceptions = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredExceptions.slice(start, start + pageSize);
  }, [filteredExceptions, currentPage, pageSize]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, typeFilter, severityFilter, statusFilter, pageSize]);

  // Unique Exception Types for dropdown filter
  const exceptionTypes = useMemo(() => {
    const types = new Set(exceptions.map((e) => e.exception_type).filter(Boolean));
    return Array.from(types).sort();
  }, [exceptions]);

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Discrepancy Exception Workbench"
          description="Auditing, root-cause analysis, and remediation for unresolved reconciliation exceptions."
        />
        <TableSkeleton rows={10} cols={8} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Exception Monitoring Workbench"
        description="Classified reconciliation discrepancies with severity matrices and recommended actions."
        actions={
          <button
            onClick={fetchExceptionsData}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Exceptions</span>
          </button>
        }
      />

      {error && <ErrorBanner message={error} onRetry={fetchExceptionsData} />}

      {/* Search & Filter Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Exception ID, Invoice ID, Reason, Action..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-rose-500 transition-colors"
          />
        </div>

        {/* Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Exception Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Exception Types</option>
            {exceptionTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">CRITICAL Only</option>
            <option value="HIGH">HIGH Only</option>
            <option value="MEDIUM">MEDIUM Only</option>
            <option value="LOW">LOW Only</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">OPEN Only</option>
            <option value="UNDER_REVIEW">UNDER_REVIEW Only</option>
            <option value="RESOLVED">RESOLVED Only</option>
          </select>
        </div>
      </div>

      {/* Exception Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-[11px] text-slate-400 border-b border-slate-800 bg-slate-950/60 uppercase tracking-wider">
                <th className="py-3 px-4">Exception ID</th>
                <th className="py-3 px-4">Invoice ID</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Reason</th>
                <th className="py-3 px-4">Suggested Action</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {paginatedExceptions.length > 0 ? (
                paginatedExceptions.map((exc) => {
                  const sevStyle = SEVERITY_COLORS[exc.severity] || SEVERITY_COLORS.MEDIUM;
                  return (
                    <tr key={exc.exception_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-rose-400">{exc.exception_id}</td>
                      <td className="py-3 px-4 font-mono text-indigo-400 font-medium">{exc.invoice_id}</td>
                      <td className="py-3 px-4 font-semibold text-slate-200">{exc.exception_type}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${sevStyle.bg} ${sevStyle.border} ${sevStyle.text}`}>
                          {exc.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-bold text-slate-200">{exc.confidence_score?.toFixed(1)}%</td>
                      <td className="py-3 px-4 text-slate-300 max-w-xs truncate">{exc.reason}</td>
                      <td className="py-3 px-4 text-slate-400 max-w-xs truncate">{exc.suggested_action}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setSelectedException(exc)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600/10 hover:bg-rose-600/20 text-rose-400 border border-rose-500/30 text-xs font-semibold transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400 text-xs">
                    No discrepancy exceptions match your filter and search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div>
            Showing <span className="font-semibold text-slate-200">{filteredExceptions.length > 0 ? (currentPage - 1) * pageSize + 1 : 0}</span> to{' '}
            <span className="font-semibold text-slate-200">{Math.min(currentPage * pageSize, filteredExceptions.length)}</span> of{' '}
            <span className="font-semibold text-slate-200">{filteredExceptions.length}</span> exceptions
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span>Per page:</span>
              <select
                value={pageSize}
                onChange={(e) => setPageSize(Number(e.target.value))}
                className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-200 focus:outline-none"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                disabled={currentPage === 1}
                className="p-1.5 rounded bg-slate-800 border border-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="px-3 font-mono text-slate-200">
                {currentPage} / {totalPages}
              </span>

              <button
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="p-1.5 rounded bg-slate-800 border border-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700 transition-colors"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Exception Detail Modal */}
      <ExceptionDetailModal
        exception={selectedException}
        onClose={() => setSelectedException(null)}
      />
    </div>
  );
};

export default Exceptions;
