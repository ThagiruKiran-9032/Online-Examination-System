import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { UserPlus, BookOpen, AlertCircle, CheckCircle, Eye, EyeOff, Check, X, ShieldAlert, Loader2, KeyRound, Send } from 'lucide-react';

export const Register = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [otpMessage, setOtpMessage] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  // Real-time email verification state
  const [verifyingEmail, setVerifyingEmail] = useState(false);
  const [emailStatus, setEmailStatus] = useState(null); // { is_valid_syntax, is_real_domain, is_registered, error_detail }

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleVerifyEmail = async (val) => {
    const target = val !== undefined ? val : email;
    if (!target || !target.includes('@')) {
      setEmailStatus(null);
      return;
    }
    setVerifyingEmail(true);
    try {
      const res = await api.post('/auth/verify-email', { email: target, check_domain: true });
      setEmailStatus(res.data);
    } catch (err) {
      setEmailStatus(null);
    } finally {
      setVerifyingEmail(false);
    }
  };

  const handleSendOtp = async () => {
    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address first.');
      return;
    }
    if (emailStatus && (!emailStatus.is_valid_syntax || !emailStatus.is_real_domain || emailStatus.is_registered)) {
      setError('Please resolve email verification issues before requesting OTP.');
      return;
    }
    setError('');
    setSendingOtp(true);
    setOtpMessage('');
    try {
      const res = await api.post('/auth/send-registration-otp', { email });
      setOtpSent(true);
      setOtpMessage(res.data.message || `Verification code sent to ${email}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send verification code. Please check your email.');
    } finally {
      setSendingOtp(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (emailStatus && !emailStatus.is_valid_syntax) {
      setError('Please provide a valid email format.');
      return;
    }
    if (emailStatus && !emailStatus.is_real_domain) {
      setError('Email domain verification failed. Please use a real email address.');
      return;
    }
    if (emailStatus && emailStatus.is_registered) {
      setError('This email address is already registered. Please sign in.');
      return;
    }

    setLoading(true);
    try {
      await register(email, fullName, password, otpSent ? otp : null);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex p-3 rounded-2xl bg-blue-600/10 text-blue-500 mb-3 border border-blue-500/20">
          <BookOpen className="h-10 w-10" />
        </div>
        <h2 className="text-3xl font-extrabold text-white">Student Registration</h2>
        <p className="mt-2 text-sm text-slate-400">Create an account to register & attempt exams</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-800/80 backdrop-blur-md py-8 px-4 shadow-xl border border-slate-700/60 sm:rounded-2xl sm:px-10">
          {error && (
            <div className="mb-4 bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-500/10 border border-green-500/20 text-green-400 p-3 rounded-lg text-sm flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 flex-shrink-0" />
              <span>Account created successfully! Redirecting to login...</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-slate-300">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className="mt-1 block w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>

            <div>
              <div className="flex justify-between items-center">
                <label className="block text-sm font-medium text-slate-300">Email Address</label>
                {verifyingEmail && (
                  <span className="text-xs text-blue-400 flex items-center space-x-1">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>Verifying domain...</span>
                  </span>
                )}
              </div>
              <div className="mt-1 flex space-x-2">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setEmailStatus(null);
                    setOtpSent(false);
                    setOtpMessage('');
                  }}
                  onBlur={() => handleVerifyEmail()}
                  placeholder="john@example.com"
                  className="block w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <button
                  type="button"
                  onClick={handleSendOtp}
                  disabled={sendingOtp || !email || (emailStatus && (!emailStatus.is_valid_syntax || !emailStatus.is_real_domain || emailStatus.is_registered))}
                  className="px-3 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 border border-slate-600 rounded-lg text-xs font-medium text-slate-200 flex items-center space-x-1 flex-shrink-0 transition"
                  title="Send OTP verification code to email"
                >
                  {sendingOtp ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Send className="h-3.5 w-3.5 text-blue-400" />
                  )}
                  <span>{otpSent ? 'Resend OTP' : 'Send OTP'}</span>
                </button>
              </div>

              {/* Email Status Verification Badges */}
              {emailStatus && (
                <div className="mt-2 space-y-1 text-xs">
                  {!emailStatus.is_valid_syntax ? (
                    <div className="flex items-center text-red-400 space-x-1 font-medium">
                      <X className="h-3.5 w-3.5" />
                      <span>Invalid email format</span>
                    </div>
                  ) : !emailStatus.is_real_domain ? (
                    <div className="flex items-center text-amber-400 space-x-1 font-medium">
                      <ShieldAlert className="h-3.5 w-3.5" />
                      <span>Domain cannot be verified / non-existent mail server</span>
                    </div>
                  ) : emailStatus.is_registered ? (
                    <div className="flex items-center text-red-400 space-x-1 font-medium">
                      <X className="h-3.5 w-3.5" />
                      <span>Email already registered</span>
                    </div>
                  ) : (
                    <div className="flex items-center text-green-400 space-x-1 font-medium">
                      <Check className="h-3.5 w-3.5" />
                      <span>Real email domain & available for registration</span>
                    </div>
                  )}
                </div>
              )}

              {otpMessage && (
                <div className="mt-2 p-2 bg-blue-500/10 border border-blue-500/20 rounded text-xs text-blue-300 flex items-center space-x-1">
                  <CheckCircle className="h-3.5 w-3.5 text-blue-400 flex-shrink-0" />
                  <span>{otpMessage}</span>
                </div>
              )}
            </div>

            {/* OTP Verification Code Section */}
            {otpSent && (
              <div className="p-3 bg-slate-900/80 border border-blue-500/30 rounded-xl space-y-2">
                <label className="block text-xs font-semibold text-blue-300 uppercase tracking-wider flex items-center space-x-1.5">
                  <KeyRound className="h-3.5 w-3.5 text-blue-400" />
                  <span>Email Verification Code (OTP)</span>
                </label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.trim())}
                  placeholder="Enter 6-digit OTP code"
                  className="block w-full px-3 py-2 bg-slate-800 border border-blue-500/50 rounded-lg text-white text-center font-mono text-base tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-slate-500"
                />
                <p className="text-[11px] text-slate-400">Enter the 6-digit code sent to your email to verify ownership.</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-300">Password</label>
              <div className="relative mt-1">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  minLength={6}
                  className="block w-full px-3 py-2 pr-10 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition"
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4 text-slate-400" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || success || (emailStatus && (!emailStatus.is_valid_syntax || !emailStatus.is_real_domain || emailStatus.is_registered))}
              className="w-full flex justify-center items-center space-x-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition"
            >
              <UserPlus className="h-4 w-4" />
              <span>{loading ? 'Creating Account...' : 'Register Account'}</span>
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-slate-400">Already registered? </span>
            <Link to="/login" className="font-medium text-blue-400 hover:text-blue-300 transition">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
