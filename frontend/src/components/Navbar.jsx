import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Search, Bell, User } from 'lucide-react';

const Navbar = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-slate-200/90 px-6 py-3 flex items-center justify-between shadow-2xs">
      {/* Global Search Bar */}
      <div className="relative w-72 sm:w-96">
        <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search courses, skills, or anything..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              navigate(`/courses?q=${encodeURIComponent(e.target.value)}`);
            }
          }}
          className="w-full pl-10 pr-4 py-2 bg-slate-50 hover:bg-slate-100/80 focus:bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition"
        />
      </div>

      {/* Right Controls: Notifications & Profile Pill */}
      <div className="flex items-center space-x-4">
        {/* Notification Bell */}
        <button
          className="relative p-2 rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition"
          title="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-blue-600 ring-2 ring-white" />
        </button>

        {/* User Profile Pill */}
        {user && (
          <Link
            to="/profile"
            className="flex items-center space-x-3 pl-2 py-1 rounded-xl hover:bg-slate-50 transition"
          >
            <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-blue-700 to-indigo-800 text-white font-bold text-xs flex items-center justify-center ring-2 ring-slate-100 shrink-0 overflow-hidden shadow-2xs">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="h-full w-full object-cover" />
              ) : (
                <span>{user.name ? user.name.charAt(0) : 'U'}</span>
              )}
            </div>

            <div className="text-left hidden sm:block">
              <div className="text-xs font-bold text-slate-900 leading-tight">
                {user.name || user.employee_id}
              </div>
              <div className="text-[11px] text-slate-500 font-medium">
                {user.designation || 'Statistical Officer'}
              </div>
            </div>
          </Link>
        )}
      </div>
    </header>
  );
};

export default Navbar;
