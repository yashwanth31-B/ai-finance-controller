import React from 'react';
import { Layers, ShieldCheck, ArrowRight, Sparkles } from 'lucide-react';
import StatusBadge from './StatusBadge';

export const PlaceholderCard = ({
  title,
  description,
  phase = 'Phase 1: Project Foundation',
  nextSteps = [],
  icon: Icon = Layers
}) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 lg:p-8 backdrop-blur-sm">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <StatusBadge label={phase} variant="indigo" size="sm" />
          </div>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            {description}
          </p>

          {nextSteps.length > 0 && (
            <div className="mt-6 pt-5 border-t border-slate-800/80">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Target Capabilities in Next Phase
              </h4>
              <ul className="space-y-2.5">
                {nextSteps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                    <ArrowRight className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlaceholderCard;
