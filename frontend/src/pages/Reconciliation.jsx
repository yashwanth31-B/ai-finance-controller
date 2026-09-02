import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, Eye, ChevronLeft, ChevronRight, RefreshCw, GitCompare } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import { TableSkeleton } from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import ReconciliationDetailModal from '../components/ReconciliationDetailModal';
import { getReconciliationResults } from '../services/api';

export const Reconciliation = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [confidenceFilter, setConfidenceFilter] = useState('ALL');

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Modal State
  const [selectedItem, setSelectedItem] = useState(null);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getReconciliationResults();
      setResults(data || []);
    } catch (err) {
      console.error('Failed to fetch reconciliation results:', err);
      setError('Unable to connect to the reconciliation service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  // Filtered & Searched Data
  const filteredResults = useMemo(() => {
    return results.filter((item) => {
      // 1. Search Query Match
      const query = searchQuery.toLowerCase().trim();
      const matchSearch =
        !query ||
        item.invoice_id?.toLowerCase().includes(query) ||
        item.customer_name?.toLowerCase().includes(query) ||
        (item.selected_bank_transaction_id && item.selected_bank_transaction_id.toLowerCase().includes(query)) ||
        (item.selected_gateway_payment_id && item.selected_gateway_payment_id.toLowerCase().includes(query));

      // 2. Status Filter
      const matchStatus = statusFilter === 'ALL' || item.status === statusFilter;

      // 3. Confidence Filter
      let matchConfidence = true;
      const score = item.overall_confidence_score || 0;
      if (confidenceFilter === 'HIGH') {
        matchConfidence = score >= 90;
      } else if (confidenceFilter === 'MEDIUM') {
        matchConfidence = score >= 70 && score < 90;
      } else if (confidenceFilter === 'LOW') {
        matchConfidence = score < 70;
      }

      return matchSearch && matchStatus && matchConfidence;
    });
  }, [results, searchQuery, statusFilter, confidenceFilter]);

  // Pagination Logic
  const totalPages = Math.ceil(filteredResults.length / pageSize) || 1;
  const paginatedResults = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredResults.slice(start, start + pageSize);
  }, [filteredResults, currentPage, pageSize]);

  // Reset pagination on filter change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, statusFilter, confidenceFilter, pageSize]);

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Reconciliation Results"
          description="Interactive 3-way matching workbench across Invoice, Bank, and Gateway feeds."
        />
        <TableSkeleton rows={10} cols={8} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reconciliation Engine Workbench"
        description="Search, filter, and inspect multi-source candidate matches and confidence scores."
        actions={
          <button
            onClick={fetchResults}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Results</span>
          </button>
        }
      />

      {error && <ErrorBanner message={error} onRetry={fetchResults} />}

      {/* Search & Filter Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Invoice ID, Customer, Bank ID, Gateway ID..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Status Filter */}
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5 shrink-0" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="MATCHED">Matched Only</option>
              <option value="REVIEW">Needs Review</option>
              <option value="EXCEPTION">Exceptions Only</option>
            </select>
          </div>

          {/* Confidence Filter */}
          <select
            value={confidenceFilter}
            onChange={(e) => setConfidenceFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Confidence Levels</option>
            <option value="HIGH">High Confidence (&ge;90%)</option>
            <option value="MEDIUM">Medium Confidence (70-89%)</option>
            <option value="LOW">Low Confidence (&lt;70%)</option>
          </select>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-[11px] text-slate-400 border-b border-slate-800 bg-slate-950/60 uppercase tracking-wider">
                <th className="py-3 px-4">Invoice ID</th>
                <th className="py-3 px-4">Customer Name</th>
                <th className="py-3 px-4">Invoice Amount</th>
                <th className="py-3 px-4">Bank Match</th>
                <th className="py-3 px-4">Gateway Match</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Method</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {paginatedResults.length > 0 ? (
                paginatedResults.map((item) => (
                  <tr key={item.invoice_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-indigo-400">{item.invoice_id}</td>
                    <td className="py-3 px-4 font-medium text-slate-200">{item.customer_name}</td>
                    <td className="py-3 px-4 font-mono text-slate-200">₹{item.invoice_amount?.toLocaleString()}</td>
                    <td className="py-3 px-4 font-mono text-emerald-400">
                      {item.selected_bank_transaction_id || <span className="text-slate-400 font-sans text-[11px]">Unmatched</span>}
                    </td>
                    <td className="py-3 px-4 font-mono text-violet-400">
                      {item.selected_gateway_payment_id || <span className="text-slate-400 font-sans text-[11px]">Unmatched</span>}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-200">
                      {item.overall_confidence_score?.toFixed(1)}%
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[10px] font-mono">
                        {item.matching_method}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge
                        label={item.status}
                        variant={item.status === 'MATCHED' ? 'success' : item.status === 'REVIEW' ? 'warning' : 'danger'}
                        size="sm"
                      />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedItem(item)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 text-xs font-semibold transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View</span>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400 text-xs">
                    No matching reconciliation records found for your current search and filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div>
            Showing <span className="font-semibold text-slate-200">{filteredResults.length > 0 ? (currentPage - 1) * pageSize + 1 : 0}</span> to{' '}
            <span className="font-semibold text-slate-200">{Math.min(currentPage * pageSize, filteredResults.length)}</span> of{' '}
            <span className="font-semibold text-slate-200">{filteredResults.length}</span> items
          </div>

          <div className="flex items-center gap-4">
            {/* Page Size Selector */}
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

            {/* Page Nav Buttons */}
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

      {/* Detail Modal */}
      <ReconciliationDetailModal
        item={selectedItem}
        onClose={() => setSelectedItem(null)}
      />
    </div>
  );
};

export default Reconciliation;
