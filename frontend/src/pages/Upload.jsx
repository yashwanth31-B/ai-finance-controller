import React from 'react';
import { UploadCloud, FileSpreadsheet, Landmark, CreditCard, Info } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import PlaceholderCard from '../components/PlaceholderCard';

export const Upload = () => {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Multi-Source Data Ingestion"
        description="Upload batch datasets for Invoice Systems, Bank Transactions, and Payment Gateways (50+ records per batch)."
        badge={<StatusBadge label="Phase 1: Foundation" variant="indigo" size="md" />}
      />

      {/* 3 Source Ingestion Panels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Source 1: Invoices */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <StatusBadge label="Source 1" variant="neutral" size="sm" />
            </div>
            <h3 className="text-base font-semibold text-white">Invoice System Records</h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports CSV / JSON invoice exports containing Invoice ID, Customer, Amount, Issue Date, Due Date.
            </p>
          </div>

          <div className="mt-6 border-2 border-dashed border-slate-800 rounded-lg p-6 text-center bg-slate-950/40">
            <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <div className="text-xs font-semibold text-slate-300">
              Drop Invoice Files
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              CSV or JSON format
            </div>
          </div>
        </div>

        {/* Source 2: Bank Transactions */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <Landmark className="w-5 h-5" />
              </div>
              <StatusBadge label="Source 2" variant="neutral" size="sm" />
            </div>
            <h3 className="text-base font-semibold text-white">Bank Transaction Feeds</h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports bank statement feeds containing Transaction Reference, Value Date, Debit/Credit, Description.
            </p>
          </div>

          <div className="mt-6 border-2 border-dashed border-slate-800 rounded-lg p-6 text-center bg-slate-950/40">
            <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <div className="text-xs font-semibold text-slate-300">
              Drop Bank Statements
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              CSV, MT940, or CAMT
            </div>
          </div>
        </div>

        {/* Source 3: Payment Gateways */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
                <CreditCard className="w-5 h-5" />
              </div>
              <StatusBadge label="Source 3" variant="neutral" size="sm" />
            </div>
            <h3 className="text-base font-semibold text-white">Gateway Settlements</h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports Razorpay/Stripe settlement logs with Payment ID, Settlement ID, Gross, Fee, Tax, Net.
            </p>
          </div>

          <div className="mt-6 border-2 border-dashed border-slate-800 rounded-lg p-6 text-center bg-slate-950/40">
            <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <div className="text-xs font-semibold text-slate-300">
              Drop Gateway Logs
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              CSV or JSON settlements
            </div>
          </div>
        </div>
      </div>

      <PlaceholderCard
        title="Batch Ingestion Pipeline (50+ records capability)"
        description="The multi-source ingestion pipeline validates schemas, checks integrity, and loads data into SQLite for high-throughput batch reconciliation."
        phase="Phase 1: Foundation"
        icon={UploadCloud}
        nextSteps={[
          'Pandas-based high performance CSV / JSON batch parsing',
          'Automated column mapping and schema validation',
          'Batch validation of 50+ transaction records per source',
          'Data cleaning and currency normalization',
        ]}
      />
    </div>
  );
};

export default Upload;
