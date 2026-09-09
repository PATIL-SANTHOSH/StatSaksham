import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Competencies from './pages/Competencies';
import Assessment from './pages/Assessment';
import SkillGaps from './pages/SkillGaps';
import LearningPath from './pages/LearningPath';
import Courses from './pages/Courses';
import QuizGenerator from './pages/QuizGenerator';
import AIAssistant from './pages/AIAssistant';
import Progress from './pages/Progress';
import AdminDashboard from './pages/AdminDashboard';
import AdminEmployees from './pages/AdminEmployees';

const ProtectedLayout = ({ children, requireAdmin = false }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && user.role !== 'ADMIN') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex bg-[#F8FAFC] text-slate-900 font-sans antialiased">
      {/* Left Full-Height Deep Navy Sidebar */}
      <Sidebar />

      {/* Right Top Header + Scrollable Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <Navbar />
        <main className="flex-1 p-6 md:p-8 overflow-y-auto w-full">
          <div className="max-w-6xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to={user.role === 'ADMIN' ? '/admin/dashboard' : '/dashboard'} replace /> : <Login />}
      />

      {/* Root redirect */}
      <Route
        path="/"
        element={
          <Navigate
            to={user ? (user.role === 'ADMIN' ? '/admin/dashboard' : '/dashboard') : '/login'}
            replace
          />
        }
      />

      {/* Learner Routes */}
      <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/profile" element={<ProtectedLayout><Profile /></ProtectedLayout>} />
      <Route path="/competencies" element={<ProtectedLayout><Competencies /></ProtectedLayout>} />
      <Route path="/assessment" element={<ProtectedLayout><Assessment /></ProtectedLayout>} />
      <Route path="/skill-gaps" element={<ProtectedLayout><SkillGaps /></ProtectedLayout>} />
      <Route path="/learning-path" element={<ProtectedLayout><LearningPath /></ProtectedLayout>} />
      <Route path="/courses" element={<ProtectedLayout><Courses /></ProtectedLayout>} />
      <Route path="/quiz" element={<ProtectedLayout><QuizGenerator /></ProtectedLayout>} />
      <Route path="/assistant" element={<ProtectedLayout><AIAssistant /></ProtectedLayout>} />
      <Route path="/progress" element={<ProtectedLayout><Progress /></ProtectedLayout>} />

      {/* Admin Routes */}
      <Route path="/admin/dashboard" element={<ProtectedLayout requireAdmin={true}><AdminDashboard /></ProtectedLayout>} />
      <Route path="/admin/analytics" element={<ProtectedLayout requireAdmin={true}><AdminDashboard /></ProtectedLayout>} />
      <Route path="/admin/employees" element={<ProtectedLayout requireAdmin={true}><AdminEmployees /></ProtectedLayout>} />
      <Route path="/admin/competencies" element={<ProtectedLayout requireAdmin={true}><Competencies /></ProtectedLayout>} />

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
