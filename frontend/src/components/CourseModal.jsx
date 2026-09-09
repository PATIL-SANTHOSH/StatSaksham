import React, { useState } from 'react';
import { 
  X, 
  ArrowLeft, 
  Star, 
  Clock, 
  GraduationCap, 
  Globe, 
  Check, 
  CheckCircle2, 
  ArrowRight,
  Sparkles,
  BookOpen,
  Layers,
  Award
} from 'lucide-react';

const CourseModal = ({ course, isOpen, onClose, onEnroll, isEnrolled, isCompleted }) => {
  const [activeTab, setActiveTab] = useState('Overview');

  if (!isOpen || !course) return null;

  const isIgot = course.course_type === 'iGOT';
  const skills = (course.competency_tags || 'Python, Data Analysis, Pandas, Data Visualization, NumPy, Matplotlib, Sampling, Official Statistics').split(',');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs transition-opacity animate-in fade-in duration-150">
      <div 
        className="relative w-full max-w-3xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Bar */}
        <div className="px-6 py-3 bg-white border-b border-slate-200 flex items-center justify-between">
          <button
            onClick={onClose}
            className="flex items-center space-x-1.5 text-xs font-bold text-slate-600 hover:text-slate-900 transition"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Courses</span>
          </button>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-700">
          {/* Dark Navy Hero Header Banner Card */}
          <div className="bg-[#0C1E38] text-white rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 shadow-md">
            <div className="flex items-start space-x-4">
              {/* Icon Box */}
              <div className="h-14 w-14 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 font-mono font-bold text-lg text-yellow-400 shadow-inner">
                {course.title.toLowerCase().includes('python') ? 'Py' : <BookOpen className="h-7 w-7 text-blue-400" />}
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center space-x-2">
                  <h2 className="text-lg font-extrabold text-white tracking-tight">
                    {course.title}
                  </h2>
                  <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded uppercase ${
                    isIgot ? 'bg-orange-500/30 text-orange-300 border border-orange-400/30' : 'bg-indigo-500/30 text-indigo-300 border border-indigo-400/30'
                  }`}>
                    {course.course_type}
                  </span>
                </div>

                <p className="text-xs text-slate-300 font-medium">
                  Provided by: <span className="text-white font-semibold">{course.provider}</span>
                </p>

                <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-slate-300">
                  <span className="flex items-center space-x-1 text-amber-300 font-bold">
                    <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                    <span>4.7</span>
                    <span className="text-slate-400 font-normal">(3.2k learners)</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span>{course.estimated_duration || '10 hours'}</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <GraduationCap className="h-3 w-3 text-slate-400" />
                    <span>Beginner</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <Globe className="h-3 w-3 text-slate-400" />
                    <span>English / Hindi</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Enroll / Completed Button on Right of Hero */}
            <div className="shrink-0">
              {isCompleted ? (
                <div className="px-4 py-2.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-xl font-bold text-xs flex items-center space-x-1.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span>Completed</span>
                </div>
              ) : onEnroll ? (
                <button
                  onClick={() => {
                    onEnroll(course);
                    onClose();
                  }}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow transition flex items-center space-x-1.5"
                >
                  <span>{isEnrolled ? 'Advance Progress (+40%)' : 'Enroll Now'}</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              ) : null}
            </div>
          </div>

          {/* Modal Tabs */}
          <div className="flex items-center space-x-6 border-b border-slate-200 text-xs font-bold text-slate-500">
            {['Overview', 'Modules', 'Learning Outcomes', 'Reviews'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-2.5 transition relative ${
                  activeTab === tab ? 'text-blue-600' : 'hover:text-slate-900'
                }`}
              >
                <span>{tab}</span>
                {activeTab === tab && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
              </button>
            ))}
          </div>

          {/* Tab Content: Overview */}
          {activeTab === 'Overview' && (
            <div className="space-y-5">
              <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
                {course.description || "This course introduces the fundamentals of statistical analysis and programming, covering data manipulation, visualization, and real-world applications in government data systems."}
              </p>

              {course.reason && (
                <div className="p-3.5 bg-blue-50/80 border border-blue-200 rounded-xl space-y-1">
                  <div className="flex items-center space-x-1.5 text-blue-900 font-bold text-[11px] uppercase tracking-wide">
                    <Sparkles className="h-3.5 w-3.5 text-blue-600" />
                    <span>Why Recommended for Your Cadre:</span>
                  </div>
                  <p className="text-slate-700 text-xs leading-relaxed">{course.reason}</p>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2">
                {/* Key Highlights */}
                <div>
                  <h3 className="font-extrabold text-sm text-slate-900 mb-3">Key Highlights</h3>
                  <div className="space-y-2 text-xs text-slate-700">
                    <div className="flex items-center space-x-2">
                      <div className="h-4 w-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                        <Check className="h-3 w-3" />
                      </div>
                      <span className="font-medium">Hands-on exercises with survey microdata</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="h-4 w-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                        <Check className="h-3 w-3" />
                      </div>
                      <span className="font-medium">Real-world government use cases (MoSPI)</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="h-4 w-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                        <Check className="h-3 w-3" />
                      </div>
                      <span className="font-medium">Aligned with official statistics domain</span>
                    </div>
                  </div>
                </div>

                {/* Skills Covered */}
                <div>
                  <h3 className="font-extrabold text-sm text-slate-900 mb-3">Skills Covered</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 bg-slate-100 text-slate-700 font-semibold rounded-lg text-[11px] border border-slate-200"
                      >
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content: Modules */}
          {activeTab === 'Modules' && (
            <div className="space-y-3">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-900">Module 1: Foundations of Official Statistical Systems</div>
                  <div className="text-[11px] text-slate-500">Overview of SNA, CPI, PLFS, and ASI frameworks</div>
                </div>
                <span className="text-[11px] font-bold text-slate-500">2.5 hours</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-900">Module 2: Practical Data Pipelines & Validation</div>
                  <div className="text-[11px] text-slate-500">Data cleaning, unit-level microdata, aggregation scripts</div>
                </div>
                <span className="text-[11px] font-bold text-slate-500">4.0 hours</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-slate-900">Module 3: Visual Dashboards & Dissemination</div>
                  <div className="text-[11px] text-slate-500">Building reports and automated indicators</div>
                </div>
                <span className="text-[11px] font-bold text-slate-500">3.5 hours</span>
              </div>
            </div>
          )}

          {/* Tab Content: Outcomes */}
          {activeTab === 'Learning Outcomes' && (
            <div className="space-y-2.5 text-xs text-slate-700">
              <p>By the conclusion of this training module, officials will be certified to:</p>
              <ul className="list-disc list-inside space-y-1 text-slate-600">
                <li>Execute automated Python/R scripts for national sample survey data validation.</li>
                <li>Implement standardized statistical classification standards (NIC, NCO).</li>
                <li>Meet MoSPI cadre competency benchmarks at certified Level 3+ proficiency.</li>
              </ul>
            </div>
          )}

          {/* Tab Content: Reviews */}
          {activeTab === 'Reviews' && (
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900">Statistical Officer, PSD</span>
                  <div className="flex text-amber-400">★★★★★</div>
                </div>
                <p className="text-slate-600 mt-1">Excellent government-focused dataset examples. Highly recommended for all cadre officers.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseModal;
