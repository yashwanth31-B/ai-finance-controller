import React from 'react';
import { useOutletContext } from 'react-router-dom';
import { Settings as SettingsIcon, Sliders, Database, Shield, Server } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import PlaceholderCard from '../components/PlaceholderCard';

export const Settings = () => {
  const { apiStatus } = useOutletContext();

  return (
    <div className="space-y-8">
      <PageHeader
        title="Platform Settings & Rules"
        description="Configure multi-source matching tolerances, reconciliation thresholds, and backend integrations."
        badge={<StatusBadge label="Phase 1: Foundation" variant="indigo" size="md" />}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matching Tolerances Placeholder */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sliders className="w-4 h-4 text-indigo-400" />
            <h3 className="text-sm font-semibold text-white">Reconciliation Tolerances</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Amount Difference Tolerance ($)
              </label>
              <input
                type="text"
                disabled
                defaultValue="0.00"
                className="w-full bg-slate-950/70 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-400 cursor-not-allowed"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">Configurable tolerance window for fee variances</span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Date Window Tolerance (Days)
              </label>
              <input
                type="text"
                disabled
                defaultValue="± 2 Days"
                className="w-full bg-slate-950/70 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-400 cursor-not-allowed"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">Maximum settlement delay between invoice and bank credit</span>
            </div>
          </div>
        </div>

        {/* Backend Endpoint Settings */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Server className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">Backend Connection</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                API Base URL
              </label>
              <input
                type="text"
                readOnly
                value={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
                className="w-full bg-slate-950/70 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-indigo-300"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Live Status
              </label>
              <div className="flex items-center justify-between p-2.5 bg-slate-950/70 border border-slate-800 rounded-lg text-xs">
                <span className="text-slate-300">FastAPI Health</span>
                <StatusBadge
                  label={apiStatus === 'healthy' ? 'Connected' : 'Offline'}
                  variant={apiStatus === 'healthy' ? 'success' : 'danger'}
                  size="sm"
                  dot={true}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <PlaceholderCard
        title="Rule Configuration & System Controls"
        description="Phase 2 will introduce dynamic rule configuration for custom matching algorithms, automated exception workflows, and ERP connector credentials."
        phase="Phase 1: Foundation"
        icon={SettingsIcon}
        nextSteps={[
          'Configurable deterministic and fuzzy rule builders',
          'Automated webhook triggers for batch reconciliation',
          'Export and backup settings',
        ]}
      />
    </div>
  );
};

export default Settings;
