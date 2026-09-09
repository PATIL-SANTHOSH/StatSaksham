import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { recommendationAPI, progressAPI } from '../services/api';
import CourseModal from '../components/CourseModal';
import { 
  GraduationCap, 
  Sparkles, 
  Clock, 
  Star, 
  ChevronDown, 
  Layers, 
  BookOpen, 
  Check, 
  ArrowRight,
  BarChart2,
  PieChart,
  Database,
  Cpu
} from 'lucide-react';

const LearningPath = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState(null);
  const [enrolledProgress, setEnrolledProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ALL');
  const [sortBy, setSortBy] = useState('Relevance');

  // Selected course for modal inspection
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchData = async () => {
    if (!user) return;
    try {
      const [recRes, progRes] = await Promise.all([
        recommendationAPI.getForEmployee(user.employee_id),
        progressAPI.getForEmployee(user.employee_id)
      ]);
      setRecommendations(recRes.data);
      setEnrolledProgress(progRes.data.recent_activities || []);
    } catch (err) {
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  const handleEnrollOrProgress = async (course) => {
    try {
      const payload = {
        employee_id: user.employee_id,
        course_type: course.course_type,
        course_id: course.course_id,
        title: course.title,
        provider: course.provider,
        competency_name: course.competency_name
      };
      await progressAPI.enrollOrUpdate(payload);
      await fetchData();
    } catch (err) {
      alert('Error updating learning progress.');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Synthesizing Recommended Learning Path...</p>
      </div>
    );
  }

  const allRecs = recommendations?.all_recommendations || [];
  const igotRecs = recommendations?.igot_recommendations || [];
  const nsstaRecs = recommendations?.nssta_recommendations || [];

  let displayList = [];
  if (activeTab === 'ALL') displayList = allRecs;
  else if (activeTab === 'iGOT') displayList = igotRecs;
  else if (activeTab === 'NSSTA') displayList = nsstaRecs;

  const enrolledCourseIds = new Set(enrolledProgress.map(p => p.course_id));
  const progressMap = {};
  enrolledProgress.forEach(p => {
    progressMap[p.course_id] = p;
  });

  const getCourseIcon = (title, type) => {
    if (title.toLowerCase().includes('python')) return <span className="font-mono font-bold text-xs text-yellow-600">Py</span>;
    if (title.toLowerCase().includes('survey') || title.toLowerCase().includes('sampling')) return <BarChart2 className="h-5 w-5 text-indigo-600" />;
    if (title.toLowerCase().includes('visualization') || title.toLowerCase().includes('power bi')) return <PieChart className="h-5 w-5 text-blue-600" />;
    if (title.toLowerCase().includes('national accounts')) return <Layers className="h-5 w-5 text-emerald-600" />;
    return <BookOpen className="h-5 w-5 text-slate-700" />;
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Course Modal */}
      <CourseModal
        course={selectedCourse}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedCourse(null);
        }}
        onEnroll={handleEnrollOrProgress}
        isEnrolled={selectedCourse ? enrolledCourseIds.has(selectedCourse.course_id) : false}
        isCompleted={selectedCourse && progressMap[selectedCourse.course_id]?.status === 'Completed'}
      />

      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
            Recommended Learning Path
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Based on your skill gaps, here are the most relevant courses from iGOT and NSSTA.
          </p>
        </div>

        {/* Sort By Dropdown */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400 font-semibold">Sort by:</span>
          <div className="bg-white border border-slate-200/90 rounded-xl px-3 py-1.5 font-bold text-slate-800 shadow-2xs flex items-center space-x-2">
            <span>{sortBy}</span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
          </div>
        </div>
      </div>

      {/* Tabs Row */}
      <div className="flex items-center space-x-6 border-b border-slate-200/90 text-xs font-bold text-slate-500">
        <button
          onClick={() => setActiveTab('ALL')}
          className={`pb-3 transition relative ${
            activeTab === 'ALL' ? 'text-blue-600' : 'hover:text-slate-900'
          }`}
        >
          <span>All</span>
          {activeTab === 'ALL' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
        </button>

        <button
          onClick={() => setActiveTab('iGOT')}
          className={`pb-3 transition relative ${
            activeTab === 'iGOT' ? 'text-blue-600' : 'hover:text-slate-900'
          }`}
        >
          <span>iGOT Courses</span>
          {activeTab === 'iGOT' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
        </button>

        <button
          onClick={() => setActiveTab('NSSTA')}
          className={`pb-3 transition relative ${
            activeTab === 'NSSTA' ? 'text-blue-600' : 'hover:text-slate-900'
          }`}
        >
          <span>NSSTA Training Programmes</span>
          {activeTab === 'NSSTA' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
        </button>

        <button
          onClick={() => setActiveTab('MY_LEARNING')}
          className={`pb-3 transition relative ${
            activeTab === 'MY_LEARNING' ? 'text-blue-600' : 'hover:text-slate-900'
          }`}
        >
          <span>My Learning Path ({enrolledProgress.length})</span>
          {activeTab === 'MY_LEARNING' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
        </button>
      </div>

      {/* View 1: My Learning Enrolled */}
      {activeTab === 'MY_LEARNING' ? (
        <div className="space-y-4">
          {enrolledProgress.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-3xl border border-slate-200/90 p-8 shadow-2xs">
              <BookOpen className="h-10 w-10 text-slate-400 mx-auto mb-2" />
              <h3 className="font-bold text-slate-800 text-sm">No courses enrolled yet</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Explore recommended iGOT or NSSTA modules and click 'View Details' to enroll.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {enrolledProgress.map((p) => (
                <div key={p.id} className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                        p.course_type === 'iGOT' ? 'bg-orange-100 text-orange-800' : 'bg-indigo-100 text-indigo-800'
                      }`}>
                        {p.course_type}
                      </span>
                      <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                        p.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {p.status} ({p.progress_percentage}%)
                      </span>
                    </div>

                    <h3 className="font-bold text-sm text-slate-900">{p.title}</h3>
                    <p className="text-xs text-slate-500 mt-1 font-medium">{p.provider} • {p.hours_spent}h Logged</p>

                    <div className="mt-3">
                      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-300 ${
                            p.status === 'Completed' ? 'bg-emerald-500' : 'bg-blue-600'
                          }`}
                          style={{ width: `${p.progress_percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="text-slate-500">
                      Target: <strong className="text-slate-700">{p.competency_name || 'Statistical Competency'}</strong>
                    </span>
                    {p.status !== 'Completed' ? (
                      <button
                        onClick={() => handleEnrollOrProgress(p)}
                        className="font-bold text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                      >
                        <span>Advance (+40%)</span>
                        <ArrowRight className="h-3 w-3" />
                      </button>
                    ) : (
                      <span className="text-emerald-700 font-bold flex items-center space-x-1">
                        <Check className="h-3.5 w-3.5" />
                        <span>Completed</span>
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* View 2: Recommended Course Cards List */
        <div className="space-y-4">
          {displayList.map((rec) => {
            const isDone = progressMap[rec.course_id]?.status === 'Completed';

            return (
              <div
                key={rec.id}
                className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs hover:shadow-xs transition flex flex-col md:flex-row md:items-center md:justify-between gap-4"
              >
                {/* Left: Thumbnail & Details */}
                <div className="flex items-start space-x-4">
                  <div className="h-12 w-12 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center shrink-0 shadow-2xs">
                    {getCourseIcon(rec.title, rec.course_type)}
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-extrabold text-sm text-slate-900 leading-snug">
                        {rec.title}
                      </h3>
                      {rec.course_type && (
                        <span className={`text-[9px] font-extrabold px-1.5 py-0.2 rounded uppercase ${
                          rec.course_type === 'iGOT' ? 'bg-orange-100 text-orange-800' : 'bg-indigo-100 text-indigo-800'
                        }`}>
                          {rec.course_type}
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-500 font-medium">
                      Provided by: <span className="text-slate-700 font-semibold">{rec.provider}</span>
                    </p>

                    <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-slate-500 font-medium">
                      <span className="flex items-center space-x-1">
                        <Clock className="h-3 w-3 text-slate-400" />
                        <span>{rec.estimated_duration}</span>
                      </span>
                      <span>•</span>
                      <span>{rec.priority === 'High' ? 'Intermediate' : 'Beginner'}</span>
                      <span>•</span>
                      <span className="text-blue-700 font-semibold">{rec.competency_name}</span>
                    </div>
                  </div>
                </div>

                {/* Right: Rating & View Details Button */}
                <div className="flex items-center justify-between md:justify-end space-x-4 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                  <div className="flex items-center space-x-1 text-xs font-bold text-slate-700">
                    <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                    <span>4.7</span>
                    <span className="text-[11px] text-slate-400 font-normal">(3.2k)</span>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedCourse(rec);
                      setIsModalOpen(true);
                    }}
                    className="px-4 py-2 bg-[#0C1E38] hover:bg-blue-900 text-white font-bold text-xs rounded-xl shadow-xs transition"
                  >
                    View Details
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default LearningPath;
