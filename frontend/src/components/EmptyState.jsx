import React from 'react';
import { Search, Info, RotateCcw } from 'lucide-react';

const EmptyState = ({ 
  icon: Icon = Info, 
  title = 'No records found', 
  description = 'Try adjusting your search query or filters.',
  actionLabel = null,
  onAction = null
}) => {
  return (
    <div className="text-center py-12 px-4 bg-white rounded-2xl border border-slate-200 shadow-2xs max-w-md mx-auto my-6">
      <div className="h-12 w-12 rounded-2xl bg-slate-100 text-slate-500 mx-auto flex items-center justify-center mb-3">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="font-bold text-slate-800 text-sm">{title}</h3>
      <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-4 inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg transition"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>{actionLabel}</span>
        </button>
      )}
    </div>
  );
};

export default EmptyState;
