import React from 'react';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  badgeVariant = 'neutral',
  accentColor = 'indigo'
}) => {
  const accentBorders = {
    indigo: 'hover:border-indigo-500/50',
    emerald: 'hover:border-emerald-500/50',
    amber: 'hover:border-amber-500/50',
    rose: 'hover:border-rose-500/50',
    blue: 'hover:border-blue-500/50',
  };

  const iconColors = {
    indigo: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  };

  return (
    <div
      className={`relative bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm transition-all duration-200 ${accentBorders[accentColor] || accentBorders.indigo}`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${iconColors[accentColor] || iconColors.indigo}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono">
          {value}
        </span>
        {badge && (
          <span className="text-xs text-slate-400 font-medium">
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-2">
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default StatCard;
