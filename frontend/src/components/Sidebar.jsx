import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitCompare,
  AlertTriangle,
  UploadCloud,
  History,
  Settings,
  Scale,
  CircleDot
} from 'lucide-react';
import { NAV_ITEMS } from '../utils/constants';

const ICON_MAP = {
  LayoutDashboard,
  GitCompare,
  AlertTriangle,
  UploadCloud,
  History,
  Settings,
};

export const Sidebar = ({ apiStatus, appInfo }) => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
          <Scale className="w-5 h-5" />
        </div>
        <div>
          <div className="text-sm font-bold text-white tracking-tight leading-none">
            AI Finance Controller
          </div>
          <div className="text-[11px] text-slate-400 font-medium mt-1">
            Multi-Source Reconciler
          </div>
        </div>
      </div>

      {/* Navigation Section */}
      <div className="flex-1 py-5 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Reconciliation Platform
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = ICON_MAP[item.iconName] || CircleDot;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800 text-xs">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-slate-400 font-medium">Backend Engine</span>
            <span className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === 'healthy'
                    ? 'bg-emerald-400 animate-pulse'
                    : apiStatus === 'checking'
                    ? 'bg-amber-400 animate-ping'
                    : 'bg-rose-400'
                }`}
              />
              <span
                className={`font-semibold capitalize ${
                  apiStatus === 'healthy'
                    ? 'text-emerald-400'
                    : apiStatus === 'checking'
                    ? 'text-amber-400'
                    : 'text-rose-400'
                }`}
              >
                {apiStatus}
              </span>
            </span>
          </div>
          <div className="text-[11px] text-slate-400 font-mono truncate">
            {appInfo?.name || 'FastAPI Service'}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
