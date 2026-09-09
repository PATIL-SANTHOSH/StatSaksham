import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  BarChart2, 
  CheckCircle2, 
  Award, 
  GraduationCap, 
  TrendingUp, 
  Sparkles, 
  Lock, 
  Eye, 
  EyeOff, 
  Shield, 
  ChevronDown, 
  Building2, 
  ArrowRight 
} from 'lucide-react';

const Login = () => {
  const [employeeId, setEmployeeId] = useState('OSS1001');
  const [password, setPassword] = useState('demo123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPersonas, setShowPersonas] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const res = await login(employeeId, password);
    setLoading(false);
    if (res.success) {
      if (res.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/dashboard');
      }
    } else {
      setError(res.error);
    }
  };

  const handleQuickPersona = async (id, pass) => {
    setEmployeeId(id);
    setPassword(pass);
    setError('');
    setLoading(true);
    const res = await login(id, pass);
    setLoading(false);
    if (res.success) {
      if (res.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/dashboard');
      }
    } else {
      setError(res.error);
    }
  };

  const personas = [
    { id: 'OSS1001', name: 'Ravi Kumar', role: 'Statistical Officer', dept: 'National Accounts Division' },
    { id: 'OSS1002', name: 'Priya Sharma', role: 'Junior Statistical Officer', dept: 'Price Statistics Division' },
    { id: 'OSS1003', name: 'Amit Verma', role: 'Statistical Officer', dept: 'Field Operations Division' },
    { id: 'OSS1004', name: 'Neha Singh', role: 'Research Officer', dept: 'Data Informatics Division' },
    { id: 'OSS1005', name: 'Arjun Rao', role: 'Assistant Director', dept: 'Economic Statistics Division' },
    { id: 'ADMIN001', name: 'Admin Official', role: 'Joint Director', dept: 'Workforce & Capacity Building', isAdmin: true },
  ];

  return (
    <div className="min-h-screen w-full flex flex-col md:flex-row bg-[#0C1E38]">
      {/* Left Column: Government / Statistical Identity */}
      <div className="relative flex-1 p-8 sm:p-12 lg:p-16 flex flex-col justify-between overflow-hidden bg-gradient-to-br from-[#0C1E38] via-[#0F2344] to-[#0A182E] text-white">
        {/* Subtle Decorative Grid Pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(#1E3A8A_1px,transparent_1px)] [background-size:24px_24px] opacity-20 pointer-events-none" />

        {/* Top MoSPI & StatSaksham Branding Header */}
        <div className="relative z-10 flex items-start justify-between">
          <div className="space-y-1">
            <div className="text-[11px] font-bold tracking-wider uppercase text-slate-300 flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-amber-400" />
              <span>Ministry of Statistics and Programme Implementation</span>
            </div>
            <div className="text-[10px] text-slate-400">Government of India</div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md">
              <BarChart2 className="h-5 w-5 stroke-[2.5]" />
            </div>
            <div className="text-right">
              <div className="font-extrabold text-sm text-white tracking-tight">StatSaksham</div>
              <div className="text-[9px] text-slate-400">Learn • Grow • Strengthen Statistics</div>
            </div>
          </div>
        </div>

        {/* Main Headline Section */}
        <div className="relative z-10 my-auto py-12 max-w-xl">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-[1.15]">
            Empowering<br />
            Officials for a<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">
              Data-Driven India
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base mt-6 leading-relaxed max-w-md">
            Personalized learning. Stronger competencies.<br />
            A smarter statistical system.
          </p>
        </div>

        {/* 4 Feature Icon Pills at Bottom Left */}
        <div className="relative z-10 grid grid-cols-2 gap-4 max-w-lg pt-6 border-t border-slate-700/60 text-xs">
          <div className="flex items-center space-x-2.5 text-slate-200">
            <div className="h-7 w-7 rounded-lg bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-300 shrink-0">
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <span className="font-medium">Assess Skills</span>
          </div>

          <div className="flex items-center space-x-2.5 text-slate-200">
            <div className="h-7 w-7 rounded-lg bg-emerald-500/20 border border-emerald-400/30 flex items-center justify-center text-emerald-300 shrink-0">
              <GraduationCap className="h-4 w-4" />
            </div>
            <span className="font-medium">Learn from iGOT & NSSTA</span>
          </div>

          <div className="flex items-center space-x-2.5 text-slate-200">
            <div className="h-7 w-7 rounded-lg bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shrink-0">
              <Sparkles className="h-4 w-4 text-amber-300" />
            </div>
            <span className="font-medium">Get Recommendations</span>
          </div>

          <div className="flex items-center space-x-2.5 text-slate-200">
            <div className="h-7 w-7 rounded-lg bg-amber-500/20 border border-amber-400/30 flex items-center justify-center text-amber-300 shrink-0">
              <TrendingUp className="h-4 w-4" />
            </div>
            <span className="font-medium">Track Progress</span>
          </div>
        </div>
      </div>

      {/* Right Column: Floating White Authentication Card */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-10 bg-slate-900/60 md:bg-[#0B1A30] relative">
        <div className="w-full max-w-md bg-white rounded-3xl p-8 sm:p-10 shadow-2xl border border-slate-100 text-slate-900">
          <div className="mb-6">
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Welcome Back</h2>
            <p className="text-xs text-slate-500 mt-1 font-medium">Login to your account</p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-semibold">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Employee ID</label>
              <input
                type="text"
                required
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value.toUpperCase())}
                placeholder="Enter your Employee ID"
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center space-x-2 text-slate-600 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span>Remember me</span>
              </label>

              <button
                type="button"
                onClick={() => alert('For prototype demonstration, use passwords demo123 (Learner) or admin123 (Admin).')}
                className="text-blue-600 font-bold hover:underline"
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 bg-[#0C1E38] hover:bg-[#081528] text-white font-bold text-xs rounded-xl shadow-md transition flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <span>Login</span>
              )}
            </button>
          </form>

          {/* OR Divider */}
          <div className="relative my-5 text-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <span className="relative bg-white px-3 text-[11px] font-bold text-slate-400 uppercase">
              OR
            </span>
          </div>

          {/* Government SSO Button */}
          <button
            type="button"
            onClick={() => handleQuickPersona('OSS1001', 'demo123')}
            className="w-full py-2.5 px-4 bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold text-xs rounded-xl border border-slate-200 transition flex items-center justify-center space-x-2"
          >
            <Shield className="h-4 w-4 text-blue-700" />
            <span>Login with Government SSO (For Production)</span>
          </button>

          {/* Collapsible Demo Personas Selector */}
          <div className="mt-5 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setShowPersonas(!showPersonas)}
              className="w-full flex items-center justify-between text-[11px] font-bold text-slate-500 hover:text-blue-600 transition"
            >
              <span>1-Click Presentation Personas ({personas.length})</span>
              <ChevronDown className={`h-3.5 w-3.5 transition-transform ${showPersonas ? 'rotate-180' : ''}`} />
            </button>

            {showPersonas && (
              <div className="mt-2 space-y-1.5 max-h-48 overflow-y-auto pr-1 text-xs">
                {personas.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => handleQuickPersona(p.id, p.isAdmin ? 'admin123' : 'demo123')}
                    className="w-full text-left p-2 rounded-lg bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 transition flex items-center justify-between group"
                  >
                    <div>
                      <div className="font-bold text-slate-800 text-xs">{p.name} <span className="font-mono text-[10px] text-slate-500">({p.id})</span></div>
                      <div className="text-[10px] text-slate-500">{p.role} • {p.dept}</div>
                    </div>
                    <ArrowRight className="h-3 w-3 text-slate-400 group-hover:text-blue-600 transition" />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
