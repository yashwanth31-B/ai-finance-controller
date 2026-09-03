import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Sliders,
  Server,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Info,
  ShieldCheck,
  Sun,
  Moon,
  Monitor,
  User,
  Bot,
  Sparkles
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorBanner from '../components/ErrorBanner';
import { getSettings, updateSettings, resetSettings } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

export const Settings = () => {
  const { apiStatus } = useOutletContext() || {};
  const { theme, setTheme } = useTheme();
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    amount_tolerance: 0.0,
    date_tolerance_days: 3,
    auto_match_threshold: 90.0,
    review_threshold: 70.0,
    fuzzy_similarity_threshold: 70.0,
    candidate_score_gap: 10.0
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);

  const fetchSettingsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSettings();
      setFormData({
        amount_tolerance: data.amount_tolerance,
        date_tolerance_days: data.date_tolerance_days,
        auto_match_threshold: data.auto_match_threshold,
        review_threshold: data.review_threshold,
        fuzzy_similarity_threshold: data.fuzzy_similarity_threshold,
        candidate_score_gap: data.candidate_score_gap
      });
    } catch (err) {
      console.error('Failed to load settings:', err);
      setError(err.response?.data?.detail || 'Failed to fetch platform settings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettingsData();
  }, []);

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification(null);
    }, 4000);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const validateFrontend = () => {
    const amt = parseFloat(formData.amount_tolerance);
    const dateTol = parseInt(formData.date_tolerance_days, 10);
    const autoThresh = parseFloat(formData.auto_match_threshold);
    const revThresh = parseFloat(formData.review_threshold);
    const fuzzyThresh = parseFloat(formData.fuzzy_similarity_threshold);
    const candGap = parseFloat(formData.candidate_score_gap);

    if (isNaN(amt) || amt < 0) return 'Amount difference tolerance cannot be negative.';
    if (isNaN(dateTol) || dateTol < 0) return 'Date window tolerance days cannot be negative.';
    if (isNaN(autoThresh) || autoThresh < 0 || autoThresh > 100) return 'Auto-match threshold must be between 0 and 100.';
    if (isNaN(revThresh) || revThresh < 0 || revThresh > 100) return 'Review threshold must be between 0 and 100.';
    if (autoThresh <= revThresh) return 'Auto-match threshold must be strictly greater than review threshold.';
    if (isNaN(fuzzyThresh) || fuzzyThresh < 0 || fuzzyThresh > 100) return 'Fuzzy similarity threshold must be between 0 and 100.';
    if (isNaN(candGap) || candGap < 0) return 'Candidate score gap cannot be negative.';

    return null;
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const valError = validateFrontend();
    if (valError) {
      showNotification(valError, 'error');
      return;
    }

    try {
      setSaving(true);
      const payload = {
        amount_tolerance: parseFloat(formData.amount_tolerance),
        date_tolerance_days: parseInt(formData.date_tolerance_days, 10),
        auto_match_threshold: parseFloat(formData.auto_match_threshold),
        review_threshold: parseFloat(formData.review_threshold),
        fuzzy_similarity_threshold: parseFloat(formData.fuzzy_similarity_threshold),
        candidate_score_gap: parseFloat(formData.candidate_score_gap)
      };

      await updateSettings(payload);
      showNotification('Settings saved successfully', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to save settings.', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    try {
      setResetting(true);
      const res = await resetSettings();
      setFormData({
        amount_tolerance: res.amount_tolerance,
        date_tolerance_days: res.date_tolerance_days,
        auto_match_threshold: res.auto_match_threshold,
        review_threshold: res.review_threshold,
        fuzzy_similarity_threshold: res.fuzzy_similarity_threshold,
        candidate_score_gap: res.candidate_score_gap
      });
      showNotification('Settings restored to default configuration', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to reset settings.', 'error');
    } finally {
      setResetting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <PageHeader
          title="Platform Settings & Rules"
          description="Configure multi-source matching tolerances, reconciliation thresholds, and backend rules."
        />
        <LoadingSkeleton type="cards" count={2} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Platform Settings & Rules"
          description="Configure multi-source matching tolerances, reconciliation thresholds, and backend rules."
        />
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/70 border border-indigo-800/60 text-indigo-300 text-xs font-mono">
          <ShieldCheck className="w-4 h-4 text-indigo-400" />
          <span>Settings apply to future reconciliation runs.</span>
        </div>
      </div>

      {/* Notification Toast */}
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

      {error && <ErrorBanner message={error} onRetry={fetchSettingsData} />}

      <form onSubmit={handleSave} className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Settings Form Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Appearance Section */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
                <div className="w-9 h-9 rounded-lg bg-violet-500/10 border border-violet-500/30 flex items-center justify-center text-violet-400">
                  <Sun className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Appearance & Theme</h3>
                  <p className="text-[11px] text-slate-400">
                    Choose interface theme for sidebar, headers, cards, tables, and modals.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setTheme('dark')}
                  className={`p-3 rounded-lg border text-center transition-all flex flex-col items-center gap-2 ${
                    theme === 'dark'
                      ? 'bg-indigo-950/80 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <Moon className="w-5 h-5 text-indigo-400" />
                  <span className="text-xs font-bold">Dark Mode</span>
                </button>

                <button
                  type="button"
                  onClick={() => setTheme('light')}
                  className={`p-3 rounded-lg border text-center transition-all flex flex-col items-center gap-2 ${
                    theme === 'light'
                      ? 'bg-indigo-950/80 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <Sun className="w-5 h-5 text-amber-400" />
                  <span className="text-xs font-bold">Light Mode</span>
                </button>

                <button
                  type="button"
                  onClick={() => setTheme('system')}
                  className={`p-3 rounded-lg border text-center transition-all flex flex-col items-center gap-2 ${
                    theme === 'system'
                      ? 'bg-indigo-950/80 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  <Monitor className="w-5 h-5 text-violet-400" />
                  <span className="text-xs font-bold">System Theme</span>
                </button>
              </div>
            </div>

            {/* Section 1: Monetary & Time Tolerances */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
                <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Reconciliation Matching Tolerances</h3>
                  <p className="text-[11px] text-slate-400">
                    Set allowed monetary variance and payment settlement delay windows.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Amount Difference Tolerance */}
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">
                    Amount Difference Tolerance
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    name="amount_tolerance"
                    value={formData.amount_tolerance}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-indigo-500 transition-colors"
                    placeholder="0.00"
                  />
                  <span className="text-[11px] text-slate-400 mt-1.5 flex items-start gap-1">
                    <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                    <span>Maximum allowed amount difference before a record is treated as an amount mismatch.</span>
                  </span>
                </div>

                {/* Date Window Tolerance */}
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">
                    Date Window Tolerance (Days)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    name="date_tolerance_days"
                    value={formData.date_tolerance_days}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-indigo-500 transition-colors"
                    placeholder="3"
                  />
                  <span className="text-[11px] text-slate-400 mt-1.5 flex items-start gap-1">
                    <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                    <span>Maximum allowed settlement delay in days between invoice and payment date.</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Section 2: Confidence & Rule Thresholds */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
                <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Confidence & Discrepancy Thresholds</h3>
                  <p className="text-[11px] text-slate-400">
                    Configure confidence limits for automatic matching and human review routing.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Auto Match Threshold */}
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">
                    Auto Match Threshold (0 - 100)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    max="100"
                    name="auto_match_threshold"
                    value={formData.auto_match_threshold}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-emerald-400 font-bold focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                  <span className="text-[11px] text-slate-400 mt-1.5 flex items-start gap-1">
                    <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                    <span>Minimum confidence required for automatic reconciliation.</span>
                  </span>
                </div>

                {/* Review Threshold */}
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">
                    Review Threshold (0 - 100)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    max="100"
                    name="review_threshold"
                    value={formData.review_threshold}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-amber-400 font-bold focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                  <span className="text-[11px] text-slate-400 mt-1.5 flex items-start gap-1">
                    <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                    <span>Minimum score to qualify for human review instead of automatic exception.</span>
                  </span>
                </div>

                {/* Fuzzy Similarity Threshold */}
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">
                    Fuzzy Similarity Threshold (0 - 100)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    max="100"
                    name="fuzzy_similarity_threshold"
                    value={formData.fuzzy_similarity_threshold}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-indigo-300 font-bold focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                  <span className="text-[11px] text-slate-400 mt-1.5 flex items-start gap-1">
                    <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                    <span>Minimum company name similarity score required for fuzzy matching.</span>
                  </span>
                </div>

                {/* Candidate Score Gap */}
                <div>
                  <label className="block text-xs font-semibold text-slate-200 mb-1">
                    Candidate Score Gap
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    name="candidate_score_gap"
                    value={formData.candidate_score_gap}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-purple-300 font-bold focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                  <span className="text-[11px] text-slate-400 mt-1.5 flex items-start gap-1">
                    <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                    <span>Minimum score difference between top two candidates to avoid ambiguous match classification.</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-2">
              <button
                type="button"
                onClick={handleReset}
                disabled={resetting || saving}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all disabled:opacity-50"
              >
                {resetting ? <Loader2 className="w-4 h-4 animate-spin" /> : <RotateCcw className="w-4 h-4" />}
                <span>Reset Defaults</span>
              </button>

              <button
                type="submit"
                disabled={saving || resetting}
                className="inline-flex items-center gap-2.5 px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50"
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                <span>Save Settings</span>
              </button>
            </div>
          </div>

          {/* Sidebar / Connection & User Info Panel */}
          <div className="space-y-6">
            {/* Account Info Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <User className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Account Information</h3>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Name:</span>
                  <span className="text-slate-200 font-bold">{user?.name || 'Finance User'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Email:</span>
                  <span className="text-slate-200 font-mono">{user?.email || 'user@finance.ai'}</span>
                </div>
                <div className="flex justify-between items-center pt-1">
                  <span className="text-slate-400">Role:</span>
                  <StatusBadge status={user?.role || 'REVIEWER'} variant="indigo" size="sm" />
                </div>
              </div>
            </div>

            {/* AI Assistant Provider Status */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Bot className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-bold text-white">AI Assistant Engine Status</h3>
              </div>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Engine State:</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    ENABLED
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Provider:</span>
                  <span className="text-slate-200 font-mono text-[11px]">Rule Engine + OpenAI Fallback</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed border-t border-slate-800/80 pt-2">
                  System queries reconciliation database deterministically first before invoking AI reasoning. API key secrets are kept strictly server-side.
                </p>
              </div>
            </div>

            {/* Diagnostic Connection Panel */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Server className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Backend Connection</h3>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    API Base URL (Read-Only)
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-indigo-300 cursor-not-allowed select-all"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Backend Service Health
                  </label>
                  <div className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs">
                    <span className="text-slate-300 font-medium">FastAPI Status</span>
                    <StatusBadge
                      status={apiStatus === 'healthy' ? 'CONNECTED' : 'OFFLINE'}
                      variant={apiStatus === 'healthy' ? 'success' : 'danger'}
                      size="sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Settings;
