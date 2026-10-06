import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import { Clock, AlertTriangle, ChevronLeft, ChevronRight, CheckCircle, Send, Flag } from 'lucide-react';

export const TakeExam = () => {
  const { attemptId } = useParams();
  const navigate = useNavigate();

  const [attemptData, setAttemptData] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [flagged, setFlagged] = useState({});
  const [timeLeftSeconds, setTimeLeftSeconds] = useState(null);
  const [tabSwitches, setTabSwitches] = useState(0);
  const [warningBanner, setWarningBanner] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const submittingRef = useRef(false);

  // 1. Check if attempt already completed
  useEffect(() => {
    const fetchAttempt = async () => {
      try {
        const res = await api.get(`/attempts/${attemptId}/result`);
        if (res.data.status === 'completed' || res.data.status === 'time_expired') {
          navigate(`/student/result/${attemptId}`, { replace: true });
          return;
        }
      } catch (err) {
        // Attempt in progress
      }
    };
    fetchAttempt();
  }, [attemptId, navigate]);

  // 2. Load attempt data & initialize countdown timer safely
  useEffect(() => {
    const init = async () => {
      try {
        const res = await api.get(`/attempts/${attemptId}/result`);
        const data = res.data;

        setAttemptData(data);
        setTabSwitches(data.tab_switches || 0);

        // Safe timestamp & duration calculation
        const durationMins = Number(data.duration_minutes) || 15;
        const durationSec = durationMins * 60;
        
        let startMs = new Date(data.start_time).getTime();
        if (isNaN(startMs)) {
          startMs = Date.now();
        }
        
        const targetTimeMs = startMs + (durationSec * 1000);
        const elapsedSec = Math.floor((Date.now() - startMs) / 1000);
        const remainingSec = Math.max(0, durationSec - elapsedSec);

        setTimeLeftSeconds(isNaN(remainingSec) ? durationSec : remainingSec);
      } catch (err) {
        console.error("Failed to load attempt runner:", err);
      }
    };
    init();
  }, [attemptId]);

  // 3. Anti-cheating Tab-switch Detector
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.hidden && !submittingRef.current) {
        setWarningBanner(true);
        setTabSwitches(prev => prev + 1);
        try {
          await api.post(`/attempts/${attemptId}/record-warning`, { warning_type: "tab_switch" });
        } catch (e) {
          console.error("Warning record error:", e);
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [attemptId]);

  // 4. Submit Handler
  const handleSubmitExam = useCallback(async (isAutoSubmit = false) => {
    if (submittingRef.current) return;
    submittingRef.current = true;
    setSubmitting(true);

    try {
      const payload = { answers };
      await api.post(`/attempts/${attemptId}/submit`, payload);
      navigate(`/student/result/${attemptId}`, { replace: true });
    } catch (err) {
      console.error("Submission failed:", err);
      submittingRef.current = false;
      setSubmitting(false);
      alert("Failed to submit exam. Please try again.");
    }
  }, [answers, attemptId, navigate]);

  // 5. Active Ticking Countdown Timer
  useEffect(() => {
    if (timeLeftSeconds === null) return;
    if (timeLeftSeconds <= 0) {
      handleSubmitExam(true);
      return;
    }

    const timerId = setInterval(() => {
      setTimeLeftSeconds(prev => {
        if (prev <= 1) {
          clearInterval(timerId);
          handleSubmitExam(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerId);
  }, [timeLeftSeconds, handleSubmitExam]);

  if (!attemptData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-sm font-medium">Initializing Exam Runner...</p>
        </div>
      </div>
    );
  }

  const questions = attemptData.questions_review || [];
  const currentQ = questions[currentIndex];

  const formatTimer = (seconds) => {
    if (seconds === null || isNaN(seconds)) return "00:00";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const handleSelectOption = (optIndex) => {
    setAnswers(prev => ({
      ...prev,
      [currentQ.question_id]: String(optIndex)
    }));
  };

  const toggleFlag = (qId) => {
    setFlagged(prev => ({ ...prev, [qId]: !prev[qId] }));
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-between">
      {/* Clean Top Bar (Exam Info & Tab Switch Alerts) */}
      <header className="bg-slate-900 text-white sticky top-0 z-50 shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="px-2.5 py-0.5 rounded-md text-xs font-bold bg-blue-600/30 text-blue-300 border border-blue-500/30">
              {attemptData.category}
            </span>
            <h1 className="text-lg font-bold text-white leading-tight">{attemptData.exam_title}</h1>
          </div>

          <div>
            {tabSwitches > 0 && (
              <div className="flex items-center space-x-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/30 px-3 py-1 rounded-full text-xs font-semibold">
                <AlertTriangle className="h-4 w-4 text-amber-400" />
                <span>{tabSwitches} Tab Switch Warnings</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Anti-Cheating Warning Banner */}
      {warningBanner && (
        <div className="bg-amber-500 text-slate-900 px-4 py-2.5 text-center text-sm font-semibold flex items-center justify-center space-x-2 shadow-inner">
          <AlertTriangle className="h-5 w-5 flex-shrink-0" />
          <span>Warning: Switching tabs or leaving the window is recorded as anti-cheating violations!</span>
          <button onClick={() => setWarningBanner(false)} className="underline ml-4 text-xs font-bold">Dismiss</button>
        </div>
      )}

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 py-6 flex-1 w-full grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left: Question Card */}
        <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center border-b border-slate-100 pb-4 mb-4">
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                Question {currentIndex + 1} of {questions.length}
              </span>
              <button
                onClick={() => toggleFlag(currentQ.question_id)}
                className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition flex items-center space-x-1 ${
                  flagged[currentQ.question_id] 
                    ? 'bg-amber-100 text-amber-800 border border-amber-300' 
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <Flag className="h-3.5 w-3.5" />
                <span>{flagged[currentQ.question_id] ? 'Flagged for Review' : 'Flag Question'}</span>
              </button>
            </div>

            <h2 className="text-lg font-bold text-slate-900 mb-6">{currentQ.question_text}</h2>

            {/* Options List */}
            <div className="space-y-3">
              {currentQ.options.map((opt, oIdx) => {
                const isSelected = answers[currentQ.question_id] === String(oIdx);
                return (
                  <button
                    key={oIdx}
                    onClick={() => handleSelectOption(oIdx)}
                    className={`w-full text-left p-4 rounded-xl border-2 transition flex items-center justify-between ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/60 text-blue-900 font-semibold'
                        : 'border-slate-200 hover:border-slate-300 bg-white text-slate-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${
                        isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {String.fromCharCode(65 + oIdx)}
                      </span>
                      <span>{opt}</span>
                    </div>
                    {isSelected && <CheckCircle className="h-5 w-5 text-blue-600" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Previous / Next Question Controls */}
          <div className="flex justify-between items-center pt-6 border-t border-slate-100 mt-8">
            <button
              onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="flex items-center space-x-1 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold disabled:opacity-40 transition"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>

            <button
              onClick={() => setCurrentIndex(prev => Math.min(questions.length - 1, prev + 1))}
              disabled={currentIndex === questions.length - 1}
              className="flex items-center space-x-1 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold disabled:opacity-40 transition"
            >
              <span>Next</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Right Sidebar: Prominent Timer & Question Palette */}
        <div className="space-y-6">
          {/* Prominent Sidebar Countdown Timer Card */}
          <div className="bg-slate-900 text-white rounded-2xl p-5 border border-slate-800 shadow-md text-center">
            <div className="flex items-center justify-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              <Clock className="h-4 w-4 text-blue-400" />
              <span>Time Remaining</span>
            </div>
            <div className={`text-4xl font-mono font-black tracking-tight my-1 ${
              timeLeftSeconds !== null && timeLeftSeconds < 300 ? 'text-red-400 animate-pulse' : 'text-blue-400'
            }`}>
              {formatTimer(timeLeftSeconds)}
            </div>
            <div className="text-[10px] text-slate-500">Auto-submits when countdown reaches 00:00</div>
          </div>

          {/* Question Navigation Palette */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-4">Question Palette</h3>
              
              <div className="grid grid-cols-5 gap-2">
                {questions.map((q, idx) => {
                  const isAnswered = answers[q.question_id] !== undefined;
                  const isFlagged = flagged[q.question_id];
                  const isCurrent = idx === currentIndex;

                  let btnStyle = "bg-slate-100 text-slate-700 border-slate-200";
                  if (isCurrent) btnStyle = "ring-2 ring-blue-600 bg-blue-600 text-white font-bold";
                  else if (isAnswered) btnStyle = "bg-green-600 text-white font-bold border-green-600";
                  else if (isFlagged) btnStyle = "bg-amber-400 text-slate-900 font-bold border-amber-500";

                  return (
                    <button
                      key={q.question_id}
                      onClick={() => setCurrentIndex(idx)}
                      className={`h-10 rounded-lg text-xs font-semibold flex items-center justify-center transition border ${btnStyle}`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>

              <div className="mt-6 space-y-2 text-xs text-slate-600 pt-4 border-t border-slate-100">
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-green-600 inline-block"></span>
                  <span>Answered</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-amber-400 inline-block"></span>
                  <span>Flagged for Review</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3.5 h-3.5 rounded bg-slate-100 border border-slate-300 inline-block"></span>
                  <span>Unanswered</span>
                </div>
              </div>
            </div>

            {/* Single Action Button at Bottom of Sidebar */}
            <button
              onClick={() => handleSubmitExam(false)}
              disabled={submitting}
              className="w-full mt-6 flex items-center justify-center space-x-2 py-3 bg-green-600 hover:bg-green-500 text-white font-bold text-sm rounded-xl transition shadow-sm"
            >
              <Send className="h-4 w-4" />
              <span>{submitting ? 'Submitting...' : 'Finish & Submit Exam'}</span>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
