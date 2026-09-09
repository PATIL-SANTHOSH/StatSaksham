import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { quizAPI } from '../services/api';
import { 
  UploadCloud, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  ArrowRight, 
  ArrowLeft, 
  FileUp, 
  RotateCcw,
  FileText,
  Check
} from 'lucide-react';

const QuizGenerator = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Document upload state
  const [file, setFile] = useState(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [competencyTag, setCompetencyTag] = useState('Python for Data Analysis');
  const [uploading, setUploading] = useState(false);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [userDocs, setUserDocs] = useState([]);

  // Question generator configuration
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [rawText, setRawText] = useState('');
  const [useManualText, setUseManualText] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Active Quiz Runner state
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [quizResult, setQuizResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(540); // 9 minutes

  useEffect(() => {
    if (!user) return;
    const fetchDocs = async () => {
      try {
        const res = await quizAPI.getDocuments(user.employee_id);
        setUserDocs(res.data);
      } catch (e) {
        console.error('Error fetching documents:', e);
      }
    };
    fetchDocs();
  }, [user]);

  // Countdown timer when quiz active
  useEffect(() => {
    if (quizQuestions.length === 0 || quizResult) return;
    const interval = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [quizQuestions, quizResult]);

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file to upload.');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('employee_id', user.employee_id);
      formData.append('competency_tag', competencyTag);
      formData.append('title', uploadTitle || file.name);

      const res = await quizAPI.uploadDocument(formData);
      setUploadedDoc(res.data);
      setUserDocs([res.data, ...userDocs]);
    } catch (err) {
      alert('Error uploading document. Ensure file is a valid PDF, PPTX, or TXT.');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    setGenerating(true);
    setQuizResult(null);
    setAnswers({});
    setCurrentQIndex(0);
    setTimeLeft(numQuestions * 100);

    try {
      const payload = {
        document_id: uploadedDoc ? uploadedDoc.id : null,
        competency: competencyTag,
        difficulty: difficulty,
        num_questions: parseInt(numQuestions),
        raw_text: useManualText ? rawText : null
      };

      const res = await quizAPI.generateQuiz(payload);
      setQuizQuestions(res.data);
    } catch (err) {
      alert('Failed to generate AI Quiz. Ensure document has sufficient statistical content.');
    } finally {
      setGenerating(false);
    }
  };

  const handleOptionSelect = (qId, optionKey) => {
    setAnswers({ ...answers, [qId]: optionKey });
  };

  const handleQuizSubmit = async () => {
    if (quizQuestions.length === 0) return;
    setSubmitting(true);
    try {
      const submitPayload = {
        employee_id: user.employee_id,
        document_id: uploadedDoc ? uploadedDoc.id : null,
        competency: competencyTag,
        answers: quizQuestions.map(q => ({
          question_id: q.id,
          selected_option: answers[q.id] || 'A'
        }))
      };

      const res = await quizAPI.submitQuiz(submitPayload);
      setQuizResult(res.data);
    } catch (err) {
      alert('Error submitting quiz answers.');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTimer = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // View 1: Results View
  if (quizResult) {
    return (
      <div className="max-w-3xl mx-auto space-y-6 pb-12">
        <div className="bg-white rounded-3xl p-8 border border-slate-200/90 shadow-2xs text-center space-y-4">
          <div className={`h-16 w-16 rounded-full mx-auto flex items-center justify-center ${
            quizResult.passed ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'
          }`}>
            {quizResult.passed ? <CheckCircle2 className="h-8 w-8" /> : <Clock className="h-8 w-8" />}
          </div>

          <h2 className="text-2xl font-black text-slate-900">{quizResult.competency} Quiz Results</h2>
          <p className="text-xs text-slate-500">RAG-Generated Evaluation Assessment</p>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-md mx-auto text-left pt-2">
            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200/80">
              <span className="text-[10px] text-slate-400 font-bold uppercase block">Score</span>
              <span className="text-2xl font-black text-blue-700">{quizResult.score_percentage}%</span>
            </div>
            <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-200/80">
              <span className="text-[10px] text-slate-400 font-bold uppercase block">Correct</span>
              <span className="text-2xl font-black text-slate-900">{quizResult.correct_count}/{quizResult.total_questions}</span>
            </div>
            <div className="p-3.5 bg-emerald-50 rounded-2xl border border-emerald-200">
              <span className="text-[10px] text-emerald-800 font-bold uppercase block">Competency</span>
              <span className="text-lg font-black text-emerald-700">
                {quizResult.new_competency_level ? `Level ${quizResult.new_competency_level}` : 'Verified'}
              </span>
            </div>
          </div>

          <div className="pt-4 flex justify-center space-x-3">
            <button
              onClick={() => {
                setQuizQuestions([]);
                setQuizResult(null);
              }}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition"
            >
              Generate Another Quiz
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-5 py-2 bg-[#0C1E38] hover:bg-blue-900 text-white font-bold text-xs rounded-xl shadow transition"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // View 2: Active Quiz Runner (Matches Middle-Right Reference exactly)
  if (quizQuestions.length > 0) {
    const q = quizQuestions[currentQIndex];
    const totalQ = quizQuestions.length;

    return (
      <div className="max-w-3xl mx-auto space-y-6 pb-12">
        {/* Runner Header */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-2xs flex items-center justify-between">
          <div>
            <h2 className="text-base font-extrabold text-slate-900">
              {competencyTag} - Quiz
            </h2>
            <div className="text-xs text-slate-500 font-medium mt-0.5">
              Question {currentQIndex + 1} of {totalQ}
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
            style={{ width: `${((currentQIndex + 1) / totalQ) * 100}%` }}
          />
        </div>

        {/* Question Card with Radio Choices */}
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs space-y-6">
          <h3 className="text-base font-bold text-slate-900 leading-relaxed">
            {q.question_text}
          </h3>

          <div className="space-y-3 pt-2">
            {[
              { key: 'A', text: q.option_a },
              { key: 'B', text: q.option_b },
              { key: 'C', text: q.option_c },
              { key: 'D', text: q.option_d },
            ].map((opt) => {
              const isSelected = answers[q.id] === opt.key;
              return (
                <button
                  key={opt.key}
                  onClick={() => handleOptionSelect(q.id, opt.key)}
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

            {currentQIndex < totalQ - 1 ? (
              <button
                onClick={() => setCurrentQIndex((prev) => prev + 1)}
                className="inline-flex items-center space-x-1.5 px-5 py-2.5 bg-[#0C1E38] hover:bg-blue-900 text-white text-xs font-bold rounded-xl shadow-xs transition"
              >
                <span>Next</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            ) : (
              <button
                onClick={handleQuizSubmit}
                disabled={submitting}
                className="inline-flex items-center space-x-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition disabled:opacity-50"
              >
                <span>{submitting ? 'Submitting...' : 'Submit Quiz'}</span>
                <Check className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // View 3: Document Upload & AI Generation Configuration
  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">AI Quiz Generator</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Upload learning material (PDF, PPTX, TXT) to generate customized MCQs using the RAG pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Upload Card */}
        <div className="md:col-span-7 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs space-y-4">
          <h3 className="font-extrabold text-sm text-slate-900">Upload Learning Material</h3>

          <form onSubmit={handleFileUpload} className="space-y-4 text-xs">
            <div className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-2xl p-6 text-center bg-slate-50/60 transition cursor-pointer relative">
              <input
                type="file"
                accept=".pdf,.pptx,.ppt,.txt,.docx"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                    setUploadTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ''));
                  }
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <FileUp className="h-9 w-9 text-blue-600 mx-auto mb-2" />
              <p className="font-bold text-slate-800 text-sm">
                {file ? file.name : 'Click or Drag & Drop File Here'}
              </p>
              <p className="text-[11px] text-slate-500 mt-1">
                Supports PDF, PPTX, TXT up to 25MB
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Document Title</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g. Python for Data Analysis"
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 focus:outline-none text-xs font-semibold"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Target Competency</label>
                <select
                  value={competencyTag}
                  onChange={(e) => setCompetencyTag(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-600 focus:outline-none bg-white font-semibold text-xs"
                >
                  <option value="Python for Data Analysis">Python for Data Analysis</option>
                  <option value="National Accounts">National Accounts</option>
                  <option value="Sampling Techniques">Sampling Techniques</option>
                  <option value="Price Statistics">Price Statistics</option>
                  <option value="Survey Design">Survey Design</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full py-2.5 bg-[#0C1E38] hover:bg-[#081528] disabled:opacity-40 text-white font-bold rounded-xl shadow-xs transition flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <span>Extracting Text & Vector Chunking...</span>
              ) : (
                <>
                  <UploadCloud className="h-4 w-4" />
                  <span>Process Document with RAG Engine</span>
                </>
              )}
            </button>
          </form>

          {uploadedDoc && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-center space-x-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
              <span><strong>{uploadedDoc.filename}</strong> ingested into {uploadedDoc.chunk_count} vector chunks!</span>
            </div>
          )}
        </div>

        {/* Configuration Card */}
        <div className="md:col-span-5 bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-2xs flex flex-col justify-between space-y-4">
          <div>
            <h3 className="font-extrabold text-sm text-slate-900 mb-3">Quiz Parameters</h3>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1.5">Number of Questions</label>
                <div className="grid grid-cols-4 gap-2">
                  {[5, 10, 15, 20].map((num) => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setNumQuestions(num)}
                      className={`py-2 rounded-xl font-bold transition ${
                        numQuestions === num
                          ? 'bg-blue-600 text-white shadow-xs'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      {num}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1.5">Assessment Difficulty</label>
                <div className="grid grid-cols-3 gap-2">
                  {['Beginner', 'Intermediate', 'Advanced'].map((diff) => (
                    <button
                      key={diff}
                      type="button"
                      onClick={() => setDifficulty(diff)}
                      className={`py-2 rounded-xl font-bold transition text-[11px] ${
                        difficulty === diff
                          ? 'bg-[#0C1E38] text-white shadow-xs'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      {diff}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="font-bold text-slate-700">Or Paste Text Excerpt</label>
                  <button
                    type="button"
                    onClick={() => setUseManualText(!useManualText)}
                    className="text-[11px] text-blue-600 font-bold hover:underline"
                  >
                    {useManualText ? 'Use Uploaded File' : 'Paste Text'}
                  </button>
                </div>

                {useManualText && (
                  <textarea
                    rows={3}
                    value={rawText}
                    onChange={(e) => setRawText(e.target.value)}
                    placeholder="Paste statistical policy or training notes..."
                    className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-600 focus:outline-none"
                  />
                )}
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerateQuiz}
            disabled={generating || (!uploadedDoc && !rawText && !useManualText)}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-black text-xs rounded-xl shadow transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {generating ? (
              <span>Generating AI MCQs...</span>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Generate {numQuestions} AI MCQs Now</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizGenerator;
