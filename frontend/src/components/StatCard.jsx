import React from 'react';

const StatCard = ({ title, value, subtitle, icon: Icon, color = 'blue', trend = null, badge = null }) => {
  const colorMap = {
    blue: {
      border: 'border-slate-200/90 hover:border-blue-300',
      iconBg: 'bg-blue-600 text-white shadow-blue-500/20 shadow-md',
      valueColor: 'text-slate-900',
      accentBg: 'bg-blue-50/50'
    },
    amber: {
      border: 'border-slate-200/90 hover:border-amber-300',
      iconBg: 'bg-amber-500 text-white shadow-amber-500/20 shadow-md',
      valueColor: 'text-slate-900',
      accentBg: 'bg-amber-50/50'
    },
    emerald: {
      border: 'border-slate-200/90 hover:border-emerald-300',
      iconBg: 'bg-emerald-600 text-white shadow-emerald-500/20 shadow-md',
      valueColor: 'text-slate-900',
      accentBg: 'bg-emerald-50/50'
    },
    rose: {
      border: 'border-slate-200/90 hover:border-rose-300',
      iconBg: 'bg-rose-600 text-white shadow-rose-500/20 shadow-md',
      valueColor: 'text-slate-900',
      accentBg: 'bg-rose-50/50'
    },
    purple: {
      border: 'border-slate-200/90 hover:border-indigo-300',
      iconBg: 'bg-indigo-600 text-white shadow-indigo-500/20 shadow-md',
      valueColor: 'text-slate-900',
      accentBg: 'bg-indigo-50/50'
    }
  };

  const style = colorMap[color] || colorMap.blue;

  return (
    <div className={`bg-white rounded-2xl p-5 border ${style.border} shadow-2xs hover:shadow-md transition-all duration-200 flex flex-col justify-between`}>
      <div>
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              {title}
            </span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className={`text-2xl sm:text-3xl font-black tracking-tight ${style.valueColor}`}>
                {value}
              </span>
              {badge && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                  {badge}
                </span>
              )}
            </div>
          </div>

          {Icon && (
            <div className={`p-3 rounded-xl shrink-0 ${style.iconBg}`}>
              <Icon className="h-5 w-5" />
            </div>
          )}
        </div>

        {subtitle && (
          <p className="text-xs text-slate-500 font-medium mt-1.5 line-clamp-1">
            {subtitle}
          </p>
        )}
      </div>

      {trend && (
        <div className="mt-3.5 pt-3 border-t border-slate-100 text-xs flex items-center justify-between text-slate-600">
          <span className="text-slate-500 text-[11px]">{trend.label}</span>
          <span className="font-bold text-blue-700 text-xs bg-blue-50/80 px-2 py-0.5 rounded-md border border-blue-100/60">
            {trend.value}
          </span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
