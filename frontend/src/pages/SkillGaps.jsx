import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { competencyAPI } from '../services/api';
import { 
  TrendingDown, 
  Lightbulb, 
  ArrowRight, 
  ChevronDown,
  CheckCircle2
} from 'lucide-react';

const SkillGaps = () => {
  const { user } = useAuth();
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    const fetchGaps = async () => {
      setLoading(true);
      try {
        const res = await competencyAPI.getSkillGaps(user.employee_id);
        setGapData(res.data);
      } catch (err) {
        console.error('Error fetching skill gaps:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchGaps();
  }, [user]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Loading Skill Gap Matrix...</p>
      </div>
    );
  }

  const allGaps = gapData?.gaps || [];

  // Top focus competencies for key insight
  const highGaps = allGaps.filter(g => g.gap > 0).slice(0, 3).map(g => g.competency_name);
  const keyInsightText = highGaps.length > 0 
    ? `Focus on improving ${highGaps.join(', ')} to align with your role requirements.`
    : "Your competencies currently meet or exceed all role requirements.";

  return (
    <div className="space-y-6 pb-12">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Skill Gap Analysis</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Here's a comparison of your current skills vs. required skills for your role.
          </p>
        </div>

        {/* Role Selector */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400 font-semibold">Your Role:</span>
          <div className="bg-white border border-slate-200/90 rounded-xl px-3 py-1.5 font-bold text-slate-800 shadow-2xs flex items-center space-x-2">
            <span>{gapData?.job_role || 'Statistical Officer'}</span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
          </div>
        </div>
      </div>

      {/* Comparison Table / Matrix Card */}
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-200/90 text-slate-400 font-bold uppercase tracking-wider text-[11px]">
                <th className="py-4 px-6 w-1/4">Competency</th>
                <th className="py-4 px-6 w-1/3">Current Level</th>
                <th className="py-4 px-6 w-1/3">Required Level</th>
                <th className="py-4 px-6 text-center w-24">Gap</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {allGaps.map((item) => {
                const currentWidth = (item.current_level / 5) * 100;
                const reqWidth = (item.required_level / 5) * 100;

                return (
                  <tr key={item.competency_id} className="hover:bg-slate-50/70 transition">
                    {/* Competency Name */}
                    <td className="py-4 px-6 font-bold text-slate-900 text-xs sm:text-sm">
                      {item.competency_name}
                    </td>

                    {/* Current Level Horizontal Bar */}
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        <div className="h-2 flex-1 max-w-[140px] bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600 rounded-full transition-all duration-300"
                            style={{ width: `${currentWidth}%` }}
                          />
                        </div>
                        <span className="font-semibold text-slate-500 text-[11px] w-8">
                          {item.current_level}/5
                        </span>
                      </div>
                    </td>

                    {/* Required Level Horizontal Bar */}
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        <div className="h-2 flex-1 max-w-[140px] bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-slate-300 rounded-full"
                            style={{ width: `${reqWidth}%` }}
                          />
                        </div>
                        <span className="font-semibold text-slate-500 text-[11px] w-8">
                          {item.required_level}/5
                        </span>
                      </div>
                    </td>

                    {/* Gap Number Badge */}
                    <td className="py-4 px-6 text-center">
                      {item.gap > 0 ? (
                        <span className={`inline-flex items-center justify-center h-6 min-w-6 px-2 rounded-full font-black text-xs ${
                          item.gap >= 2 ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                        }`}>
                          {item.gap}
                        </span>
                      ) : (
                        <span className="inline-flex items-center justify-center h-6 min-w-6 px-2 rounded-full font-bold text-xs bg-emerald-100 text-emerald-700">
                          0
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Insight Bottom Callout Card */}
      <div className="bg-[#FFFBEB] border border-[#FEE3A2] rounded-2xl p-4 sm:p-5 flex items-start space-x-3.5 shadow-2xs">
        <div className="h-9 w-9 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0 mt-0.5">
          <Lightbulb className="h-5 w-5 fill-amber-500 text-amber-500" />
        </div>
        <div className="space-y-0.5">
          <h4 className="font-black text-sm text-slate-900">Key Insight</h4>
          <p className="text-xs text-slate-700 font-medium leading-relaxed">
            {keyInsightText}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SkillGaps;
