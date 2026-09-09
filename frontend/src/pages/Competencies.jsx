import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { competencyAPI } from '../services/api';
import CompetencyLevelMeter from '../components/CompetencyLevelMeter';
import EmptyState from '../components/EmptyState';
import { 
  Award, 
  CheckCircle2, 
  Clock, 
  FileCheck2, 
  Search, 
  Filter, 
  ArrowRight, 
  Info,
  ShieldCheck,
  TrendingUp,
  Layers
} from 'lucide-react';

const Competencies = () => {
  const { user } = useAuth();
  const [competencies, setCompetencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (!user) return;
    const fetchCompetencies = async () => {
      setLoading(true);
      try {
        const res = await competencyAPI.getEmployeeCompetencies(user.employee_id);
        setCompetencies(res.data);
      } catch (err) {
        console.error('Error fetching employee competencies:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCompetencies();
  }, [user]);

  const categories = ['All', 'Statistical', 'Technical', 'Digital Governance', 'Behavioural / Managerial'];

  const filtered = competencies.filter((c) => {
    const matchCategory = selectedCategory === 'All' || c.category === selectedCategory;
    const matchSearch = 
      c.competency_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.domain && c.domain.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCategory && matchSearch;
  });

  const totalCount = competencies.length;
  const verifiedCount = competencies.filter(c => c.verified_by_assessment).length;
  const avgLevel = totalCount > 0 
    ? (competencies.reduce((acc, c) => acc + c.current_level, 0) / totalCount).toFixed(1) 
    : 0;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 text-xs font-bold px-2.5 py-1 rounded-md border border-blue-200 mb-2">
            <Award className="h-3.5 w-3.5" />
            <span>National Statistical Competency Framework</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900">My Competency Profile</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time evaluation across Statistical, Technical, Governance, and Behavioural domains on a standardized 1–5 scale.
          </p>
        </div>

        <Link
          to="/assessment"
          className="inline-flex items-center space-x-2 bg-gov-navy hover:bg-blue-900 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow transition shrink-0"
        >
          <FileCheck2 className="h-4 w-4 text-emerald-400" />
          <span>Launch Competency Assessment</span>
        </Link>
      </div>

      {/* Summary Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-2xs">
          <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Assessed Competencies</span>
          <span className="text-2xl font-black text-slate-900 mt-1 block">{totalCount} Domains</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Full MoSPI standard framework</span>
        </div>
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-2xs">
          <span className="text-[10px] text-emerald-600 font-bold uppercase block">Assessment Verified</span>
          <span className="text-2xl font-black text-emerald-700 mt-1 block">{verifiedCount} Certified</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Standardized MCQ verified</span>
        </div>
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-2xs">
          <span className="text-[10px] text-blue-600 font-bold uppercase block">Average Proficiency</span>
          <span className="text-2xl font-black text-blue-700 mt-1 block">Level {avgLevel} / 5</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Role cadre average</span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0 text-xs">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl font-bold whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-gov-navy text-white shadow-xs'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search competencies, methods..."
            className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-600 focus:outline-none"
          />
        </div>
      </div>

      {/* Competencies Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gov-navy"></div>
          <p className="text-xs text-slate-500 mt-2 font-semibold">Loading Competency Metrics...</p>
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No competencies found"
          description="No competency standards match your active category and search filter."
          actionLabel="Reset Search & Filters"
          onAction={() => {
            setSelectedCategory('All');
            setSearchQuery('');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((comp) => (
            <div
              key={comp.id}
              className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between hover:shadow-md hover:border-blue-300 transition-all duration-200"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="text-[10px] font-extrabold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                      {comp.category}
                    </span>
                    <h3 className="font-bold text-sm text-slate-900 mt-1.5 leading-snug">
                      {comp.competency_name}
                    </h3>
                  </div>
                  {comp.verified_by_assessment ? (
                    <span className="inline-flex items-center space-x-1 text-[10px] font-bold bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full border border-emerald-200 shrink-0">
                      <ShieldCheck className="h-3 w-3 text-emerald-600" />
                      <span>Verified</span>
                    </span>
                  ) : (
                    <span className="text-[10px] font-semibold bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full shrink-0">
                      Profile
                    </span>
                  )}
                </div>

                <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                  {comp.description || `Assessment and operational standards for ${comp.competency_name} in official statistical duties.`}
                </p>

                <div className="mt-4 p-3 bg-slate-50/80 rounded-xl border border-slate-200/70">
                  <CompetencyLevelMeter
                    level={comp.current_level}
                    size="md"
                    showLabel={true}
                  />
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="text-slate-400 flex items-center space-x-1 text-[10px]">
                  <Clock className="h-3 w-3" />
                  <span>Source: {comp.source}</span>
                </span>
                <Link
                  to="/assessment"
                  className="font-bold text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                >
                  <span>Assess</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Competencies;
