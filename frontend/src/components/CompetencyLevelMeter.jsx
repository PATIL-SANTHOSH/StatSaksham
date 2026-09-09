import React from 'react';

const levelNames = ['', 'Beginner (L1)', 'Basic (L2)', 'Intermediate (L3)', 'Advanced (L4)', 'Expert (L5)'];

const CompetencyLevelMeter = ({ level = 1, requiredLevel = null, showLabel = true, size = 'md' }) => {
  const safeLevel = Math.max(0, Math.min(5, level));
  const safeRequired = requiredLevel ? Math.max(1, Math.min(5, requiredLevel)) : null;

  const barHeights = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-3.5'
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center space-x-1.5">
        {[1, 2, 3, 4, 5].map((i) => {
          const isFilled = i <= safeLevel;
          const isRequiredTarget = safeRequired && i === safeRequired;
          
          let bgColor = 'bg-slate-200/80';
          if (isFilled) {
            if (safeLevel >= 4) bgColor = 'bg-emerald-600 shadow-2xs';
            else if (safeLevel === 3) bgColor = 'bg-blue-600 shadow-2xs';
            else if (safeLevel === 2) bgColor = 'bg-amber-500 shadow-2xs';
            else bgColor = 'bg-rose-500 shadow-2xs';
          }

          return (
            <div
              key={i}
              className={`flex-1 rounded-sm ${barHeights[size]} ${bgColor} transition-all duration-300 relative`}
              title={`Level ${i}: ${levelNames[i]}`}
            >
              {isRequiredTarget && (
                <div 
                  className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-slate-900 ring-2 ring-white shadow-xs" 
                  title={`Required Cadre Target: Level ${safeRequired}`}
                />
              )}
            </div>
          );
        })}
      </div>
      {showLabel && (
        <div className="flex items-center justify-between text-[11px]">
          <span className="font-bold text-slate-800">
            {levelNames[safeLevel] || `Level ${safeLevel}/5`}
          </span>
          {safeRequired && (
            <span className="text-[10px] font-semibold text-slate-500">
              Required: <strong className="text-slate-700">L{safeRequired}</strong>
              {safeLevel >= safeRequired ? (
                <span className="text-emerald-600 font-bold ml-1">✓ Met</span>
              ) : (
                <span className="text-rose-600 font-bold ml-1">(-{safeRequired - safeLevel})</span>
              )}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default CompetencyLevelMeter;
