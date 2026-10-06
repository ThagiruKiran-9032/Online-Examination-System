import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api/axios';
import { ArrowLeft, Plus, Trash2, Edit, CheckCircle, HelpCircle } from 'lucide-react';

export const QuestionManager = () => {
  const { examId } = useParams();
  const [exam, setExam] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);

  // Question Form State
  const [questionText, setQuestionText] = useState('');
  const [questionType, setQuestionType] = useState('mcq');  // 'mcq' or 'true_false'
  const [options, setOptions] = useState(['', '', '', '']);
  const [correctAnswer, setCorrectAnswer] = useState('0');
  const [marks, setMarks] = useState(1);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [examRes, qRes] = await Promise.all([
        api.get(`/exams/${examId}`),
        api.get(`/exams/${examId}/questions`)
      ]);
      setExam(examRes.data);
      setQuestions(qRes.data);
    } catch (err) {
      console.error("Failed to load question manager:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [examId]);

  const handleOpenModal = (q = null) => {
    if (q) {
      setEditingQuestion(q);
      setQuestionText(q.question_text);
      setQuestionType(q.question_type);
      setOptions(q.options || []);
      setCorrectAnswer(String(q.correct_answer));
      setMarks(q.marks);
    } else {
      setEditingQuestion(null);
      setQuestionText('');
      setQuestionType('mcq');
      setOptions(['', '', '', '']);
      setCorrectAnswer('0');
      setMarks(1);
    }
    setShowModal(true);
  };

  const handleQuestionTypeChange = (type) => {
    setQuestionType(type);
    if (type === 'true_false') {
      setOptions(['True', 'False']);
      setCorrectAnswer('0');
    } else {
      setOptions(['', '', '', '']);
      setCorrectAnswer('0');
    }
  };

  const handleOptionChange = (idx, value) => {
    const newOptions = [...options];
    newOptions[idx] = value;
    setOptions(newOptions);
  };

  const handleSaveQuestion = async (e) => {
    e.preventDefault();
    if (!questionText.trim()) return alert("Question text is required");

    const payload = {
      question_text: questionText,
      question_type: questionType,
      options: options,
      correct_answer: String(correctAnswer),
      marks: Number(marks)
    };

    try {
      if (editingQuestion) {
        await api.put(`/questions/${editingQuestion.id}`, payload);
      } else {
        await api.post(`/exams/${examId}/questions`, payload);
      }
      setShowModal(false);
      fetchData();
    } catch (err) {
      alert("Failed to save question");
    }
  };

  const handleDeleteQuestion = async (qId) => {
    if (!window.confirm("Delete this question?")) return;
    try {
      await api.delete(`/questions/${qId}`);
      fetchData();
    } catch (err) {
      alert("Failed to delete question");
    }
  };

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
          <h1 className="text-2xl font-bold text-slate-900">{exam?.title} - Question Builder</h1>
          <p className="text-slate-500 text-sm">{questions.length} questions configured ({exam?.category})</p>
        </div>
      </div>

      <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 mb-6 shadow-sm">
        <div className="text-sm text-slate-600">
          Total Exam Marks: <span className="font-bold text-slate-900">{questions.reduce((acc, q) => acc + q.marks, 0)}</span> | Passing Marks: <span className="font-bold text-slate-900">{exam?.passing_marks}</span>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-lg shadow-sm transition"
        >
          <Plus className="h-4 w-4" />
          <span>Add Question</span>
        </button>
      </div>

      {questions.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 shadow-sm">
          <HelpCircle className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-slate-700">No questions added yet</h3>
          <p className="text-slate-400 text-sm mt-1">Add MCQs or True/False questions to build this exam.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {questions.map((q, index) => (
            <div key={q.id} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center">
                    {index + 1}
                  </span>
                  <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-600 uppercase">
                    {q.question_type === 'mcq' ? 'Multiple Choice' : 'True / False'}
                  </span>
                  <span className="text-xs text-slate-400">({q.marks} mark)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <button onClick={() => handleOpenModal(q)} className="text-slate-400 hover:text-amber-600 p-1" title="Edit">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button onClick={() => handleDeleteQuestion(q.id)} className="text-slate-400 hover:text-red-600 p-1" title="Delete">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <h4 className="text-base font-semibold text-slate-900 mb-3">{q.question_text}</h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {q.options.map((opt, oIdx) => {
                  const isCorrect = String(oIdx) === String(q.correct_answer) || opt === q.correct_answer;
                  return (
                    <div
                      key={oIdx}
                      className={`p-2.5 rounded-lg text-sm flex items-center justify-between border ${
                        isCorrect
                          ? 'bg-green-50 border-green-300 text-green-800 font-medium'
                          : 'bg-slate-50 border-slate-200 text-slate-700'
                      }`}
                    >
                      <span>{opt}</span>
                      {isCorrect && <CheckCircle className="h-4 w-4 text-green-600" />}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add / Edit Question Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-slate-900 mb-4">{editingQuestion ? 'Edit Question' : 'Add New Question'}</h2>
            <form onSubmit={handleSaveQuestion} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Question Type</label>
                <select
                  value={questionType}
                  onChange={(e) => handleQuestionTypeChange(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="mcq">Multiple Choice (MCQ)</option>
                  <option value="true_false">True / False</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Question Text</label>
                <textarea
                  required
                  rows={3}
                  value={questionText}
                  onChange={(e) => setQuestionText(e.target.value)}
                  placeholder="Enter the question text here..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              {questionType === 'mcq' ? (
                <div className="space-y-2">
                  <label className="block text-xs font-semibold text-slate-700 uppercase">Options (Select radio for correct answer)</label>
                  {options.map((opt, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                      <input
                        type="radio"
                        name="correctOpt"
                        checked={String(correctAnswer) === String(idx)}
                        onChange={() => setCorrectAnswer(String(idx))}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                      />
                      <input
                        type="text"
                        required
                        value={opt}
                        onChange={(e) => handleOptionChange(idx, e.target.value)}
                        placeholder={`Option ${idx + 1}`}
                        className="flex-1 px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  <label className="block text-xs font-semibold text-slate-700 uppercase">Select Correct Answer</label>
                  <div className="flex space-x-4">
                    <label className="flex items-center space-x-2 text-sm font-medium">
                      <input
                        type="radio"
                        name="tfAnswer"
                        checked={String(correctAnswer) === '0'}
                        onChange={() => setCorrectAnswer('0')}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span>True</span>
                    </label>
                    <label className="flex items-center space-x-2 text-sm font-medium">
                      <input
                        type="radio"
                        name="tfAnswer"
                        checked={String(correctAnswer) === '1'}
                        onChange={() => setCorrectAnswer('1')}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span>False</span>
                    </label>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Marks</label>
                <input
                  type="number"
                  min={1}
                  value={marks}
                  onChange={(e) => setMarks(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition shadow-sm"
                >
                  Save Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
