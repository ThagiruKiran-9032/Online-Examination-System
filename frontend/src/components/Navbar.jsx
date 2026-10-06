import React from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, BookOpen, User, ShieldCheck } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const navLinkClass = ({ isActive }) =>
    `px-3.5 py-1.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
      isActive
        ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30 border border-blue-500/40'
        : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
    }`;

  return (
    <nav className="bg-slate-900 text-white shadow-md sticky top-0 z-50 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-3">
            <Link to={user.role === 'admin' ? '/admin' : '/student'} className="flex items-center space-x-2 font-bold text-xl tracking-tight hover:text-blue-400 transition">
              <BookOpen className="h-6 w-6 text-blue-500" />
              <span>Exam Portal</span>
            </Link>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
              user.role === 'admin' 
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
                : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
            }`}>
              {user.role === 'admin' ? 'Admin Mode' : 'Student Mode'}
            </span>
          </div>

          <div className="flex items-center space-x-3 sm:space-x-4">
            {user.role === 'admin' ? (
              <>
                <NavLink to="/admin" end className={navLinkClass}>
                  Exams
                </NavLink>
                <NavLink to="/admin/students" className={navLinkClass}>
                  Students
                </NavLink>
              </>
            ) : (
              <>
                <NavLink to="/student" end className={navLinkClass}>
                  My Dashboard
                </NavLink>
                <NavLink to="/student/results" className={navLinkClass}>
                  My Results
                </NavLink>
              </>
            )}

            <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-blue-400">
                  {user.full_name?.charAt(0) || 'U'}
                </div>
                <span className="text-sm font-semibold text-slate-200 hidden md:inline">{user.full_name}</span>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-xl transition"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
