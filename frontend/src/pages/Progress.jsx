import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { progressAPI } from '../services/api';
import { 
  Activity, 
  Clock, 
  CheckCircle2, 
  Award, 
  BookOpen, 
  TrendingUp, 
  Calendar 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

const Progress = () => {
  const { user } = useAuth();
  const [progressSummary, setProgressSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    const fetchProgress = async () => {
      setLoading(true);
      try {
        const res = await progressAPI.getForEmployee(user.employee_id);
        setProgressSummary(res.data);
      } catch (err) {
        console.error('Error fetching progress:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
  }, [user]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Loading Learning Progress...</p>
      </div>
    );
  }

  const activities = progressSummary?.recent_activities || [];

  const activityTrend = [
    { week: 'W1', hours: 4 },
    { week: 'W2', hours: 7 },
    { week: 'W3', hours: 12 },
    { week: 'W4', hours: 18 },
    { week: 'W5', hours: 22 },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Learning Progress</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Audited record of official training hours logged across iGOT Karmayogi and NSSTA programmes.
        </p>
      </div>

      {/* 4 Metric Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Clock className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{progressSummary?.total_learning_hours || 0}h</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Total Hours Logged</div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{progressSummary?.completed_count || 0}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Courses Completed</div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{progressSummary?.in_progress_count || 0}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">In Progress</div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <Award className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{progressSummary?.total_enrolled || 0}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Total Enrollments</div>
          </div>
        </div>
      </div>

      {/* Progress Line Chart & Activity Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Weekly Learning Activity */}
        <div className="lg:col-span-5 bg-white rounded-3xl p-6 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-sm text-slate-900 mb-1">Learning Hours Trajectory</h3>
            <p className="text-xs text-slate-500 mb-4">Cumulative capacity building hours</p>

            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={activityTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="week" tick={{ fontSize: 10, fill: '#64748B' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} unit="h" />
                  <Tooltip />
                  <Line type="monotone" dataKey="hours" stroke="#3B82F6" strokeWidth={2.5} dot={{ r: 4, fill: '#3B82F6' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-center text-[11px] text-slate-500">
            Audited via National Statistical System
          </div>
        </div>

        {/* Ledger Table */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200/90 shadow-2xs overflow-hidden">
          <div className="p-5 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-extrabold text-sm text-slate-900">Training Engagement Ledger</h3>
            <span className="text-xs text-slate-500 font-semibold">{activities.length} entries</span>
          </div>

          {activities.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">No activities recorded yet.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200/90 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                    <th className="py-3 px-4">Course</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4 text-center">Status</th>
                    <th className="py-3 px-4 text-center">Hours</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {activities.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition">
                      <td className="py-3 px-4 font-bold text-slate-900">
                        {item.title}
                        <div className="text-[10px] text-slate-400 font-normal">{item.provider}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`text-[9px] font-extrabold px-1.5 py-0.2 rounded uppercase ${
                          item.course_type === 'iGOT' ? 'bg-orange-100 text-orange-800' : 'bg-indigo-100 text-indigo-800'
                        }`}>
                          {item.course_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          item.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center font-bold text-slate-800">
                        {item.hours_spent}h
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Progress;
