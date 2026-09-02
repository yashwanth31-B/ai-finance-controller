import React from 'react';
import { useLocation } from 'react-router-dom';
import { RefreshCw, ShieldCheck, Menu } from 'lucide-react';
import { NAV_ITEMS } from '../utils/constants';
import StatusBadge from './StatusBadge';

export const Header = ({ apiStatus, lastChecked, onRefresh, onMobileToggle }) => {
  const location = useLocation();
  const currentNav = NAV_ITEMS.find((item) => item.path === location.pathname) || {
    label: 'Dashboard',
    description: 'Executive overview & reconciliation KPIs'
  };

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Route & Breadcrumb Information */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMobileToggle}
          className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/60"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="hidden sm:inline">Platform</span>
          <span className="hidden sm:inline">/</span>
          <span className="text-slate-200 font-medium">{currentNav.label}</span>
        </div>
      </div>

      {/* Right controls: API Health status & Refresh */}
      <div className="flex items-center gap-3">
        {/* Backend Connectivity Status Badge */}
        <div className="flex items-center gap-2">
          {apiStatus === 'healthy' ? (
            <StatusBadge
              label="API Connected"
              variant="success"
              size="sm"
              dot={true}
            />
          ) : apiStatus === 'checking' ? (
            <StatusBadge
              label="Checking..."
              variant="warning"
              size="sm"
              dot={true}
            />
          ) : (
            <StatusBadge
              label="API Offline"
              variant="danger"
              size="sm"
              dot={true}
            />
          )}
        </div>

        {/* Refresh API status button */}
        <button
          onClick={onRefresh}
          title="Refresh backend status"
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/60 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>

        {/* Phase Indicator */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-950/40 border border-indigo-800/40 text-[11px] font-medium text-indigo-300">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span>Phase 8: Dashboard</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
