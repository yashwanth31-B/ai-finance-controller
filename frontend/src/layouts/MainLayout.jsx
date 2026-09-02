import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import useApiHealth from '../hooks/useApiHealth';
import { AlertCircle } from 'lucide-react';

export const MainLayout = () => {
  const { status, appInfo, lastChecked, error, refresh } = useApiHealth(15000);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 antialiased font-sans">
      {/* Navigation Sidebar */}
      <Sidebar
        apiStatus={status}
        appInfo={appInfo}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          apiStatus={status}
          lastChecked={lastChecked}
          onRefresh={refresh}
          onMobileToggle={() => setMobileOpen(true)}
        />

        {/* Backend Connectivity Alert (if offline) */}
        {status === 'offline' && (
          <div className="bg-rose-950/40 border-b border-rose-800/40 px-6 py-2.5 flex items-center justify-between text-xs text-rose-300">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>
                Unable to connect to the reconciliation service at <code className="bg-rose-900/40 px-1 py-0.5 rounded text-rose-200">http://localhost:8000</code>. Ensure the FastAPI backend is running.
              </span>
            </div>
            <button
              onClick={refresh}
              className="underline font-semibold hover:text-rose-200 ml-4 shrink-0"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Dynamic Route Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet context={{ apiStatus: status, appInfo, refreshApi: refresh }} />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
