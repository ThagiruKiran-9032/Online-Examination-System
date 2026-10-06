import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { BookOpen, Clock, Award, CheckCircle, Play, Filter, FileText } from 'lucide-react';

const CATEGORIES = ["All", "Numeric", "Logic & Reasoning", "English", "General Knowledge", "Technical"];

export const StudentDashboard = () => {
  const [exams, setExams] = useState([]);
  const [myRegistrations, setMyRegistrations] = useState([]);
  const [myResults, setMyResults] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchData = async () => {
    setLoading(true);
    try {
      const url = selectedCategory === "All" ? '/exams/' : `/exams/?category=${encodeURIComponent(selectedCategory)}`;
      const [examRes, regRes, resRes] = await Promise.all([
        api.get(url),
        api.get('/students/me/registrations'),
        api.get('/students/me/results')
      ]);
      setExams(examRes.data);
      setMyRegistrations(regRes.data.map(r => r.exam_id));
      setMyResults(resRes.data);
    } catch (err) {
      console.error("Failed to fetch student dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedCategory]);

  const handleRegister = async (examId) => {
    try {
      await api.post(`/exams/${examId}/register`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Registration failed");
    }
  };

  const handleStartExam = async (examId) => {
    try {
      const res = await api.post(`/exams/${examId}/start-attempt`);
      const { attempt_id } = res.data;
      navigate(`/student/attempt/${attempt_id}`);
    } catch (err) {
      alert(err.response?.data?.detail || "Could not start exam attempt");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Student Welcome Header */}
      <div className="bg-gradient-to-r from-slate-900 to-blue-900 rounded-2xl p-8 text-white shadow-lg mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight">Available Online Examinations</h1>
        <p className="text-blue-200 mt-2 max-w-2xl text-sm">
          Browse exams across Numerical Ability, Logic & Reasoning, English, and General Knowledge. Register with 1-click and attempt timed tests.
        </p>
      </div>

      {/* Subject Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-4 mb-6 border-b border-slate-200">
        <Filter className="h-4 w-4 text-slate-400 mr-2 flex-shrink-0" />
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold whitespace-nowrap transition ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Exam Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : exams.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm">
          <BookOpen className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-slate-700">No active exams found in this category</h3>
          <p className="text-slate-400 text-sm mt-1">Check back later or select a different category.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.map((exam) => {
            const isRegistered = myRegistrations.includes(exam.id);
            const myAttempt = myResults.find(r => r.exam_id === exam.id);

            return (
              <div key={exam.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between p-6">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-3 py-1 rounded-md text-xs font-bold bg-blue-50 text-blue-700 border border-blue-100">
                      {exam.category}
                    </span>
                    {isRegistered && (
                      <span className="inline-flex items-center space-x-1 text-xs font-semibold text-green-700 bg-green-50 px-2.5 py-0.5 rounded-full border border-green-200">
                        <CheckCircle className="h-3.5 w-3.5" />
                        <span>Registered</span>
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 line-clamp-1">{exam.title}</h3>
                  <p className="text-slate-500 text-sm mt-1 line-clamp-2 h-10">{exam.description || 'No description provided.'}</p>

                  <div className="grid grid-cols-3 gap-2 my-4 p-3 bg-slate-50 rounded-xl text-xs text-slate-600 border border-slate-100">
                    <div className="flex flex-col items-center">
                      <Clock className="h-4 w-4 text-slate-400 mb-1" />
                      <span>{exam.duration_minutes} Mins</span>
                    </div>
                    <div className="flex flex-col items-center">
                      <FileText className="h-4 w-4 text-slate-400 mb-1" />
                      <span>{exam.total_questions} Questions</span>
                    </div>
                    <div className="flex flex-col items-center">
                      <Award className="h-4 w-4 text-slate-400 mb-1" />
                      <span>Pass: {exam.passing_marks}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100">
                  {myAttempt ? (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs p-2.5 bg-slate-50 rounded-lg">
                        <span className="font-semibold text-slate-600">Your Result:</span>
                        <span className={`font-bold ${myAttempt.passed ? 'text-green-600' : 'text-red-600'}`}>
                          {myAttempt.score} / {myAttempt.total_possible_score} ({myAttempt.passed ? 'PASSED' : 'FAILED'})
                        </span>
                      </div>
                      <button
                        onClick={() => navigate(`/student/result/${myAttempt.attempt_id}`)}
                        className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg transition"
                      >
                        View Result & Review
                      </button>
                    </div>
                  ) : isRegistered ? (
                    <button
                      onClick={() => handleStartExam(exam.id)}
                      className="w-full flex items-center justify-center space-x-2 py-2.5 bg-green-600 hover:bg-green-500 text-white font-semibold text-sm rounded-xl shadow-sm transition"
                    >
                      <Play className="h-4 w-4 fill-white" />
                      <span>Start Exam Now</span>
                    </button>
                  ) : (
                    <button
                      onClick={() => handleRegister(exam.id)}
                      className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-sm transition"
                    >
                      Register for Exam
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
