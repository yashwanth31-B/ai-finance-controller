import React from 'react';
import { useOutletContext, Link } from 'react-router-dom';
import {
  Percent,
  CheckCircle2,
  Zap,
  AlertTriangle,
  Layers,
  ArrowUpRight,
  Database,
  FileSpreadsheet,
  Landmark,
  CreditCard,
  ShieldCheck,
  Server
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import PlaceholderCard from '../components/PlaceholderCard';
import { DATA_SOURCES } from '../utils/constants';

const SOURCE_ICONS = {
  invoices: FileSpreadsheet,
  bank: Landmark,
  gateways: CreditCard,
};

export const Dashboard = () => {
  const { apiStatus, appInfo } = useOutletContext();

  return (
    <div className="space-y-8">
      {/* Page Title & Status Header */}
      <PageHeader
        title="Finance Controller Overview"
        description="Multi-source automated reconciliation platform across Invoices, Bank Feeds, and Payment Gateways."
        badge={
          <StatusBadge
            label="Phase 1: Foundation"
            variant="indigo"
            size="md"
          />
        }
        actions={
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-colors"
          >
            <span>Batch Ingestion</span>
            <ArrowUpRight className="w-4 h-4" />
          </Link>
        }
      />

      {/* Target Metric KPI Grid (Placeholders for 50+ batch processing) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Reconciliation Metrics (Batch Processing)
          </h2>
          <span className="text-[11px] text-slate-400">
            Target Batch Size: 50+ records
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Match Rate"
            value="-- %"
            subtitle="Automated 3-way match confidence ratio"
            icon={Percent}
            badge="Target >= 95%"
            accentColor="indigo"
          />
          <StatCard
            title="Verified Accuracy"
            value="-- %"
            subtitle="Rule-validated transaction accuracy"
            icon={CheckCircle2}
            badge="Zero tolerance"
            accentColor="emerald"
          />
          <StatCard
            title="Throughput"
            value="-- rec/s"
            subtitle="Batch reconciliation processing speed"
            icon={Zap}
            badge="Real-time / Batch"
            accentColor="blue"
          />
          <StatCard
            title="Unresolved Exceptions"
            value="0"
            subtitle="Discrepancies flagged for manual review"
            icon={AlertTriangle}
            badge="Pending runs"
            accentColor="amber"
          />
        </div>
      </div>

      {/* Three Financial Data Sources Status */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Reconciliation Data Sources
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {DATA_SOURCES.map((source) => {
            const Icon = SOURCE_ICONS[source.id] || Database;
            return (
              <div
                key={source.id}
                className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2.5 rounded-lg bg-slate-800/80 text-indigo-400 border border-slate-700/60">
                    <Icon className="w-5 h-5" />
                  </div>
                  <StatusBadge label={source.badge} variant="neutral" size="sm" />
                </div>
                <h3 className="text-sm font-semibold text-white">{source.name}</h3>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  {source.description}
                </p>
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Schema Config</span>
                  <span className="text-slate-400 font-mono">Ready (Phase 1)</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Backend Integration & Phase Roadmap */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PlaceholderCard
            title="Automated Multi-Source Reconciliation Engine"
            description="Phase 1 establishes the clean full-stack architectural foundation. The platform is prepared to ingest 50+ records across Invoices, Bank Feeds, and Payment Gateways to execute automated reconciliation with exception routing."
            phase="Phase 1 Active"
            icon={Layers}
            nextSteps={[
              'Multi-source transaction schema ingestion for Invoices, Bank Feeds, and Gateways',
              'Deterministic rule matching & tolerance-based reconciliation',
              'AI-assisted fuzzy matching for transaction discrepancy resolution',
              'Real-time metrics computation: match rate, verified accuracy, throughput, exceptions',
            ]}
          />
        </div>

        {/* Backend Connectivity Card */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Backend Services
              </span>
              <StatusBadge
                label={apiStatus === 'healthy' ? 'Online' : 'Offline'}
                variant={apiStatus === 'healthy' ? 'success' : 'danger'}
                size="sm"
                dot={true}
              />
            </div>
            <div className="space-y-3">
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/80">
                <div className="text-xs text-slate-400">API Application</div>
                <div className="text-sm font-semibold text-white font-mono mt-0.5">
                  {appInfo?.name || 'AI Finance Controller'}
                </div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/80">
                <div className="text-xs text-slate-400">Health Endpoint</div>
                <div className="text-xs font-mono text-indigo-300 mt-0.5">
                  GET /api/health
                </div>
              </div>
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/80">
                <div className="text-xs text-slate-400">Database Engine</div>
                <div className="text-xs font-mono text-slate-300 mt-0.5">
                  SQLite (SQLAlchemy 2.0 ORM)
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span>FastAPI v1.0.0</span>
            <span className="font-mono text-emerald-400">CORS Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
