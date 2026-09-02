import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileSpreadsheet,
  Landmark,
  CreditCard,
  CheckCircle2,
  AlertTriangle,
  X,
  Play,
  Loader2,
  FileCheck,
  ArrowRight,
  Database,
  Info
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import ErrorBanner from '../components/ErrorBanner';
import { validateUploadFiles, runUploadedReconciliation, runReconciliation } from '../services/api';

const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const Upload = () => {
  const navigate = useNavigate();

  // Selected File States
  const [files, setFiles] = useState({
    invoices: null,
    bank: null,
    gateway: null,
  });

  // Drag over States per card
  const [dragOver, setDragOver] = useState({
    invoices: false,
    bank: false,
    gateway: false,
  });

  // File Inputs Refs
  const inputRefs = {
    invoices: useRef(null),
    bank: useRef(null),
    gateway: useRef(null),
  };

  // State Management
  const [stage, setStage] = useState('SELECTING'); // SELECTING -> VALIDATING -> READY -> RUNNING -> COMPLETED
  const [validationResult, setValidationResult] = useState(null);
  const [activePreviewTab, setActivePreviewTab] = useState('invoices');
  const [clientErrors, setClientErrors] = useState({});
  const [globalError, setGlobalError] = useState(null);
  const [isRunningDemo, setIsRunningDemo] = useState(false);

  // File Selection Handler
  const handleFileSelect = (type, file) => {
    setGlobalError(null);
    setValidationResult(null);
    setStage('SELECTING');

    if (!file) return;

    // Check extension
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setClientErrors((prev) => ({
        ...prev,
        [type]: `Invalid file type. Only .csv files are permitted.`,
      }));
      return;
    }

    // Check size
    if (file.size > MAX_SIZE_BYTES) {
      setClientErrors((prev) => ({
        ...prev,
        [type]: `File size (${formatBytes(file.size)}) exceeds the 10 MB limit.`,
      }));
      return;
    }

    // Clear client error and save file
    setClientErrors((prev) => ({ ...prev, [type]: null }));
    setFiles((prev) => ({ ...prev, [type]: file }));
  };

  // Remove File Handler
  const handleRemoveFile = (type) => {
    setFiles((prev) => ({ ...prev, [type]: null }));
    setClientErrors((prev) => ({ ...prev, [type]: null }));
    setValidationResult(null);
    setStage('SELECTING');
    if (inputRefs[type].current) {
      inputRefs[type].current.value = '';
    }
  };

  // Drag & Drop Handlers
  const handleDragOver = (type, e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver((prev) => ({ ...prev, [type]: true }));
  };

  const handleDragLeave = (type, e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver((prev) => ({ ...prev, [type]: false }));
  };

  const handleDrop = (type, e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver((prev) => ({ ...prev, [type]: false }));
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(type, droppedFile);
    }
  };

  // Validate Uploaded Files
  const handleValidate = async () => {
    if (!files.invoices || !files.bank || !files.gateway) {
      setGlobalError('Please select all three CSV files before running validation.');
      return;
    }

    try {
      setStage('VALIDATING');
      setGlobalError(null);

      const formData = new FormData();
      formData.append('invoices', files.invoices);
      formData.append('bank', files.bank);
      formData.append('gateway', files.gateway);

      const result = await validateUploadFiles(formData);
      setValidationResult(result);

      if (result.valid) {
        setStage('READY');
      } else {
        setStage('SELECTING');
      }
    } catch (err) {
      console.error('Validation request failed:', err);
      setGlobalError('Unable to connect to the reconciliation service for validation.');
      setStage('SELECTING');
    }
  };

  // Run Uploaded Reconciliation
  const handleRunUploadedReconciliation = async () => {
    if (!validationResult || !validationResult.upload_batch_id) return;

    try {
      setStage('RUNNING');
      setGlobalError(null);
      await runUploadedReconciliation(validationResult.upload_batch_id);
      setStage('COMPLETED');
    } catch (err) {
      console.error('Uploaded reconciliation run failed:', err);
      setGlobalError('Reconciliation execution failed. Ensure backend service is active.');
      setStage('READY');
    }
  };

  // Use Synthetic Demo Data Fallback
  const handleUseDemoData = async () => {
    try {
      setIsRunningDemo(true);
      setGlobalError(null);
      await runReconciliation();
      navigate('/reconciliation');
    } catch (err) {
      console.error('Demo reconciliation run failed:', err);
      setGlobalError('Unable to run demo reconciliation. Ensure backend is active.');
    } finally {
      setIsRunningDemo(false);
    }
  };

  const allFilesSelected = files.invoices && files.bank && files.gateway;

  return (
    <div className="space-y-8">
      {/* Page Title & Demo Data Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Multi-Source Data Ingestion</h1>
          <p className="text-xs text-slate-400 mt-1">
            Upload, validate, preview, and reconcile CSV exports across Invoices, Bank Feeds, and Payment Gateways.
          </p>
        </div>

        <button
          onClick={handleUseDemoData}
          disabled={isRunningDemo}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 border border-slate-700 text-xs font-semibold shadow-md transition-all shrink-0"
        >
          {isRunningDemo ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading Demo Data...</span>
            </>
          ) : (
            <>
              <Database className="w-4 h-4 text-indigo-400" />
              <span>Use Demo Data</span>
            </>
          )}
        </button>
      </div>

      {/* Global Error Banner */}
      {globalError && <ErrorBanner message={globalError} />}

      {/* Stage Progress Indicator */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between overflow-x-auto text-xs">
        {[
          { key: 'SELECTING', label: '1. Select Files' },
          { key: 'VALIDATING', label: '2. Validating' },
          { key: 'READY', label: '3. Ready to Reconcile' },
          { key: 'RUNNING', label: '4. Running Engine' },
          { key: 'COMPLETED', label: '5. Completed' },
        ].map((sStep, idx) => {
          const isCurrent = stage === sStep.key;
          const isDone =
            (stage === 'READY' && (sStep.key === 'SELECTING' || sStep.key === 'VALIDATING')) ||
            (stage === 'RUNNING' && sStep.key !== 'COMPLETED') ||
            stage === 'COMPLETED';

          return (
            <div key={sStep.key} className="flex items-center gap-2 shrink-0">
              <span
                className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
                  isCurrent
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                    : isDone
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-slate-950 text-slate-400 border border-slate-800'
                }`}
              >
                {sStep.label}
              </span>
              {idx < 4 && <ArrowRight className="w-3.5 h-3.5 text-slate-700" />}
            </div>
          );
        })}
      </div>

      {/* 3 Upload Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Invoice Data */}
        <UploadCard
          type="invoices"
          title="Invoice Ledger CSV"
          description="ERP / billing ledger containing invoice_id, customer_name, amount, currency, invoice_date, reference."
          icon={FileSpreadsheet}
          accentColor="indigo"
          file={files.invoices}
          clientError={clientErrors.invoices}
          validationResult={validationResult?.files?.invoices}
          dragOver={dragOver.invoices}
          inputRef={inputRefs.invoices}
          onSelect={(f) => handleFileSelect('invoices', f)}
          onRemove={() => handleRemoveFile('invoices')}
          onDragOver={(e) => handleDragOver('invoices', e)}
          onDragLeave={(e) => handleDragLeave('invoices', e)}
          onDrop={(e) => handleDrop('invoices', e)}
        />

        {/* Card 2: Bank Transactions */}
        <UploadCard
          type="bank"
          title="Bank Transactions CSV"
          description="Bank statement feed containing transaction_id, description, amount, currency, transaction_date, reference."
          icon={Landmark}
          accentColor="emerald"
          file={files.bank}
          clientError={clientErrors.bank}
          validationResult={validationResult?.files?.bank}
          dragOver={dragOver.bank}
          inputRef={inputRefs.bank}
          onSelect={(f) => handleFileSelect('bank', f)}
          onRemove={() => handleRemoveFile('bank')}
          onDragOver={(e) => handleDragOver('bank', e)}
          onDragLeave={(e) => handleDragLeave('bank', e)}
          onDrop={(e) => handleDrop('bank', e)}
        />

        {/* Card 3: Gateway Transactions */}
        <UploadCard
          type="gateway"
          title="Gateway Settlement CSV"
          description="Razorpay / Stripe processor report containing payment_id, customer_name, amount, currency, payment_date, reference."
          icon={CreditCard}
          accentColor="violet"
          file={files.gateway}
          clientError={clientErrors.gateway}
          validationResult={validationResult?.files?.gateway}
          dragOver={dragOver.gateway}
          inputRef={inputRefs.gateway}
          onSelect={(f) => handleFileSelect('gateway', f)}
          onRemove={() => handleRemoveFile('gateway')}
          onDragOver={(e) => handleDragOver('gateway', e)}
          onDragLeave={(e) => handleDragLeave('gateway', e)}
          onDrop={(e) => handleDrop('gateway', e)}
        />
      </div>

      {/* Action Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div>
          <h3 className="text-sm font-bold text-white">Validation & Execution Controls</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Validate all 3 files before triggering the 3-way reconciliation engine.
          </p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {stage === 'SELECTING' && (
            <button
              onClick={handleValidate}
              disabled={!allFilesSelected}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold shadow-lg shadow-indigo-600/20 transition-all"
            >
              <FileCheck className="w-4 h-4" />
              <span>Validate CSV Files</span>
            </button>
          )}

          {stage === 'VALIDATING' && (
            <button disabled className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600/50 text-white text-xs font-bold">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Validating Schemas...</span>
            </button>
          )}

          {stage === 'READY' && (
            <button
              onClick={handleRunUploadedReconciliation}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/25 transition-all"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>Run Reconciliation</span>
            </button>
          )}

          {stage === 'RUNNING' && (
            <button disabled className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-2.5 rounded-xl bg-emerald-600/50 text-white text-xs font-bold">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Running Reconciliation Engine...</span>
            </button>
          )}

          {stage === 'COMPLETED' && (
            <button
              onClick={() => navigate('/reconciliation')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all"
            >
              <span>View Reconciliation Results</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Completion Banner */}
      {stage === 'COMPLETED' && (
        <div className="bg-emerald-950/40 border border-emerald-800/40 rounded-xl p-5 text-emerald-300 flex items-center justify-between text-xs">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
            <div>
              <h4 className="font-bold text-white text-sm">Batch Reconciliation Completed</h4>
              <p className="text-emerald-200/80 mt-0.5">
                Uploaded files successfully normalized and reconciled across 3 sources. Dashboard KPIs updated.
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/reconciliation')}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow transition-colors shrink-0"
          >
            Go to Results
          </button>
        </div>
      )}

      {/* CSV Data Preview Section */}
      {validationResult && validationResult.valid && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden space-y-4 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Uploaded Data Preview (First 10 Rows)
              </h3>
              <p className="text-[11px] text-slate-400">
                {validationResult.files[activePreviewTab]?.rows} total rows — displaying first 10
              </p>
            </div>

            {/* Preview Tabs */}
            <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800">
              {[
                { id: 'invoices', label: 'Invoices' },
                { id: 'bank', label: 'Bank Transactions' },
                { id: 'gateway', label: 'Gateway Transactions' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActivePreviewTab(tab.id)}
                  className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-colors ${
                    activePreviewTab === tab.id
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Preview Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="text-[11px] text-slate-400 border-b border-slate-800 bg-slate-950/60 uppercase tracking-wider">
                  {validationResult.files[activePreviewTab]?.preview?.length > 0 &&
                    Object.keys(validationResult.files[activePreviewTab].preview[0]).map((col) => (
                      <th key={col} className="py-2.5 px-3">
                        {col}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                {validationResult.files[activePreviewTab]?.preview?.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                    {Object.values(row).map((val, cIdx) => (
                      <td key={cIdx} className="py-2.5 px-3 whitespace-nowrap">
                        {val !== null && val !== undefined ? String(val) : '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Reusable Upload Card Component
const UploadCard = ({
  type,
  title,
  description,
  icon: Icon,
  accentColor,
  file,
  clientError,
  validationResult,
  dragOver,
  inputRef,
  onSelect,
  onRemove,
  onDragOver,
  onDragLeave,
  onDrop,
}) => {
  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className={`bg-slate-900 border rounded-xl p-6 flex flex-col justify-between transition-all ${
        dragOver ? 'border-indigo-500 bg-indigo-950/20' : 'border-slate-800'
      }`}
    >
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className={`p-2 rounded-lg bg-${accentColor}-500/10 text-${accentColor}-400 border border-${accentColor}-500/20`}>
            <Icon className="w-5 h-5" />
          </div>
          {validationResult && (
            <StatusBadge
              label={validationResult.valid ? 'Valid CSV' : 'Schema Error'}
              variant={validationResult.valid ? 'success' : 'danger'}
              size="sm"
            />
          )}
        </div>

        <h3 className="text-base font-bold text-white">{title}</h3>
        <p className="text-xs text-slate-400 mt-1 leading-relaxed">{description}</p>
      </div>

      {/* Selected File Area or Dropzone */}
      <div className="mt-6">
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          onChange={(e) => onSelect(e.target.files[0])}
          className="hidden"
        />

        {file ? (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 min-w-0">
                <FileCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="text-xs font-semibold text-slate-200 truncate">{file.name}</span>
              </div>
              <button
                onClick={onRemove}
                className="p-1 text-slate-400 hover:text-rose-400 rounded-md transition-colors"
                title="Remove file"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <span className="text-[11px] text-slate-400 block font-mono">{formatBytes(file.size)}</span>
          </div>
        ) : (
          <div
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-xl p-6 text-center bg-slate-950/40 hover:bg-slate-950/80 cursor-pointer transition-all"
          >
            <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <div className="text-xs font-semibold text-slate-300">Click or drag CSV here</div>
            <div className="text-[11px] text-slate-400 mt-1">Maximum 10 MB per file</div>
          </div>
        )}

        {/* Client Error Message */}
        {clientError && (
          <div className="mt-3 p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/40 text-[11px] text-rose-300 flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
            <span>{clientError}</span>
          </div>
        )}

        {/* Server Validation Errors */}
        {validationResult && validationResult.errors?.length > 0 && (
          <div className="mt-3 p-3 rounded-lg bg-rose-950/40 border border-rose-800/40 text-[11px] text-rose-300 space-y-1">
            <div className="font-semibold text-rose-400 mb-1 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Validation Errors:</span>
            </div>
            <ul className="list-disc list-inside space-y-0.5 text-[11px]">
              {validationResult.errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
