import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, Mail, Phone, Building, Lock, CheckCircle2, AlertCircle, Eye, EyeOff, Save } from 'lucide-react';

export const StudentProfile = () => {
  const { user, updateProfile } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [department, setDepartment] = useState(user?.department || '');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null); // { type: 'success'|'error', text: '' }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      const payload = {
        full_name: fullName,
        phone: phone || null,
        department: department || null,
      };
      if (password) {
        payload.password = password;
      }

      await updateProfile(payload);
      setPassword('');
      setMessage({ type: 'success', text: 'Profile details updated successfully!' });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to update profile details. Please try again.'
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Student Profile & Settings</h1>
        <p className="text-slate-500 text-sm mt-1">
          Manage your personal account details. Note that email addresses are locked for security reasons.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-xl flex items-center space-x-3 text-sm font-medium ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile Summary Card */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col items-center text-center h-fit">
          <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center font-bold text-2xl shadow-md mb-4">
            {user?.full_name?.charAt(0) || 'S'}
          </div>
          <h2 className="text-lg font-bold text-slate-900">{user?.full_name}</h2>
          <p className="text-slate-500 text-xs mt-0.5">{user?.email}</p>
          <span className="mt-3 px-3 py-1 bg-blue-50 text-blue-700 text-xs font-semibold rounded-full border border-blue-100 uppercase tracking-wider">
            {user?.role || 'Student'} Account
          </span>
          <div className="w-full border-t border-slate-100 mt-6 pt-4 text-left space-y-2.5 text-xs text-slate-500">
            <div className="flex justify-between">
              <span>Account Status:</span>
              <span className="font-semibold text-green-600">Active</span>
            </div>
            <div className="flex justify-between">
              <span>Joined:</span>
              <span className="font-semibold text-slate-700">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Edit Form */}
        <div className="md:col-span-2 bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-6 border-b border-slate-100 pb-3">
            Edit Personal Details
          </h3>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field - LOCKED / READ-ONLY */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-700 uppercase">Email Address</label>
                <span className="inline-flex items-center text-xs text-amber-600 font-medium bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  <Lock className="h-3 w-3 mr-1" /> Read-Only
                </span>
              </div>
              <div className="relative">
                <input
                  type="email"
                  disabled
                  value={user?.email || ''}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-slate-500 text-sm font-medium cursor-not-allowed"
                />
                <Mail className="h-4 w-4 text-slate-400 absolute left-3.5 top-3" />
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Email address cannot be modified to protect account identity and exam registration records.
              </p>
            </div>

            {/* Full Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Full Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <User className="h-4 w-4 text-slate-400 absolute left-3.5 top-3" />
              </div>
            </div>

            {/* Phone Number */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Phone Number</label>
              <div className="relative">
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+1 (555) 000-0000"
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <Phone className="h-4 w-4 text-slate-400 absolute left-3.5 top-3" />
              </div>
            </div>

            {/* Department / Branch */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Department / Branch</label>
              <div className="relative">
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. Computer Science, Mechanical, etc."
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <Building className="h-4 w-4 text-slate-400 absolute left-3.5 top-3" />
              </div>
            </div>

            {/* Optional Password Update */}
            <div className="pt-3 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                New Password <span className="text-slate-400 font-normal lowercase">(leave blank to keep current)</span>
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter new password (optional)"
                  className="w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <Lock className="h-4 w-4 text-slate-400 absolute left-3.5 top-3" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 transition"
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-4 flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className="inline-flex items-center space-x-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-sm transition"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
