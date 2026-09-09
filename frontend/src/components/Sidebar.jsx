import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  User,
  FileCheck2,
  TrendingDown,
  GraduationCap,
  BookOpen,
  HelpCircle,
  Activity,
  Bot,
  LogOut,
  Sparkles,
  BarChart2,
  Users,
  Layers,
  LifeBuoy
} from 'lucide-react';

const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'ADMIN';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const learnerNav = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'My Profile', path: '/profile', icon: User },
    { name: 'Assessment', path: '/assessment', icon: FileCheck2 },
    { name: 'Skill Gap', path: '/skill-gaps', icon: TrendingDown },
    { name: 'Learning Path', path: '/learning-path', icon: GraduationCap },
    { name: 'Courses', path: '/courses', icon: BookOpen },
    { name: 'Quiz', path: '/quiz', icon: HelpCircle },
    { name: 'Progress', path: '/progress', icon: Activity },
    { name: 'AI Assistant', path: '/assistant', icon: Bot, isAi: true },
  ];

  const adminNav = [
    { name: 'Admin Dashboard', path: '/admin/dashboard', icon: LayoutDashboard },
    { name: 'Workforce Analytics', path: '/admin/analytics', icon: BarChart2 },
    { name: 'Employee Directory', path: '/admin/employees', icon: Users },
    { name: 'Competency Framework', path: '/competencies', icon: Layers },
    { name: 'Course Catalogues', path: '/courses', icon: BookOpen },
  ];

  const links = isAdmin ? adminNav : learnerNav;

  return (
    <aside className="w-60 bg-[#0C1E38] text-slate-300 flex flex-col shrink-0 min-h-screen border-r border-[#162B4C] select-none">
      {/* Brand Header */}
      <div className="px-6 py-6 flex items-center space-x-3 border-b border-[#162B4C]">
        <div className="flex items-center space-x-2">
          {/* Logo Mark: Stylized Bar Chart Icon */}
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md">
            <BarChart2 className="h-5 w-5 stroke-[2.5]" />
          </div>
          <div>
            <span className="font-extrabold text-lg text-white tracking-tight flex items-center">
              StatSaksham
            </span>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
        {links.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3.5 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-300 hover:bg-[#162B4C] hover:text-white'
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="truncate">{item.name}</span>
              {item.isAi && (
                <span className="ml-auto text-[9px] font-black bg-blue-500/30 text-blue-200 px-1.5 py-0.5 rounded border border-blue-400/30">
                  AI
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Actions: Support & Logout */}
      <div className="p-3 border-t border-[#162B4C] space-y-1">
        <button
          onClick={() => navigate('/assistant')}
          className="w-full flex items-center space-x-3 px-3.5 py-2 text-xs font-medium text-slate-300 hover:bg-[#162B4C] hover:text-white rounded-xl transition"
        >
          <LifeBuoy className="h-4 w-4 shrink-0 text-slate-400" />
          <span>Support</span>
        </button>

        <button
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-3.5 py-2 text-xs font-medium text-slate-300 hover:bg-rose-900/40 hover:text-rose-200 rounded-xl transition"
        >
          <LogOut className="h-4 w-4 shrink-0 text-slate-400" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
