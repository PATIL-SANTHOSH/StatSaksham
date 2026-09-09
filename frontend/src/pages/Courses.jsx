import React, { useState, useEffect } from 'react';
import { courseAPI, progressAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import CourseModal from '../components/CourseModal';
import { 
  BookOpen, 
  Search, 
  Clock, 
  Star, 
  ChevronDown, 
  Layers, 
  Check, 
  ArrowRight,
  BarChart2,
  PieChart,
  Database,
  Cpu
} from 'lucide-react';

const Courses = () => {
  const { user } = useAuth();
  const [igotCourses, setIgotCourses] = useState([]);
  const [nsstaProgrammes, setNsstaProgrammes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [catalogueTab, setCatalogueTab] = useState('iGOT');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  // Modal inspection
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchCourses = async () => {
      setLoading(true);
      try {
        const [igotRes, nsstaRes] = await Promise.all([
          courseAPI.getIGOT(),
          courseAPI.getNSSTA()
        ]);
        setIgotCourses(igotRes.data);
        setNsstaProgrammes(nsstaRes.data);
      } catch (err) {
        console.error('Error fetching course catalogues:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCourses();
  }, []);

  const handleEnrollCourse = async (course) => {
    if (!user) return;
    try {
      const payload = {
        employee_id: user.employee_id,
        course_type: course.course_type,
        course_id: course.course_id || course.training_id,
        title: course.title,
        provider: course.provider,
        competency_name: course.category
      };
      await progressAPI.enrollOrUpdate(payload);
      alert(`Enrolled in "${course.title}".`);
    } catch (err) {
      alert('Error updating course enrollment.');
    }
  };

  const categories = ['All', 'Statistical', 'Technical', 'Digital Governance', 'Behavioural / Managerial'];
  const currentList = catalogueTab === 'iGOT' ? igotCourses : nsstaProgrammes;

  const filtered = currentList.filter((c) => {
    const matchCat = categoryFilter === 'All' || c.category === categoryFilter;
    const matchSearch = 
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.provider.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.competency_tags && c.competency_tags.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCat && matchSearch;
  });

  const getCourseIcon = (title) => {
    if (title.toLowerCase().includes('python')) return <span className="font-mono font-bold text-xs text-yellow-600">Py</span>;
    if (title.toLowerCase().includes('survey') || title.toLowerCase().includes('sampling')) return <BarChart2 className="h-5 w-5 text-indigo-600" />;
    if (title.toLowerCase().includes('visualization') || title.toLowerCase().includes('power bi')) return <PieChart className="h-5 w-5 text-blue-600" />;
    if (title.toLowerCase().includes('national accounts')) return <Layers className="h-5 w-5 text-emerald-600" />;
    return <BookOpen className="h-5 w-5 text-slate-700" />;
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Course Detail Modal */}
      <CourseModal
        course={selectedCourse}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedCourse(null);
        }}
        onEnroll={handleEnrollCourse}
      />

      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Training Courses</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Browse verified training modules from iGOT Karmayogi and NSSTA / TPAC.
          </p>
        </div>

        {/* Search input */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search courses or tags..."
            className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-200/90 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 shadow-2xs transition"
          />
        </div>
      </div>

      {/* Tabs Row */}
      <div className="flex items-center space-x-6 border-b border-slate-200/90 text-xs font-bold text-slate-500">
        <button
          onClick={() => setCatalogueTab('iGOT')}
          className={`pb-3 transition relative ${
            catalogueTab === 'iGOT' ? 'text-blue-600' : 'hover:text-slate-900'
          }`}
        >
          <span>iGOT Karmayogi ({igotCourses.length})</span>
          {catalogueTab === 'iGOT' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
        </button>

        <button
          onClick={() => setCatalogueTab('NSSTA')}
          className={`pb-3 transition relative ${
            catalogueTab === 'NSSTA' ? 'text-blue-600' : 'hover:text-slate-900'
          }`}
        >
          <span>NSSTA / TPAC Programmes ({nsstaProgrammes.length})</span>
          {catalogueTab === 'NSSTA' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />}
        </button>
      </div>

      {/* Category Filter Chips */}
      <div className="flex items-center space-x-2 overflow-x-auto text-xs pb-1">
        <span className="text-slate-400 font-bold text-[10px] uppercase">Domain:</span>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={`px-3 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition ${
              categoryFilter === cat
                ? 'bg-[#0C1E38] text-white font-bold shadow-2xs'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200/80'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Course List */}
      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-xs font-semibold text-slate-500 mt-2">Loading Course Catalogues...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs hover:shadow-xs transition flex flex-col md:flex-row md:items-center md:justify-between gap-4"
            >
              {/* Left: Icon & Info */}
              <div className="flex items-start space-x-4">
                <div className="h-12 w-12 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center shrink-0 shadow-2xs">
                  {getCourseIcon(item.title)}
                </div>

                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-extrabold text-sm text-slate-900 leading-snug">
                      {item.title}
                    </h3>
                    <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded uppercase bg-slate-100 text-slate-700 border border-slate-200">
                      {item.category}
                    </span>
                  </div>

                  <p className="text-xs text-slate-500 font-medium">
                    Provided by: <span className="text-slate-700 font-semibold">{item.provider}</span>
                  </p>

                  <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-slate-500 font-medium">
                    <span className="flex items-center space-x-1">
                      <Clock className="h-3 w-3 text-slate-400" />
                      <span>{item.duration_hours ? `${item.duration_hours} hours` : `${item.duration_days} Days`}</span>
                    </span>
                    <span>•</span>
                    <span className="text-blue-700 font-semibold">{item.competency_tags}</span>
                  </div>
                </div>
              </div>

              {/* Right: Rating & View Details */}
              <div className="flex items-center justify-between md:justify-end space-x-4 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                <div className="flex items-center space-x-1 text-xs font-bold text-slate-700">
                  <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                  <span>4.8</span>
                  <span className="text-[11px] text-slate-400 font-normal">(1.4k)</span>
                </div>

                <button
                  onClick={() => {
                    setSelectedCourse(item);
                    setIsModalOpen(true);
                  }}
                  className="px-4 py-2 bg-[#0C1E38] hover:bg-blue-900 text-white font-bold text-xs rounded-xl shadow-xs transition"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Courses;
