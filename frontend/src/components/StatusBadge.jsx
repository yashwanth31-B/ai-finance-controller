import React from 'react';

const VARIANT_STYLES = {
  success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  danger: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  neutral: 'bg-slate-800 text-slate-400 border-slate-700',
};

export const StatusBadge = ({ label, variant = 'neutral', size = 'md', dot = false }) => {
  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };

  const dotColors = {
    success: 'bg-emerald-400',
    warning: 'bg-amber-400',
    danger: 'bg-rose-400',
    info: 'bg-blue-400',
    indigo: 'bg-indigo-400',
    neutral: 'bg-slate-400',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${VARIANT_STYLES[variant] || VARIANT_STYLES.neutral} ${sizeStyles[size] || sizeStyles.md}`}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant] || dotColors.neutral} animate-pulse`} />
      )}
      {label}
    </span>
  );
};

export default StatusBadge;
