import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/axios';
import { ArrowLeft, Trophy, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

export const ExamResults = () => {
  const { examId } = useParams();
  const [exam, setExam] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [examRes, lbRes] = await Promise.all([
          api.get(`/exams/${examId}`),
          api.get(`/exams/${examId}/leaderboard`)
        ]);
        setExam(examRes.data);
        setLeaderboard(lbRes.data);
      } catch (err) {
        console.error("Failed to load leaderboard:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [examId]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center space-x-3 mb-6">
        <Link to="/admin" className="p-2 bg-white rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{exam?.title} - Leaderboard & Results</h1>
          <p className="text-slate-500 text-sm">Category: {exam?.category} | Passing Score: {exam?.passing_marks} marks</p>
        </div>
      </div>

      {leaderboard.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm">
          <Trophy className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-slate-700">No attempts submitted yet</h3>
          <p className="text-slate-400 text-sm mt-1">Results and rankings will appear here once students submit their exams.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 font-semibold text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3.5 text-center w-16">Rank</th>
                <th className="px-6 py-3.5">Student Name</th>
                <th className="px-6 py-3.5">Score</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5 text-center">Tab Switches</th>
                <th className="px-6 py-3.5 text-right">Submitted At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {leaderboard.map((lb) => (
                <tr key={lb.student_id} className="hover:bg-slate-50/80 transition">
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full font-bold text-xs ${
                      lb.rank === 1 ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                      lb.rank === 2 ? 'bg-slate-200 text-slate-800' :
                      lb.rank === 3 ? 'bg-amber-700/10 text-amber-900' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {lb.rank}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-semibold text-slate-900">{lb.student_name}</td>
                  <td className="px-6 py-4 font-bold text-blue-600">{lb.score} / {lb.total_possible_score}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                      lb.passed ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
                    }`}>
                      {lb.passed ? <CheckCircle className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
                      <span>{lb.passed ? 'PASSED' : 'FAILED'}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {lb.tab_switches > 0 ? (
                      <span className="inline-flex items-center space-x-1 text-amber-600 font-semibold bg-amber-50 px-2 py-0.5 rounded text-xs">
                        <AlertTriangle className="h-3.5 w-3.5" />
                        <span>{lb.tab_switches} warnings</span>
                      </span>
                    ) : (
                      <span className="text-slate-400 text-xs">0 warnings</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right text-xs text-slate-500">
                    {new Date(lb.submitted_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
