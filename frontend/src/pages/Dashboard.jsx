import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  Loader2,
  Percent,
  CheckCircle2,
  Zap,
  AlertTriangle,
  Layers,
  ArrowUpRight,
  ShieldCheck,
  TrendingUp,
  Award,
  CheckCircle,
  Eye,
  RefreshCw
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import PageHeader from '../components/PageHeader';
import LoadingSkeleton, { CardSkeleton, TableSkeleton, ChartSkeleton } from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import EmptyState from '../components/EmptyState';
import ReconciliationDetailModal from '../components/ReconciliationDetailModal';
import ExceptionDetailModal from '../components/ExceptionDetailModal';
import { getMetrics, getReconciliationResults, getExceptions, runReconciliation } from '../services/api';
import { STATUS_COLORS, SEVERITY_COLORS } from '../utils/constants';

export const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [results, setResults] = useState([]);
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  
  const [selectedResult, setSelectedResult] = useState(null);
  const [selectedException, setSelectedException] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      const [mRes, rRes, eRes] = await Promise.all([
        getMetrics(),
        getReconciliationResults(),
        getExceptions()
      ]);
      setMetrics(mRes);
      setResults(rRes || []);
      setExceptions(eRes || []);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Unable to connect to the reconciliation service.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleRunReconciliation = async () => {
    try {
      setRunning(true);
      setSuccessMessage('');
      setError(null);
      await runReconciliation();
      setSuccessMessage('Reconciliation run executed successfully across synthetic datasets!');
      await fetchDashboardData();
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (err) {
      console.error('Reconciliation run failed:', err);
      setError('Reconciliation execution failed. Ensure the backend is reachable.');
    } finally {
      setRunning(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="animate-pulse space-y-2">
          <div className="h-7 bg-slate-800 rounded w-64"></div>
          <div className="h-4 bg-slate-800 rounded w-96"></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <CardSkeleton /><CardSkeleton /><CardSkeleton /><CardSkeleton />
        </div>
        <TableSkeleton rows={4} cols={6} />
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="space-y-6 py-6">
        <ErrorBanner message={error} onRetry={fetchDashboardData} />
      </div>
    );
  }

  const hasData = metrics && metrics.total_records > 0;

  if (!hasData) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="AI Finance Controller"
          description="Multi-source financial reconciliation with verification and exception handling"
        />
        <EmptyState onRunReconciliation={handleRunReconciliation} isRunning={running} />
      </div>
    );
  }

  // Prepare Recharts Data
  const statusPieData = [
    { name: 'MATCHED', value: metrics.automatically_matched, color: '#10b981' },
    { name: 'REVIEW', value: metrics.needs_review, color: '#f59e0b' },
    { name: 'EXCEPTION', value: metrics.exceptions, color: '#f43f5e' }
  ].filter(d => d.value > 0);

  const exceptionBarData = Object.entries(metrics.exception_breakdown || {})
    .map(([type, count]) => ({
      name: type.replace('_', ' '),
      count
    }))
    .filter(d => d.count > 0);

  return (
    <div className="space-y-8">
      {/* Top Heading & Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Finance Controller</h1>
          <p className="text-xs text-slate-400 mt-1">
            Multi-source financial reconciliation with verification and exception handling
          </p>
        </div>

        <button
          onClick={handleRunReconciliation}
          disabled={running}
          className="inline-flex items-center justify-center gap-2.5 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-indigo-600/20 transition-all shrink-0"
        >
          {running ? (
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
      </div>

      {/* Success / Notification Banner */}
      {successMessage && (
        <div className="bg-emerald-950/40 border border-emerald-800/40 rounded-xl p-4 text-xs text-emerald-300 flex items-center gap-3 animate-fade-in">
          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Error Banner */}
      {error && <ErrorBanner message={error} onRetry={fetchDashboardData} />}

      {/* 8 Live KPI Cards */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Executive KPI Metrics
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Records"
            value={metrics.total_records?.toLocaleString()}
            subtitle="Multi-source reconciled dataset"
            icon={Layers}
            accentColor="indigo"
          />
          <StatCard
            title="Automatically Matched"
            value={metrics.automatically_matched?.toLocaleString()}
            subtitle="Matched without manual intervention"
            icon={CheckCircle2}
            accentColor="emerald"
          />
          <StatCard
            title="Needs Review"
            value={metrics.needs_review?.toLocaleString()}
            subtitle="Fuzzy or moderate confidence matches"
            icon={TrendingUp}
            accentColor="amber"
          />
          <StatCard
            title="Exceptions"
            value={metrics.exceptions?.toLocaleString()}
            subtitle="Unresolved discrepancy records"
            icon={AlertTriangle}
            accentColor="rose"
          />

          <StatCard
            title="Match Rate"
            value={`${metrics.match_rate?.toFixed(2)}%`}
            subtitle="Automated resolution ratio"
            icon={Percent}
            accentColor="indigo"
          />
          <StatCard
            title="Verified Accuracy"
            value={
              metrics.ground_truth_available && metrics.verified_accuracy !== null
                ? `${metrics.verified_accuracy?.toFixed(2)}%`
                : 'N/A'
            }
            subtitle={
              metrics.ground_truth_available
                ? 'Ground truth verified accuracy'
                : 'Ground truth is not available for uploaded data.'
            }
            icon={Award}
            accentColor="emerald"
          />
          <StatCard
            title="Throughput"
            value={`${metrics.throughput?.toFixed(2)} records/sec`}
            subtitle="Engine processing velocity"
            icon={Zap}
            accentColor="violet"
          />
          <StatCard
            title="Average Confidence"
            value={`${metrics.average_confidence?.toFixed(2)}%`}
            subtitle="Mean batch confidence score"
            icon={ShieldCheck}
            accentColor="blue"
          />
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reconciliation Status Donut Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Reconciliation Status Distribution
            </h3>
            <span className="text-[11px] text-slate-400">
              {metrics.total_records} Total Items
            </span>
          </div>

          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {statusPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend
                  formatter={(value) => <span className="text-xs text-slate-300 font-medium">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Exception Breakdown Bar Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Discrepancy Exception Breakdown
            </h3>
            <span className="text-[11px] text-slate-400">
              {metrics.exceptions} Active Exceptions
            </span>
          </div>

          {exceptionBarData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={exceptionBarData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={10}
                    interval={0}
                    angle={-20}
                    textAnchor="end"
                  />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#f43f5e' }}
                  />
                  <Bar dataKey="count" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
              No active discrepancy exceptions detected.
            </div>
          )}
        </div>
      </div>

      {/* Scenario Performance Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Scenario Performance Evaluation
          </h3>
          <span className="text-[11px] text-slate-400">
            Verified against ground truth dataset
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-[11px] text-slate-400 border-b border-slate-800 uppercase tracking-wider">
                <th className="py-2.5 px-3">Scenario Name</th>
                <th className="py-2.5 px-3">Total Records</th>
                <th className="py-2.5 px-3">Correct Mappings</th>
                <th className="py-2.5 px-3">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
              {metrics.scenario_performance?.map((scen) => (
                <tr key={scen.scenario_name} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-3 font-sans font-medium text-slate-200">{scen.scenario_name}</td>
                  <td className="py-2.5 px-3">{scen.total_records}</td>
                  <td className="py-2.5 px-3 text-emerald-400">{scen.correct_results}</td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      scen.accuracy >= 95 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                      scen.accuracy >= 80 ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                      'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                    }`}>
                      {scen.accuracy.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Reconciliation Results Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden space-y-3">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Recent Reconciliation Results
            </h3>
            <p className="text-[11px] text-slate-400">Latest 5 invoice reconciliation items</p>
          </div>

          <a href="/reconciliation" className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
            <span>View All Reconciliation</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-[11px] text-slate-400 border-b border-slate-800 bg-slate-950/40 uppercase tracking-wider">
                <th className="py-3 px-4">Invoice ID</th>
                <th className="py-3 px-4">Customer</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Bank Match</th>
                <th className="py-3 px-4">Gateway Match</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {results.slice(0, 5).map((item) => (
                <tr key={item.invoice_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-mono font-semibold text-indigo-400">{item.invoice_id}</td>
                  <td className="py-3 px-4 text-slate-200 font-medium">{item.customer_name}</td>
                  <td className="py-3 px-4 font-mono text-slate-200">₹{item.invoice_amount?.toLocaleString()}</td>
                  <td className="py-3 px-4 font-mono text-emerald-400">{item.selected_bank_transaction_id || '—'}</td>
                  <td className="py-3 px-4 font-mono text-violet-400">{item.selected_gateway_payment_id || '—'}</td>
                  <td className="py-3 px-4 font-bold text-slate-200">{item.overall_confidence_score?.toFixed(1)}%</td>
                  <td className="py-3 px-4">
                    <StatusBadge
                      label={item.status}
                      variant={item.status === 'MATCHED' ? 'success' : item.status === 'REVIEW' ? 'warning' : 'danger'}
                      size="sm"
                    />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => setSelectedResult(item)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                      title="View 3-way breakdown"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Exceptions Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden space-y-3">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Active Discrepancy Exceptions
            </h3>
            <p className="text-[11px] text-slate-400">Latest 5 detected exceptions requiring review</p>
          </div>

          <a href="/exceptions" className="text-xs text-rose-400 hover:text-rose-300 font-semibold flex items-center gap-1">
            <span>View All Exceptions</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-[11px] text-slate-400 border-b border-slate-800 bg-slate-950/40 uppercase tracking-wider">
                <th className="py-3 px-4">Invoice ID</th>
                <th className="py-3 px-4">Exception Type</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Reason</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {exceptions.slice(0, 5).map((exc) => {
                const sevStyle = SEVERITY_COLORS[exc.severity] || SEVERITY_COLORS.MEDIUM;
                return (
                  <tr key={exc.exception_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-rose-400">{exc.invoice_id}</td>
                    <td className="py-3 px-4 text-slate-200 font-medium">{exc.exception_type}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${sevStyle.bg} ${sevStyle.border} ${sevStyle.text}`}>
                        {exc.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-200">{exc.confidence_score?.toFixed(1)}%</td>
                    <td className="py-3 px-4 text-slate-400 max-w-xs truncate">{exc.reason}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedException(exc)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                        title="View exception details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modals */}
      <ReconciliationDetailModal
        item={selectedResult}
        onClose={() => setSelectedResult(null)}
      />

      <ExceptionDetailModal
        exception={selectedException}
        onClose={() => setSelectedException(null)}
      />
    </div>
  );
};

export default Dashboard;
