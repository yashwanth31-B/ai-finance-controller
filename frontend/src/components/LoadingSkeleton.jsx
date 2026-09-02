import React from 'react';

export const CardSkeleton = () => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 animate-pulse">
    <div className="flex items-center justify-between mb-3">
      <div className="h-3 bg-slate-800 rounded w-24"></div>
      <div className="w-8 h-8 bg-slate-800 rounded-lg"></div>
    </div>
    <div className="h-7 bg-slate-800 rounded w-32 mb-2"></div>
    <div className="h-3 bg-slate-800 rounded w-40"></div>
  </div>
);

export const TableSkeleton = ({ rows = 5, cols = 6 }) => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden animate-pulse">
    <div className="p-4 border-b border-slate-800 flex justify-between items-center">
      <div className="h-4 bg-slate-800 rounded w-36"></div>
      <div className="h-8 bg-slate-800 rounded w-24"></div>
    </div>
    <div className="divide-y divide-slate-800">
      {Array.from({ length: rows }).map((_, rIdx) => (
        <div key={rIdx} className="p-4 flex items-center gap-4">
          {Array.from({ length: cols }).map((_, cIdx) => (
            <div key={cIdx} className="h-4 bg-slate-800 rounded flex-1"></div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

export const ChartSkeleton = () => (
  <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 h-72 animate-pulse flex flex-col justify-between">
    <div className="h-4 bg-slate-800 rounded w-40"></div>
    <div className="flex items-end justify-center gap-3 h-48">
      <div className="w-12 bg-slate-800 rounded-t h-24"></div>
      <div className="w-12 bg-slate-800 rounded-t h-40"></div>
      <div className="w-12 bg-slate-800 rounded-t h-32"></div>
      <div className="w-12 bg-slate-800 rounded-t h-16"></div>
    </div>
  </div>
);

export default CardSkeleton;
