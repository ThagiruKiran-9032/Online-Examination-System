import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { Award, CheckCircle, XCircle, Clock, Eye, FileText } from 'lucide-react';

export const ResultsList = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      try {
        const res = await api.get('/students/me/results');
        setResults(res.data);
      } catch (err) {
        console.error("Failed to fetch student results:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
        <h1 className="text-2xl font-bold text-slate-900">My Exam History & Results</h1>
        <p className="text-slate-500 text-sm mt-1">View all your completed exam scores, performance breakdown, and answer reviews</p>
      </div>

      {results.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm">
          <Award className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-slate-700">No exam attempts yet</h3>
          <p className="text-slate-400 text-sm mt-1">Register and attempt an exam from your dashboard to view your results here.</p>
          <Link to="/student" className="mt-4 inline-block px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl transition shadow-sm">
            Go to Dashboard
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((res) => {
            const percentage = res.total_possible_score > 0
              ? Math.round((res.score / res.total_possible_score) * 100)
              : 0;

            return (
              <div key={res.attempt_id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-blue-50 text-blue-700 border border-blue-100">
                      {res.category}
                    </span>
                    <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      res.passed ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
                    }`}>
                      {res.passed ? <CheckCircle className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
                      <span>{res.passed ? 'PASSED' : 'FAILED'}</span>
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900">{res.exam_title}</h3>
                  <p className="text-xs text-slate-400 mt-1">Submitted: {new Date(res.end_time || res.start_time).toLocaleString()}</p>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <div className="text-2xl font-black text-blue-600">{res.score} / {res.total_possible_score}</div>
                    <div className="text-xs font-semibold text-slate-500">{percentage}% Score</div>
                  </div>

                  <button
                    onClick={() => navigate(`/student/result/${res.attempt_id}`)}
                    className="inline-flex items-center space-x-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl transition shadow-sm"
                  >
                    <Eye className="h-4 w-4" />
                    <span>Review Answers</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
