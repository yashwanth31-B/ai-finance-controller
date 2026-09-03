import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import {
  FileText,
  AlertTriangle,
  History,
  FileSpreadsheet,
  Download,
  Loader2,
  CheckCircle2,
  Zap,
  Target,
  ShieldAlert,
  RefreshCw,
  Play,
  Check,
  ArrowUpRight
} from 'lucide-react';
import {
  getMetrics,
  getExceptions,
  getAuditTrail,
  runReconciliation,
  downloadReconciliationCSV,
  downloadExceptionsCSV,
  downloadAuditCSV,
  downloadSummaryPDF
} from '../services/api';

export const Reports = () => {
  const [metrics, setMetrics] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);
  const [isReconciling, setIsReconciling] = useState(false);

  // Per-download loading states
  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [downloadingReconCSV, setDownloadingReconCSV] = useState(false);
  const [downloadingExceptionsCSV, setDownloadingExceptionsCSV] = useState(false);
  const [downloadingAuditCSV, setDownloadingAuditCSV] = useState(false);

  const fetchReportsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [metricsRes, exceptionsRes, auditRes] = await Promise.all([
        getMetrics().catch(() => null),
        getExceptions().catch(() => []),
        getAuditTrail().catch(() => [])
      ]);

      setMetrics(metricsRes);
      setExceptions(exceptionsRes || []);
      setAuditEvents(auditRes || []);
    } catch (err) {
      console.error('Failed to load reports data:', err);
      setError(err.response?.data?.detail || 'Failed to load report metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportsData();
  }, []);

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification(null);
    }, 4000);
  };

  const handleRunReconciliation = async () => {
    try {
      setIsReconciling(true);
      await runReconciliation();
      showNotification('Reconciliation batch executed successfully!', 'success');
      await fetchReportsData();
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to run reconciliation.', 'error');
    } finally {
      setIsReconciling(false);
    }
  };

  const handleDownload = async (downloadFn, setDownloading, reportName) => {
    try {
      setDownloading(true);
      await downloadFn();
      showNotification(`${reportName} downloaded successfully!`, 'success');
    } catch (err) {
      console.error(`Failed to download ${reportName}:`, err);
      const errorMsg =
        err.response?.data?.detail ||
        (err.response?.data instanceof Blob
          ? 'No report data available. Run reconciliation first.'
          : `Failed to generate ${reportName}.`);
      showNotification(errorMsg, 'error');
    } finally {
      setDownloading(false);
    }
  };

  const hasData = metrics && metrics.total_records > 0;

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Financial Audit Reports & Analytics"
          description="Exportable reconciliation summary reports, compliance audit trails, and PDF analytics."
        />
        <LoadingSkeleton type="cards" count={4} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Financial Audit Reports & Analytics"
          description="Exportable reconciliation summary reports, compliance audit trails, and PDF analytics."
        />

        {hasData && (
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => handleDownload(downloadSummaryPDF, setDownloadingPDF, 'Summary PDF Report')}
              disabled={downloadingPDF}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50"
            >
              {downloadingPDF ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
              <span>Download Summary PDF</span>
            </button>

            <button
              onClick={() => handleDownload(downloadReconciliationCSV, setDownloadingReconCSV, 'Reconciliation CSV')}
              disabled={downloadingReconCSV}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-emerald-600/90 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
            >
              {downloadingReconCSV ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileSpreadsheet className="w-3.5 h-3.5" />}
              <span>Export Reconciliation CSV</span>
            </button>
          </div>
        )}
      </div>

      {/* Toast Notification Banner */}
      {notification && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between shadow-lg transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/60 border-emerald-800/80 text-emerald-300'
              : 'bg-rose-950/60 border-rose-800/80 text-rose-300'
          }`}
        >
          <div className="flex items-center gap-3 text-xs font-medium">
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{notification.message}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-xs text-slate-400 hover:text-white underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {error && <ErrorBanner message={error} onRetry={fetchReportsData} />}

      {/* Empty State when no reconciliation has been run */}
      {!hasData ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center flex flex-col items-center justify-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <FileText className="w-7 h-7" />
          </div>
          <div className="max-w-md">
            <h3 className="text-base font-bold text-white mb-2">No report data available. Run reconciliation first.</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No active reconciliation batch results were found in system cache. Run multi-source reconciliation across synthetic datasets or uploaded files to generate live audit reports.
            </p>
          </div>
          <button
            onClick={handleRunReconciliation}
            disabled={isReconciling}
            className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50"
          >
            {isReconciling ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Executing Reconciliation Run...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Reconciliation</span>
              </>
            )}
          </button>
        </div>
      ) : (
        /* Report Cards Grid */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Card 1: Reconciliation Summary Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Reconciliation Summary Report</h3>
                    <p className="text-[11px] text-slate-400">
                      Overall batch KPIs, accuracy, match rate & performance.
                    </p>
                  </div>
                </div>
                <span className="text-[11px] px-2.5 py-1 rounded-md bg-indigo-950 border border-indigo-800/60 text-indigo-300 font-mono">
                  PDF & Data Summary
                </span>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-4">
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Total Records</div>
                  <div className="text-lg font-bold text-white mt-0.5">{metrics.total_records}</div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-emerald-400 tracking-wider">Matched</div>
                  <div className="text-lg font-bold text-emerald-400 mt-0.5">{metrics.automatically_matched}</div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-amber-400 tracking-wider">Review</div>
                  <div className="text-lg font-bold text-amber-400 mt-0.5">{metrics.needs_review}</div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-rose-400 tracking-wider">Exceptions</div>
                  <div className="text-lg font-bold text-rose-400 mt-0.5">{metrics.exceptions}</div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Match Rate</div>
                  <div className="text-sm font-bold text-indigo-300 mt-0.5">{metrics.match_rate}%</div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Accuracy</div>
                  <div className="text-sm font-bold text-emerald-300 mt-0.5">
                    {metrics.verified_accuracy !== null ? `${metrics.verified_accuracy}%` : 'Ground Truth N/A'}
                  </div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Throughput</div>
                  <div className="text-sm font-bold text-violet-300 mt-0.5">{metrics.throughput} r/s</div>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Avg Score</div>
                  <div className="text-sm font-bold text-slate-200 mt-0.5">{metrics.average_confidence}%</div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Includes PDF cover sheet, KPI grid & top exceptions.</span>
              <button
                onClick={() => handleDownload(downloadSummaryPDF, setDownloadingPDF, 'Summary PDF Report')}
                disabled={downloadingPDF}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-all disabled:opacity-50"
              >
                {downloadingPDF ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                <span>Download Summary PDF</span>
              </button>
            </div>
          </div>

          {/* Card 2: Exception Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Exception Report</h3>
                    <p className="text-[11px] text-slate-400">
                      Discrepancies, missing payments & severity breakdown.
                    </p>
                  </div>
                </div>
                <span className="text-[11px] px-2.5 py-1 rounded-md bg-amber-950 border border-amber-800/60 text-amber-300 font-mono">
                  {exceptions.length} Active Records
                </span>
              </div>

              {/* Exception Preview Table */}
              <div className="my-4 overflow-x-auto rounded-lg border border-slate-800 max-h-48 overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 sticky top-0">
                    <tr>
                      <th className="p-2.5 font-semibold">Invoice ID</th>
                      <th className="p-2.5 font-semibold">Exception Type</th>
                      <th className="p-2.5 font-semibold">Severity</th>
                      <th className="p-2.5 font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {exceptions.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="p-4 text-center text-slate-400 italic text-[11px]">
                          No exceptions recorded in active run.
                        </td>
                      </tr>
                    ) : (
                      exceptions.slice(0, 5).map((e, idx) => (
                        <tr key={e.exception_id || idx} className="hover:bg-slate-800/40">
                          <td className="p-2.5 font-mono text-[11px] text-white">{e.invoice_id}</td>
                          <td className="p-2.5 text-[11px]">{e.exception_type?.replace(/_/g, ' ')}</td>
                          <td className="p-2.5">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                e.severity === 'CRITICAL' || e.severity === 'HIGH'
                                  ? 'bg-rose-950 text-rose-400 border border-rose-800/50'
                                  : 'bg-amber-950 text-amber-400 border border-amber-800/50'
                              }`}
                            >
                              {e.severity}
                            </span>
                          </td>
                          <td className="p-2.5">
                            <StatusBadge status={e.status || 'OPEN'} />
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Includes suggested actions & confidence.</span>
              <button
                onClick={() => handleDownload(downloadExceptionsCSV, setDownloadingExceptionsCSV, 'Exceptions CSV')}
                disabled={downloadingExceptionsCSV}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md shadow-amber-600/20 transition-all disabled:opacity-50"
              >
                {downloadingExceptionsCSV ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                <span>Export Exceptions CSV</span>
              </button>
            </div>
          </div>

          {/* Card 3: Audit Trail Report */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                    <History className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Audit Trail Report</h3>
                    <p className="text-[11px] text-slate-400">
                      Immutable log of human reviews, status overrides & notes.
                    </p>
                  </div>
                </div>
                <span className="text-[11px] px-2.5 py-1 rounded-md bg-purple-950 border border-purple-800/60 text-purple-300 font-mono">
                  {auditEvents.length} Event Logs
                </span>
              </div>

              {/* Audit Preview Table */}
              <div className="my-4 overflow-x-auto rounded-lg border border-slate-800 max-h-48 overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 sticky top-0">
                    <tr>
                      <th className="p-2.5 font-semibold">Timestamp</th>
                      <th className="p-2.5 font-semibold">Invoice ID</th>
                      <th className="p-2.5 font-semibold">Actor</th>
                      <th className="p-2.5 font-semibold">Event Type</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {auditEvents.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="p-4 text-center text-slate-400 italic text-[11px]">
                          No manual review audit events recorded yet.
                        </td>
                      </tr>
                    ) : (
                      auditEvents.slice(0, 5).map((a, idx) => (
                        <tr key={a.audit_id || idx} className="hover:bg-slate-800/40">
                          <td className="p-2.5 text-[10px] text-slate-400 font-mono">
                            {a.created_at ? a.created_at.slice(0, 19).replace('T', ' ') : 'N/A'}
                          </td>
                          <td className="p-2.5 font-mono text-[11px] text-white">{a.invoice_id}</td>
                          <td className="p-2.5 text-[11px]">{a.actor}</td>
                          <td className="p-2.5 text-[11px] text-purple-300 font-medium">{a.event_type}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Full compliance history with actor & timestamps.</span>
              <button
                onClick={() => handleDownload(downloadAuditCSV, setDownloadingAuditCSV, 'Audit CSV')}
                disabled={downloadingAuditCSV}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-md shadow-purple-600/20 transition-all disabled:opacity-50"
              >
                {downloadingAuditCSV ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                <span>Export Audit CSV</span>
              </button>
            </div>
          </div>

          {/* Card 4: Full Reconciliation CSV Export */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-xl">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <FileSpreadsheet className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Full Reconciliation CSV Export</h3>
                    <p className="text-[11px] text-slate-400">
                      Complete invoice, bank & gateway matching dataset dump.
                    </p>
                  </div>
                </div>
                <span className="text-[11px] px-2.5 py-1 rounded-md bg-emerald-950 border border-emerald-800/60 text-emerald-300 font-mono">
                  Full Raw Data
                </span>
              </div>

              {/* Schema Pills */}
              <div className="my-4 p-3 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
                <div className="text-[11px] font-semibold text-slate-300">Export Schema Fields:</div>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    'invoice_id',
                    'customer_name',
                    'invoice_amount',
                    'bank_transaction_id',
                    'gateway_payment_id',
                    'confidence_score',
                    'status',
                    'exception_type',
                    'severity',
                    'final_status'
                  ].map((field) => (
                    <span
                      key={field}
                      className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-900 border border-slate-700/80 text-emerald-300"
                    >
                      {field}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">Export complete dataset for Excel or ERP import.</span>
              <button
                onClick={() => handleDownload(downloadReconciliationCSV, setDownloadingReconCSV, 'Reconciliation CSV')}
                disabled={downloadingReconCSV}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
              >
                {downloadingReconCSV ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                <span>Export Reconciliation CSV</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
