import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { 
  Users, 
  UserCheck, 
  BookOpen, 
  TrendingUp, 
  ChevronDown, 
  BarChart2, 
  PieChart as PieIcon, 
  Layers,
  Activity,
  Award
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell, 
  LineChart, 
  Line, 
  CartesianGrid 
} from 'recharts';

const AdminDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('Last 6 Months');

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const res = await adminAPI.getAnalytics();
        setAnalytics(res.data);
      } catch (err) {
        console.error('Error fetching admin analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Loading Workforce Analytics...</p>
      </div>
    );
  }

  // Competency Distribution Data (Matching reference bar chart)
  const competencyDistData = [
    { name: 'Statistical', count: 85 },
    { name: 'Data Mgmt', count: 62 },
    { name: 'IT & AI', count: 74 },
    { name: 'Economics', count: 53 },
    { name: 'Visualization', count: 68 },
    { name: 'Policy', count: 42 },
  ];

  // Learning Source Donut Data (Matching reference donut chart)
  const learningSourceData = [
    { name: 'iGOT Courses', value: 60, color: '#3B82F6' },
    { name: 'NSSTA Programmes', value: 30, color: '#10B981' },
    { name: 'Others', value: 10, color: '#F59E0B' },
  ];

  // Training Effectiveness Trend Data (Matching reference line chart)
  const effectivenessData = [
    { month: 'Jan', gain: 12 },
    { month: 'Feb', gain: 18 },
    { month: 'Mar', gain: 22 },
    { month: 'Apr', gain: 26 },
    { month: 'May', gain: 29 },
    { month: 'Jun', gain: 32 },
  ];

  const totalEmployees = analytics?.total_employees || 248;
  const activeLearners = analytics?.active_employees || 187;
  const coursesCompleted = analytics?.courses_completed_count || 1024;
  const avgGain = '+32%';

  const topGaps = [
    { name: 'R Programming', pct: 68 },
    { name: 'GIS Mapping & Spatial Statistics', pct: 52 },
    { name: 'Advanced Statistical Modelling', pct: 47 },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Admin Dashboard</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Overview of employee learning and competency development.
          </p>
        </div>

        {/* Timeframe selector */}
        <div className="bg-white border border-slate-200/90 rounded-xl px-3 py-1.5 font-bold text-xs text-slate-800 shadow-2xs flex items-center space-x-2 w-fit">
          <span>{timeframe}</span>
          <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
        </div>
      </div>

      {/* 4 Metric Cards Row (Matching Reference) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Card 1: Total Employees */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{totalEmployees}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Total Employees</div>
          </div>
        </div>

        {/* Card 2: Active Learners */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{activeLearners}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Active Learners</div>
          </div>
        </div>

        {/* Card 3: Courses Completed */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{coursesCompleted.toLocaleString()}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Courses Completed</div>
          </div>
        </div>

        {/* Card 4: Average Skill Gain */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
            <TrendingUp className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{avgGain}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Average Skill Gain</div>
          </div>
        </div>
      </div>

      {/* Middle Row: Competency Distribution Bar Chart + Learning Source Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Competency Distribution Bar Chart */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs">
          <h3 className="font-extrabold text-sm text-slate-900 mb-1">Competency Distribution</h3>
          <p className="text-[11px] text-slate-500 mb-4">Personnel proficiency distribution across core domains</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={competencyDistData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748B' }} />
                <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Learning Source Donut Chart */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-sm text-slate-900 mb-1">Learning Source</h3>
            <p className="text-[11px] text-slate-500 mb-2">Training provider distribution across workforce</p>

            <div className="flex items-center justify-around py-2">
              <div className="relative h-36 w-36 shrink-0 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={learningSourceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={46}
                      outerRadius={62}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {learningSourceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
                  <span className="text-xl font-black text-slate-900">{totalEmployees}</span>
                  <span className="text-[9px] font-bold text-slate-400 uppercase">Total Learners</span>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                {learningSourceData.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between space-x-4">
                    <div className="flex items-center space-x-2">
                      <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                      <span className="text-slate-600 font-medium text-[11px]">{item.name}</span>
                    </div>
                    <span className="font-bold text-slate-900 text-xs">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-center text-[11px] text-slate-500 font-medium">
            Synced with iGOT & NSSTA Integration Adapters
          </div>
        </div>
      </div>

      {/* Bottom Row: Top Skill Gaps + Training Effectiveness Curve */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top Skill Gaps */}
        <div className="lg:col-span-6 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-sm text-slate-900 mb-1">Top Skill Gaps</h3>
            <p className="text-[11px] text-slate-500 mb-4">Key competency gaps across all statistical divisions</p>

            <div className="space-y-4">
              {topGaps.map((gap, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800">{idx + 1}. {gap.name}</span>
                    <span className="font-black text-rose-600">{gap.pct}%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-rose-500 rounded-full"
                      style={{ width: `${gap.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 text-right">
            <span className="text-[11px] text-blue-600 font-bold">Automated Capacity Recommendations Active</span>
          </div>
        </div>

        {/* Training Effectiveness Line Chart */}
        <div className="lg:col-span-6 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-extrabold text-sm text-slate-900">Training Effectiveness</h3>
              <span className="text-xs font-black text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                +32% skill improvement
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mb-4">Cumulative competency improvement trajectory</p>

            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={effectivenessData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                  <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#64748B' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
                  <Tooltip />
                  <Line type="monotone" dataKey="gain" stroke="#3B82F6" strokeWidth={2.5} dot={{ r: 4, fill: '#3B82F6' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-center text-[11px] text-slate-500 font-medium">
            Continuous evaluation post-assessment
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
