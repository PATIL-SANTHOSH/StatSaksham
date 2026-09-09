import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { assessmentAPI } from '../services/api';
import { 
  BarChart2, 
  Database, 
  Cpu, 
  TrendingUp, 
  PieChart, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  ArrowRight, 
  ArrowLeft, 
  RotateCcw, 
  Sparkles,
  Award
} from 'lucide-react';

const Assessment = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [step, setStep] = useState(1); // 1: Select Domain, 2: Take Assessment, 3: View Results
  const [selectedDomain, setSelectedDomain] = useState('Statistical Methods');
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  // Active assessment runner state
  const [activeAssessment, setActiveAssessment] = useState(null);
  const [assessmentDetail, setAssessmentDetail] = useState(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(600); // 10 mins in seconds

  useEffect(() => {
    const fetchAssessments = async () => {
      setLoading(true);
      try {
        const res = await assessmentAPI.list();
        setAssessments(res.data);
      } catch (err) {
        console.error('Error fetching assessments:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAssessments();
  }, []);

  // Timer countdown
  useEffect(() => {
    if (step !== 2 || !activeAssessment || result) return;
    const interval = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [step, activeAssessment, result]);

  const domainCards = [
    {
      id: 'Statistical Methods',
      title: 'Statistical Methods',
      description: 'Descriptive & inferential statistics, sampling, survey design',
      icon: BarChart2,
      categoryMatch: 'Statistical'
    },
    {
      id: 'Data Management',
      title: 'Data Management',
      description: 'Data cleaning, databases, metadata, data governance',
      icon: Database,
      categoryMatch: 'Technical'
    },
    {
      id: 'IT & Emerging Technologies',
      title: 'IT & Emerging Technologies',
      description: 'AI/ML, Big Data, Cloud, GIS, Python, R',
      icon: Cpu,
      categoryMatch: 'Technical'
    },
    {
      id: 'Economics & National Accounts',
      title: 'Economics & National Accounts',
      description: 'Macroeconomics, National Accounts, Economic Indicators',
      icon: TrendingUp,
      categoryMatch: 'Statistical'
    },
    {
      id: 'Data Visualization',
      title: 'Data Visualization',
      description: 'Charts, dashboards, GIS visualization, Power BI',
      icon: PieChart,
      categoryMatch: 'Technical'
    },
    {
      id: 'Policy & Governance',
      title: 'Policy & Governance',
      description: 'Data for policy, SDGs, evidence-based decision-making',
      icon: ShieldCheck,
      categoryMatch: 'Digital Governance'
    }
  ];

  const handleProceedToQuestions = async () => {
    const domainObj = domainCards.find(d => d.id === selectedDomain);
    const matchedAssessment = assessments.find(a => 
      a.category === domainObj?.categoryMatch || 
      a.title.toLowerCase().includes(selectedDomain.toLowerCase())
    ) || assessments[0];

    if (!matchedAssessment) {
      alert('No assessment available for selected domain.');
      return;
    }

    try {
      const res = await assessmentAPI.getById(matchedAssessment.id);
      setAssessmentDetail(res.data);
      setActiveAssessment(matchedAssessment);
      setCurrentQIndex(0);
      setAnswers({});
      setResult(null);
      setTimeLeft((matchedAssessment.time_limit_minutes || 10) * 60);
      setStep(2);
    } catch (err) {
      alert('Failed to load assessment questions.');
    }
  };

  const handleSelectOption = (questionId, optionLetter) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionLetter
    }));
  };

  const handleSubmit = async () => {
    if (!assessmentDetail) return;
    setSubmitting(true);
    try {
      const submitPayload = {
        employee_id: user.employee_id,
        answers: assessmentDetail.questions.map((q) => ({
          question_id: q.id,
          selected_option: answers[q.id] || 'A'
        }))
      };

      const res = await assessmentAPI.submit(assessmentDetail.id, submitPayload);
      setResult(res.data);
      setStep(3);
    } catch (err) {
      alert('Error submitting assessment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimer = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-xs font-semibold text-slate-500 mt-2">Loading Competency Assessment Framework...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Competency Assessment</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Take an assessment to identify your current skill level and receive personalized recommendations.
        </p>
      </div>

      {/* 3-Step Stepper Bar */}
      <div className="flex items-center justify-center max-w-xl mx-auto py-2">
        <div className="flex items-center space-x-3 text-xs font-bold">
          <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-blue-600' : 'text-slate-400'}`}>
            <span className={`h-6 w-6 rounded-full flex items-center justify-center text-xs ${
              step >= 1 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-600'
            }`}>
              1
            </span>
            <span>Select Domain</span>
          </div>

          <div className={`w-12 h-0.5 ${step >= 2 ? 'bg-blue-600' : 'bg-slate-200'}`} />

          <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-blue-600' : 'text-slate-400'}`}>
            <span className={`h-6 w-6 rounded-full flex items-center justify-center text-xs ${
              step >= 2 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-600'
            }`}>
              2
            </span>
            <span>Take Assessment</span>
          </div>

          <div className={`w-12 h-0.5 ${step >= 3 ? 'bg-blue-600' : 'bg-slate-200'}`} />

          <div className={`flex items-center space-x-2 ${step >= 3 ? 'text-blue-600' : 'text-slate-400'}`}>
            <span className={`h-6 w-6 rounded-full flex items-center justify-center text-xs ${
              step >= 3 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-600'
            }`}>
              3
            </span>
            <span>View Results</span>
          </div>
        </div>
      </div>

      {/* Step 1: Select Domain (3x2 Grid) */}
      {step === 1 && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {domainCards.map((domain) => {
              const Icon = domain.icon;
              const isSelected = selectedDomain === domain.id;
              return (
                <div
                  key={domain.id}
                  onClick={() => setSelectedDomain(domain.id)}
                  className={`p-6 rounded-2xl border transition-all duration-150 cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'bg-blue-50/50 border-blue-600 shadow-sm ring-1 ring-blue-500'
                      : 'bg-white border-slate-200/90 hover:border-slate-300 shadow-2xs'
                  }`}
                >
                  <div className="space-y-3">
                    <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${
                      isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700'
                    }`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-extrabold text-sm text-slate-900">{domain.title}</h3>
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">{domain.description}</p>
                    </div>
                  </div>

                  <div className="pt-4 mt-2 flex items-center justify-between text-xs">
                    <span className="text-[11px] font-semibold text-slate-400">{domain.categoryMatch}</span>
                    <span className={`text-[11px] font-bold ${isSelected ? 'text-blue-600' : 'text-slate-400'}`}>
                      {isSelected ? '✓ Selected' : 'Select'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-end pt-4">
            <button
              onClick={handleProceedToQuestions}
              className="px-6 py-2.5 bg-[#0C1E38] hover:bg-[#081528] text-white font-bold text-xs rounded-xl shadow-sm transition flex items-center space-x-2"
            >
              <span>Next</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Active Assessment Question Runner (Matches Middle-Right Reference) */}
      {step === 2 && assessmentDetail && (
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Runner Header */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex items-center justify-between">
            <div>
              <h2 className="text-base font-extrabold text-slate-900">
                {activeAssessment?.title || selectedDomain} - Quiz
              </h2>
              <div className="text-xs text-slate-500 font-medium mt-0.5">
                Question {currentQIndex + 1} of {assessmentDetail.questions.length}
              </div>
            </div>

            <div className="flex items-center space-x-2 bg-slate-900 text-white px-3.5 py-1.5 rounded-xl font-mono text-xs font-bold shadow-xs">
              <Clock className="h-4 w-4 text-amber-400" />
              <span>Time Left: {formatTimer(timeLeft)}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${((currentQIndex + 1) / assessmentDetail.questions.length) * 100}%` }}
            />
          </div>

          {/* Question Card with Radio Choices */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs space-y-6">
            <h3 className="text-base font-bold text-slate-900 leading-relaxed">
              {assessmentDetail.questions[currentQIndex]?.question_text}
            </h3>

            <div className="space-y-3 pt-2">
              {[
                { key: 'A', text: assessmentDetail.questions[currentQIndex]?.option_a },
                { key: 'B', text: assessmentDetail.questions[currentQIndex]?.option_b },
                { key: 'C', text: assessmentDetail.questions[currentQIndex]?.option_c },
                { key: 'D', text: assessmentDetail.questions[currentQIndex]?.option_d },
              ].map((opt) => {
                const qId = assessmentDetail.questions[currentQIndex]?.id;
                const isSelected = answers[qId] === opt.key;
                return (
                  <button
                    key={opt.key}
                    onClick={() => handleSelectOption(qId, opt.key)}
                    className={`w-full text-left p-4 rounded-xl border text-xs font-medium transition flex items-center space-x-3 ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-600 text-blue-900 ring-1 ring-blue-500'
                        : 'bg-slate-50/60 border-slate-200 hover:border-slate-300 text-slate-800'
                    }`}
                  >
                    <div className={`h-4 w-4 rounded-full border flex items-center justify-center shrink-0 ${
                      isSelected ? 'border-blue-600 bg-blue-600' : 'border-slate-400 bg-white'
                    }`}>
                      {isSelected && <div className="h-1.5 w-1.5 rounded-full bg-white" />}
                    </div>
                    <span className="font-semibold">{opt.text}</span>
                  </button>
                );
              })}
            </div>

            {/* Previous & Next/Submit Navigation */}
            <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
              <button
                disabled={currentQIndex === 0}
                onClick={() => setCurrentQIndex((prev) => prev - 1)}
                className="inline-flex items-center space-x-1.5 px-4 py-2 bg-white hover:bg-slate-50 disabled:opacity-40 text-slate-700 text-xs font-bold rounded-xl border border-slate-200 transition"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Previous</span>
              </button>

              {currentQIndex < assessmentDetail.questions.length - 1 ? (
                <button
                  onClick={() => setCurrentQIndex((prev) => prev + 1)}
                  className="inline-flex items-center space-x-1.5 px-5 py-2.5 bg-[#0C1E38] hover:bg-blue-900 text-white text-xs font-bold rounded-xl shadow-xs transition"
                >
                  <span>Next</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={submitting}
                  className="inline-flex items-center space-x-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition disabled:opacity-50"
                >
                  <span>{submitting ? 'Submitting...' : 'Submit Assessment'}</span>
                  <CheckCircle2 className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Assessment Results & Evaluation Screen */}
      {step === 3 && result && (
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="bg-white rounded-3xl p-8 border border-slate-200/90 shadow-2xs text-center space-y-4">
            <div className={`h-16 w-16 rounded-full mx-auto flex items-center justify-center ${
              result.passed ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'
            }`}>
              {result.passed ? <CheckCircle2 className="h-8 w-8" /> : <Award className="h-8 w-8" />}
            </div>

            <h2 className="text-2xl font-black text-slate-900">{result.assessment_title} Evaluation</h2>
            <p className="text-xs text-slate-500">Official Competency Benchmark Results</p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-lg mx-auto text-left pt-2">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Score</span>
                <span className="text-xl font-black text-blue-700">{result.score_percentage}%</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Correct</span>
                <span className="text-xl font-black text-slate-900">{result.correct_count}/{result.total_questions}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Previous Level</span>
                <span className="text-xl font-black text-slate-600">L{result.previous_level}</span>
              </div>
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <span className="text-[10px] text-emerald-800 font-bold uppercase block">Updated Level</span>
                <span className="text-xl font-black text-emerald-700">L{result.new_level} {result.level_improved && '▲'}</span>
              </div>
            </div>

            {result.level_improved && (
              <div className="p-3 bg-emerald-50 text-emerald-900 text-xs font-bold rounded-xl max-w-lg mx-auto border border-emerald-200 flex items-center justify-center space-x-2">
                <Sparkles className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>Competency level updated! Skill gaps have been automatically recalculated.</span>
              </div>
            )}

            <div className="pt-4 flex justify-center space-x-3">
              <button
                onClick={() => setStep(1)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition"
              >
                Assess Another Domain
              </button>
              <button
                onClick={() => navigate('/learning-path')}
                className="px-5 py-2 bg-[#0C1E38] hover:bg-blue-900 text-white font-bold text-xs rounded-xl shadow transition flex items-center space-x-1.5"
              >
                <span>View Recommended Courses</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Assessment;
