import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/axios';
import { CheckCircle, XCircle, Trophy, ArrowLeft, AlertTriangle, Award } from 'lucide-react';

export const ExamResult = () => {
  const { attemptId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResult = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/attempts/${attemptId}/result`);
        setResult(res.data);
      } catch (err) {
        console.error("Failed to load attempt result:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [attemptId]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-slate-600">
        Result not found.
      </div>
    );
  }

  const percentage = result.total_possible_score > 0
    ? Math.round((result.score / result.total_possible_score) * 100)
    : 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <Link to="/student" className="inline-flex items-center space-x-2 text-sm font-semibold text-slate-600 hover:text-slate-900 transition">
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Dashboard</span>
        </Link>

        <Link
          to={`/student/exams/${result.exam_id}/leaderboard`}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold text-xs rounded-xl shadow-sm transition"
        >
          <Trophy className="h-4 w-4" />
          <span>View Exam Leaderboard</span>
        </Link>
      </div>

      {/* Result Card Banner */}
      <div className={`rounded-3xl p-8 text-white shadow-xl mb-8 border ${
        result.passed
          ? 'bg-gradient-to-r from-emerald-800 to-green-900 border-green-700/50'
          : 'bg-gradient-to-r from-slate-900 to-rose-950 border-rose-900/50'
      }`}>
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-white/10 border border-white/20 uppercase tracking-wider">
              {result.category}
            </span>
            <h1 className="text-3xl font-extrabold mt-2">{result.exam_title}</h1>
            <p className="text-white/80 text-sm mt-1">Submitted on {new Date(result.end_time || result.start_time).toLocaleString()}</p>
          </div>

          <div className="mt-6 md:mt-0 flex items-center space-x-4">
            <div className="text-center bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/20 min-w-[120px]">
              <div className="text-3xl font-black">{result.score} / {result.total_possible_score}</div>
              <div className="text-xs text-white/80 uppercase font-semibold mt-1">Total Score</div>
            </div>

            <div className="text-center bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/20 min-w-[100px]">
              <div className="text-3xl font-black">{percentage}%</div>
              <div className="text-xs text-white/80 uppercase font-semibold mt-1">Percentage</div>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-white/10 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {result.passed ? (
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-sm font-bold bg-green-400 text-slate-950">
                <CheckCircle className="h-4 w-4" />
                <span>PASSED</span>
              </span>
            ) : (
              <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-sm font-bold bg-rose-500 text-white">
                <XCircle className="h-4 w-4" />
                <span>FAILED</span>
              </span>
            )}
            <span className="text-xs text-white/80">(Passing mark: {result.passing_marks})</span>
          </div>

          {result.tab_switches > 0 && (
            <div className="flex items-center space-x-1.5 text-amber-300 text-xs font-semibold bg-amber-500/20 border border-amber-500/30 px-3 py-1 rounded-full">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <span>{result.tab_switches} Tab Switch Warnings</span>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Question Review */}
      <h2 className="text-xl font-bold text-slate-900 mb-4">Detailed Question Review</h2>

      <div className="space-y-4">
        {result.questions_review.map((q, idx) => (
          <div key={q.question_id} className={`bg-white p-6 rounded-2xl border shadow-sm ${
            q.is_correct ? 'border-green-200' : 'border-red-200'
          }`}>
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center">
                  {idx + 1}
                </span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                  q.is_correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {q.is_correct ? 'Correct (+1 mark)' : 'Incorrect (0 marks)'}
                </span>
              </div>
            </div>

            <h3 className="text-base font-bold text-slate-900 mb-4">{q.question_text}</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {q.options.map((opt, oIdx) => {
                const isUserSelected = q.selected_option === String(oIdx) || q.selected_option === opt;
                const isCorrectOpt = String(oIdx) === String(q.correct_answer) || opt === q.correct_answer;

                let optStyle = "bg-slate-50 border-slate-200 text-slate-700";
                if (isCorrectOpt) optStyle = "bg-green-50 border-green-400 text-green-900 font-bold";
                else if (isUserSelected && !isCorrectOpt) optStyle = "bg-red-50 border-red-400 text-red-900 font-bold";

                return (
                  <div key={oIdx} className={`p-3 rounded-xl text-sm border flex items-center justify-between ${optStyle}`}>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-xs">{String.fromCharCode(65 + oIdx)}.</span>
                      <span>{opt}</span>
                    </div>

                    {isCorrectOpt && <span className="text-xs font-bold text-green-700">✓ Correct</span>}
                    {isUserSelected && !isCorrectOpt && <span className="text-xs font-bold text-red-700">✗ Your Choice</span>}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
