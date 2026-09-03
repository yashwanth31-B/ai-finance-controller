import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  RefreshCw,
  ShieldCheck,
  Menu,
  Sun,
  Moon,
  Monitor,
  User,
  LogOut,
  ChevronDown,
  Shield
} from 'lucide-react';
import { NAV_ITEMS } from '../utils/constants';
import StatusBadge from './StatusBadge';
import NotificationCenter from './NotificationCenter';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

export const Header = ({ apiStatus, lastChecked, onRefresh, onMobileToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const { user, logout } = useAuth();

  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);

  const currentNav = NAV_ITEMS.find((item) => item.path === location.pathname) || {
    label: 'Dashboard',
    description: 'Executive overview & reconciliation KPIs'
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenuOpen(false);
      }
    };
    if (userMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [userMenuOpen]);

  const handleLogout = async () => {
    setUserMenuOpen(false);
    await logout();
    navigate('/login');
  };

  const getRoleBadgeVariant = (role) => {
    switch (role) {
      case 'ADMIN':
        return 'indigo';
      case 'REVIEWER':
        return 'success';
      case 'VIEWER':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <header className="h-16 bg-slate-900/80 dark:bg-slate-900/90 light:bg-white/90 backdrop-blur-md border-b border-slate-800 dark:border-slate-800 light:border-slate-200 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
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
          <span className="text-slate-200 dark:text-slate-200 light:text-slate-800 font-medium">{currentNav.label}</span>
        </div>
      </div>

      {/* Right controls: Theme, Notifications, API Health & User Profile */}
      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Theme Toggle Selector */}
        <div className="flex items-center p-0.5 rounded-lg bg-slate-950/70 border border-slate-800 dark:bg-slate-950/70 light:bg-slate-100">
          <button
            onClick={() => setTheme('dark')}
            title="Dark Theme"
            className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
              theme === 'dark' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Moon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setTheme('light')}
            title="Light Theme"
            className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
              theme === 'light' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sun className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setTheme('system')}
            title="System Preference"
            className={`p-1.5 rounded-md text-xs font-medium transition-colors ${
              theme === 'system' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Monitor className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Notification Center Bell */}
        <NotificationCenter />

        {/* Refresh API status button */}
        <button
          onClick={onRefresh}
          title="Refresh backend status"
          className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/60 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* User Profile Menu */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-slate-800/60 transition-colors text-left"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 text-white text-xs font-bold flex items-center justify-center shadow-md">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-bold text-slate-200 dark:text-slate-200 light:text-slate-900 leading-tight">
                {user?.name || 'Finance User'}
              </div>
              <div className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
                <span>{user?.role || 'REVIEWER'}</span>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400 hidden sm:block" />
          </button>

          {userMenuOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 py-2 divide-y divide-slate-800">
              <div className="px-4 py-2.5 space-y-1">
                <div className="text-xs font-bold text-white">{user?.name}</div>
                <div className="text-[11px] text-slate-400 font-mono truncate">{user?.email}</div>
                <div className="pt-1">
                  <StatusBadge
                    status={user?.role || 'REVIEWER'}
                    variant={getRoleBadgeVariant(user?.role)}
                    size="sm"
                  />
                </div>
              </div>

              <div className="py-1">
                <button
                  onClick={() => {
                    setUserMenuOpen(false);
                    navigate('/settings');
                  }}
                  className="w-full text-left px-4 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white flex items-center gap-2 transition-colors"
                >
                  <User className="w-4 h-4 text-indigo-400" />
                  <span>Account & Profile</span>
                </button>
              </div>

              <div className="py-1">
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-xs text-rose-400 hover:bg-rose-950/40 flex items-center gap-2 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
