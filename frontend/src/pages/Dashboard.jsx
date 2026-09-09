import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  employeeAPI, 
  competencyAPI, 
  recommendationAPI, 
  progressAPI, 
  assessmentAPI 
} from '../services/api';
import CourseModal from '../components/CourseModal';
import { 
  FileCheck2, 
  BookOpen, 
  Activity, 
  Award, 
  TrendingUp, 
  ArrowRight, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  ChevronRight, 
  PieChart as PieIcon, 
  BarChart2,
  Calendar
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip 
} from 'recharts';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [skillGaps, setSkillGaps] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [progressSummary, setProgressSummary] = useState(null);
  const [assessments, setAssessments] = useState([]);

  // Selected course for modal inspection
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchDashboardData = async () => {
    if (!user) return;
    try {
      const [empRes, gapRes, recRes, progRes, assessRes] = await Promise.all([
        employeeAPI.getById(user.employee_id),
        competencyAPI.getSkillGaps(user.employee_id),
        recommendationAPI.getForEmployee(user.employee_id),
        progressAPI.getForEmployee(user.employee_id),
        assessmentAPI.list()
      ]);

      setProfile(empRes.data);
      setSkillGaps(gapRes.data);
      setRecommendations(recRes.data);
      setProgressSummary(progRes.data);
      setAssessments(assessRes.data);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const handleEnrollCourse = async (course) => {
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
      await fetchDashboardData();
    } catch (err) {
      alert('Error updating course enrollment.');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Loading Statistical Intelligence Dashboard...</p>
      </div>
    );
  }

  const firstName = profile?.name ? profile.name.split(' ')[0] : 'Officer';
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });

  const completedCount = progressSummary?.completed_count || 4;
  const inProgressCount = progressSummary?.in_progress_count || 2;
  const notStartedCount = 6;
  const totalCourses = completedCount + inProgressCount + notStartedCount;
  const progressPercent = Math.round((completedCount / totalCourses) * 100) || 45;

  const donutData = [
    { name: 'Completed', value: completedCount, color: '#10B981' },
    { name: 'In Progress', value: inProgressCount, color: '#3B82F6' },
    { name: 'Not Started', value: notStartedCount, color: '#E2E8F0' },
  ];

  const pendingAssessmentsCount = assessments?.length || 3;
  const recommendedCoursesCount = recommendations?.total_recommendations || 5;
  const skillsCount = skillGaps?.total_competencies || 12;

  const enrolledCourseIds = new Set(
    (progressSummary?.recent_activities || []).map(p => p.course_id)
  );

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
        onEnroll={handleEnrollCourse}
        isEnrolled={selectedCourse ? enrolledCourseIds.has(selectedCourse.course_id) : false}
      />

      {/* Top Greeting Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
            Good Morning, {firstName}! 👋
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-0.5">
            Keep learning, keep building a data-driven India.
          </p>
        </div>

        <div className="text-xs font-semibold text-slate-500 bg-white px-3.5 py-1.5 rounded-xl border border-slate-200/80 shadow-2xs w-fit">
          {currentDate}
        </div>
      </div>

      {/* Statistical Motivational Quote Banner Card */}
      <div className="bg-[#EEF4FF] border border-[#DCE7FC] rounded-2xl p-5 sm:p-6 flex items-center justify-between shadow-2xs">
        <div className="space-y-1">
          <p className="text-sm sm:text-base font-extrabold text-[#1E3A8A]">
            "Better data. Better decisions. A stronger nation."
          </p>
          <p className="text-xs text-blue-700/80 font-medium">
            National Statistical Cadre Capacity Building Initiative • MoSPI
          </p>
        </div>

        <div className="h-12 w-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center shadow-md shrink-0">
          <BarChart2 className="h-6 w-6 stroke-[2.5]" />
        </div>
      </div>

      {/* 4 Metric Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Card 1: Pending Assessments */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5 hover:shadow-xs transition">
          <div className="h-11 w-11 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <FileCheck2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{pendingAssessmentsCount}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Pending Assessments</div>
          </div>
        </div>

        {/* Card 2: Recommended Courses */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5 hover:shadow-xs transition">
          <div className="h-11 w-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{recommendedCoursesCount}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Recommended Courses</div>
          </div>
        </div>

        {/* Card 3: Ongoing Courses */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5 hover:shadow-xs transition">
          <div className="h-11 w-11 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{inProgressCount}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Ongoing Courses</div>
          </div>
        </div>

        {/* Card 4: Skills Identified */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/90 shadow-2xs flex items-center space-x-3.5 hover:shadow-xs transition">
          <div className="h-11 w-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
            <Award className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xl font-black text-slate-900">{skillsCount}</div>
            <div className="text-[11px] font-semibold text-slate-500 leading-tight">Skills Identified</div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Section: Learning Progress Donut + Upcoming Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Card: Your Learning Progress */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-extrabold text-sm text-slate-900">Your Learning Progress</h3>
            </div>

            <div className="flex items-center justify-around py-2">
              {/* Donut Chart */}
              <div className="relative h-36 w-36 shrink-0 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={donutData}
                      cx="50%"
                      cy="50%"
                      innerRadius={46}
                      outerRadius={62}
                      paddingAngle={3}
                      dataKey="value"
                      startAngle={90}
                      endAngle={-270}
                    >
                      {donutData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
                  <span className="text-xl font-black text-slate-900">{progressPercent}%</span>
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tight">Overall Progress</span>
                </div>
              </div>

              {/* Status Breakdown Legend */}
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between space-x-4">
                  <div className="flex items-center space-x-2">
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 shrink-0" />
                    <span className="text-slate-600 font-medium">Completed</span>
                  </div>
                  <span className="font-bold text-slate-900">{completedCount}</span>
                </div>

                <div className="flex items-center justify-between space-x-4">
                  <div className="flex items-center space-x-2">
                    <span className="h-2.5 w-2.5 rounded-full bg-blue-500 shrink-0" />
                    <span className="text-slate-600 font-medium">In Progress</span>
                  </div>
                  <span className="font-bold text-slate-900">{inProgressCount}</span>
                </div>

                <div className="flex items-center justify-between space-x-4">
                  <div className="flex items-center space-x-2">
                    <span className="h-2.5 w-2.5 rounded-full bg-slate-300 shrink-0" />
                    <span className="text-slate-600 font-medium">Not Started</span>
                  </div>
                  <span className="font-bold text-slate-900">{notStartedCount}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-center">
            <Link
              to="/progress"
              className="text-xs font-bold text-blue-600 hover:text-blue-800 transition inline-flex items-center space-x-1"
            >
              <span>View Details</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>

        {/* Right Card: Upcoming Tasks */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-extrabold text-sm text-slate-900">Upcoming Tasks</h3>
              <Link
                to="/learning-path"
                className="text-xs font-bold text-blue-600 hover:text-blue-800 transition"
              >
                View All
              </Link>
            </div>

            <div className="space-y-3">
              {/* Task 1: Quiz */}
              <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200/80 flex items-center justify-between hover:bg-slate-100/70 transition">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs shrink-0">
                    <FileCheck2 className="h-4 w-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-slate-900">Complete Python Basics Quiz</h4>
                    <p className="text-[11px] text-slate-500">Due: 8 Sept 2026</p>
                  </div>
                </div>
                <Link
                  to="/quiz"
                  className="px-3 py-1 bg-white hover:bg-blue-600 hover:text-white text-blue-600 border border-blue-200 font-bold text-[11px] rounded-lg transition shadow-2xs"
                >
                  Quiz
                </Link>
              </div>

              {/* Task 2: Course */}
              <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200/80 flex items-center justify-between hover:bg-slate-100/70 transition">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs shrink-0">
                    <BookOpen className="h-4 w-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-slate-900">Finish Data Visualization Module</h4>
                    <p className="text-[11px] text-slate-500">Due: 10 Sept 2026</p>
                  </div>
                </div>
                <Link
                  to="/learning-path"
                  className="px-3 py-1 bg-white hover:bg-emerald-600 hover:text-white text-emerald-700 border border-emerald-200 font-bold text-[11px] rounded-lg transition shadow-2xs"
                >
                  Course
                </Link>
              </div>

              {/* Task 3: Assessment */}
              <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200/80 flex items-center justify-between hover:bg-slate-100/70 transition">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-xs shrink-0">
                    <Award className="h-4 w-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-slate-900">Take Competency Assessment</h4>
                    <p className="text-[11px] text-slate-500">Due: 12 Sept 2026</p>
                  </div>
                </div>
                <Link
                  to="/assessment"
                  className="px-3 py-1 bg-white hover:bg-purple-600 hover:text-white text-purple-700 border border-purple-200 font-bold text-[11px] rounded-lg transition shadow-2xs"
                >
                  Assessment
                </Link>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-right">
            <span className="text-[11px] text-slate-500 font-medium">Synced with National Accounts Division Goals</span>
          </div>
        </div>
      </div>

      {/* Recommended Learning Courses Row */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-sm text-slate-900">Recommended Learning</h3>
            <p className="text-xs text-slate-500">Personalized capacity building modules from iGOT & NSSTA</p>
          </div>
          <Link
            to="/learning-path"
            className="text-xs font-bold text-blue-600 hover:text-blue-800 transition flex items-center space-x-1"
          >
            <span>View All</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(recommendations?.all_recommendations?.slice(0, 3) || []).map((rec) => (
            <div
              key={rec.id}
              className="p-4 bg-slate-50/80 rounded-2xl border border-slate-200/80 flex flex-col justify-between hover:shadow-xs transition"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded ${
                    rec.course_type === 'iGOT' 
                      ? 'bg-orange-100 text-orange-800' 
                      : 'bg-indigo-100 text-indigo-800'
                  }`}>
                    {rec.course_type}
                  </span>
                  <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                    {rec.relevance_score}% Match
                  </span>
                </div>

                <h4 className="font-bold text-xs sm:text-sm text-slate-900 line-clamp-2">
                  {rec.title}
                </h4>
                <p className="text-[11px] text-slate-500 mt-1 font-medium">{rec.provider} • {rec.estimated_duration}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-200/80 flex items-center justify-between">
                <span className="text-[11px] font-bold text-blue-700 truncate max-w-[150px]">
                  {rec.competency_name}
                </span>
                <button
                  onClick={() => {
                    setSelectedCourse(rec);
                    setIsModalOpen(true);
                  }}
                  className="px-3 py-1 bg-[#0C1E38] hover:bg-blue-900 text-white font-bold text-xs rounded-lg transition"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
