import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Minus } from 'lucide-react';

const SkillGapBadge = ({ priority = 'Medium', gap = 0, size = 'sm' }) => {
  if (gap === 0 || priority === 'None') {
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
        <span>Benchmark Met</span>
      </span>
    );
  }

  const badgeConfig = {
    High: {
      bg: 'bg-rose-50 text-rose-700 border-rose-200 ring-1 ring-rose-500/10',
      icon: AlertCircle,
      iconColor: 'text-rose-600',
      label: 'High Priority'
    },
    Medium: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200 ring-1 ring-amber-500/10',
      icon: AlertTriangle,
      iconColor: 'text-amber-600',
      label: 'Medium Priority'
    },
    Low: {
      bg: 'bg-blue-50 text-blue-700 border-blue-200 ring-1 ring-blue-500/10',
      icon: Minus,
      iconColor: 'text-blue-600',
      label: 'Low Priority'
    }
  };

  const config = badgeConfig[priority] || badgeConfig.Medium;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${config.bg}`}>
      <Icon className={`h-3 w-3 ${config.iconColor}`} />
      <span>{config.label} (Gap: {gap})</span>
    </span>
  );
};

export default SkillGapBadge;
