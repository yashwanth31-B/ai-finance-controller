import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Scale,
  Lock,
  Mail,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle,
  Sun,
  Moon,
  Monitor
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const { theme, setTheme } = useTheme();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemoAccount = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError(null);
  };

  return (
    <div className="relative min-h-screen bg-slate-950 dark:bg-slate-950 light:bg-slate-50 flex flex-col items-center justify-center p-4 text-slate-100 dark:text-slate-100 light:text-slate-900 font-sans transition-colors duration-150">
      {/* Top-Right Theme Selector */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6 z-10 flex items-center p-1 rounded-xl bg-slate-900/80 dark:bg-slate-900/80 light:bg-white border border-slate-800 dark:border-slate-800 light:border-slate-200 shadow-md">
        <button
          type="button"
          onClick={() => setTheme('dark')}
          title="Dark Mode"
          aria-label="Dark Mode"
          className={`p-2 rounded-lg text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
            theme === 'dark'
              ? 'bg-indigo-600 text-white shadow-sm font-bold'
              : 'text-slate-400 hover:text-slate-200 dark:hover:text-slate-200 light:hover:text-slate-800'
          }`}
        >
          <Moon className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={() => setTheme('light')}
          title="Light Mode"
          aria-label="Light Mode"
          className={`p-2 rounded-lg text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
            theme === 'light'
              ? 'bg-indigo-600 text-white shadow-sm font-bold'
              : 'text-slate-400 hover:text-slate-200 dark:hover:text-slate-200 light:hover:text-slate-800'
          }`}
        >
          <Sun className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={() => setTheme('system')}
          title="System Theme"
          aria-label="System Theme"
          className={`p-2 rounded-lg text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
            theme === 'system'
              ? 'bg-indigo-600 text-white shadow-sm font-bold'
              : 'text-slate-400 hover:text-slate-200 dark:hover:text-slate-200 light:hover:text-slate-800'
          }`}
        >
          <Monitor className="w-4 h-4" />
        </button>
      </div>

      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-lg shadow-indigo-600/30 mb-2">
            <Scale className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-extrabold text-white dark:text-white light:text-slate-900 tracking-tight">
            AI Finance Controller
          </h1>
          <p className="text-xs text-slate-400 dark:text-slate-400 light:text-slate-600">
            Multi-Source 3-Way Financial Reconciliation Platform
          </p>
        </div>

        {/* Login Form Card */}
        <div className="bg-slate-900 dark:bg-slate-900 light:bg-white border border-slate-800 dark:border-slate-800 light:border-slate-200 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 dark:border-slate-800 light:border-slate-200 pb-4">
            <h2 className="text-base font-bold text-white dark:text-white light:text-slate-900">
              Sign In to Controller Portal
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-950 dark:bg-indigo-950 light:bg-indigo-50 border border-indigo-800 dark:border-indigo-800 light:border-indigo-200 text-indigo-300 dark:text-indigo-300 light:text-indigo-700 font-mono font-semibold">
              Secure Auth
            </span>
          </div>

          {error && (
            <div className="p-3.5 rounded-lg bg-rose-950/80 dark:bg-rose-950/80 light:bg-rose-50 border border-rose-800/80 dark:border-rose-800/80 light:border-rose-200 text-rose-300 dark:text-rose-300 light:text-rose-800 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 dark:text-slate-300 light:text-slate-700 mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 dark:bg-slate-950 light:bg-white border border-slate-700 dark:border-slate-700 light:border-slate-300 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-white dark:text-white light:text-slate-900 focus:outline-none focus:border-indigo-500 transition-colors"
                  placeholder="reviewer@finance.ai"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 dark:text-slate-300 light:text-slate-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-950 dark:bg-slate-950 light:bg-white border border-slate-700 dark:border-slate-700 light:border-slate-300 rounded-lg pl-9 pr-10 py-2 text-xs font-mono text-white dark:text-white light:text-slate-900 focus:outline-none focus:border-indigo-500 transition-colors"
                  placeholder="••••••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 dark:hover:text-slate-200 light:hover:text-slate-700"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-400 dark:text-slate-400 light:text-slate-600">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-700 dark:border-slate-700 light:border-slate-300 bg-slate-950 dark:bg-slate-950 light:bg-white text-indigo-600 focus:ring-0"
                />
                <span>Remember me on this device</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <span>Sign In</span>
              )}
            </button>
          </form>

          {/* Quick Demo Accounts Banner */}
          <div className="pt-4 border-t border-slate-800 dark:border-slate-800 light:border-slate-200 space-y-2.5">
            <div className="text-[11px] font-semibold text-slate-400 dark:text-slate-400 light:text-slate-500 uppercase tracking-wider text-center">
              Quick Demo Accounts
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => fillDemoAccount('admin@finance.ai', 'Admin@123')}
                aria-label="Use Admin demo account"
                className="p-2 rounded-lg bg-slate-950 dark:bg-slate-950 light:bg-slate-50 hover:bg-slate-800 dark:hover:bg-slate-800 light:hover:bg-slate-100 border border-slate-800 dark:border-slate-800 light:border-slate-200 text-center transition-all group focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <div className="text-[11px] font-bold text-indigo-400 group-hover:text-indigo-300">Admin</div>
                <div className="text-[9px] text-slate-400 dark:text-slate-400 light:text-slate-600 font-mono mt-0.5">
                  Full Access
                </div>
              </button>

              <button
                type="button"
                onClick={() => fillDemoAccount('reviewer@finance.ai', 'Reviewer@123')}
                aria-label="Use Reviewer demo account"
                className="p-2 rounded-lg bg-slate-950 dark:bg-slate-950 light:bg-slate-50 hover:bg-slate-800 dark:hover:bg-slate-800 light:hover:bg-slate-100 border border-slate-800 dark:border-slate-800 light:border-slate-200 text-center transition-all group focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <div className="text-[11px] font-bold text-emerald-400 group-hover:text-emerald-300">Reviewer</div>
                <div className="text-[9px] text-slate-400 dark:text-slate-400 light:text-slate-600 font-mono mt-0.5">
                  Review/Upload
                </div>
              </button>

              <button
                type="button"
                onClick={() => fillDemoAccount('viewer@finance.ai', 'Viewer@123')}
                aria-label="Use Viewer demo account"
                className="p-2 rounded-lg bg-slate-950 dark:bg-slate-950 light:bg-slate-50 hover:bg-slate-800 dark:hover:bg-slate-800 light:hover:bg-slate-100 border border-slate-800 dark:border-slate-800 light:border-slate-200 text-center transition-all group focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <div className="text-[11px] font-bold text-amber-400 group-hover:text-amber-300">Viewer</div>
                <div className="text-[9px] text-slate-400 dark:text-slate-400 light:text-slate-600 font-mono mt-0.5">
                  Read-Only
                </div>
              </button>
            </div>
          </div>
        </div>

        <div className="text-center text-[11px] text-slate-400 dark:text-slate-400 light:text-slate-600">
          AI Finance Controller &copy; 2026. Hackathon FinTech Edition.
        </div>
      </div>
    </div>
  );
};

export default Login;
