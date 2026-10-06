import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api/axios';
import { Plus, Edit, Trash2, Eye, EyeOff, BookOpen, Clock, Award, HelpCircle, Filter } from 'lucide-react';

const CATEGORIES = ["All", "Numeric", "Logic & Reasoning", "English", "General Knowledge", "Technical"];

export const AdminDashboard = () => {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [showModal, setShowModal] = useState(false);
  const [editingExam, setEditingExam] = useState(null);

  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('General Knowledge');
  const [durationMinutes, setDurationMinutes] = useState(30);
  const [passingMarks, setPassingMarks] = useState(1);
  const [maxAttempts, setMaxAttempts] = useState(1);

  const fetchExams = async () => {
    setLoading(true);
    try {
      const url = selectedCategory === "All" ? '/exams/' : `/exams/?category=${encodeURIComponent(selectedCategory)}`;
      const res = await api.get(url);
      setExams(res.data);
    } catch (err) {
      console.error("Failed to fetch exams:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExams();
  }, [selectedCategory]);

  const handleOpenModal = (exam = null) => {
    if (exam) {
      setEditingExam(exam);
      setTitle(exam.title);
      setDescription(exam.description || '');
      setCategory(exam.category);
      setDurationMinutes(exam.duration_minutes);
      setPassingMarks(exam.passing_marks);
      setMaxAttempts(exam.max_attempts);
    } else {
      setEditingExam(null);
      setTitle('');
      setDescription('');
      setCategory('General Knowledge');
      setDurationMinutes(30);
      setPassingMarks(1);
      setMaxAttempts(1);
    }
    setShowModal(true);
  };

  const handleSaveExam = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        title,
        description,
        category,
        duration_minutes: Number(durationMinutes),
        passing_marks: Number(passingMarks),
        max_attempts: Number(maxAttempts),
      };

      if (editingExam) {
        await api.put(`/exams/${editingExam.id}`, payload);
      } else {
        await api.post('/exams/', payload);
      }
      setShowModal(false);
      fetchExams();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to save exam");
    }
  };

  const handleTogglePublish = async (id) => {
    try {
      await api.patch(`/exams/${id}/publish`);
      fetchExams();
    } catch (err) {
      alert("Failed to toggle publish status");
    }
  };

  const handleDeleteExam = async (id) => {
    if (!window.confirm("Are you sure you want to delete this exam and all its questions?")) return;
    try {
      await api.delete(`/exams/${id}`);
      fetchExams();
    } catch (err) {
      alert("Failed to delete exam");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Exam Management Console</h1>
          <p className="text-slate-500 text-sm mt-1">Create, manage, and publish exams across categories</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="mt-4 md:mt-0 inline-flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-sm text-sm transition"
        >
          <Plus className="h-5 w-5" />
          <span>Create New Exam</span>
        </button>
      </div>

      {/* Category Filters */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-4 mb-6 border-b border-slate-200">
        <Filter className="h-4 w-4 text-slate-400 mr-2 flex-shrink-0" />
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition ${
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
          <h3 className="text-lg font-semibold text-slate-700">No exams found</h3>
          <p className="text-slate-400 text-sm mt-1">Get started by creating a new exam above.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.map((exam) => (
            <div key={exam.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between p-6">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                    {exam.category}
                  </span>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                    exam.is_published ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}>
                    {exam.is_published ? 'Published' : 'Draft'}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-slate-900 line-clamp-1">{exam.title}</h3>
                <p className="text-slate-500 text-sm mt-1 line-clamp-2 h-10">{exam.description || 'No description provided.'}</p>

                <div className="grid grid-cols-3 gap-2 my-4 p-3 bg-slate-50 rounded-xl text-xs text-slate-600 border border-slate-100">
                  <div className="flex flex-col items-center">
                    <Clock className="h-4 w-4 text-slate-400 mb-1" />
                    <span>{exam.duration_minutes} mins</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <HelpCircle className="h-4 w-4 text-slate-400 mb-1" />
                    <span>{exam.total_questions} Questions</span>
                  </div>
                  <div className="flex flex-col items-center">
                    <Award className="h-4 w-4 text-slate-400 mb-1" />
                    <span>Pass: {exam.passing_marks}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 space-y-2">
                <div className="flex items-center justify-between space-x-2">
                  <Link
                    to={`/admin/exams/${exam.id}/questions`}
                    className="flex-1 text-center py-2 bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs rounded-lg transition"
                  >
                    Build Questions ({exam.total_questions})
                  </Link>

                  <Link
                    to={`/admin/exams/${exam.id}/results`}
                    className="py-2 px-3 bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium text-xs rounded-lg transition"
                  >
                    Results & Leaderboard
                  </Link>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
                  <button
                    onClick={() => handleTogglePublish(exam.id)}
                    className="flex items-center space-x-1 hover:text-blue-600 transition"
                  >
                    {exam.is_published ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    <span>{exam.is_published ? 'Unpublish' : 'Publish'}</span>
                  </button>

                  <div className="flex items-center space-x-3">
                    <button onClick={() => handleOpenModal(exam)} className="hover:text-amber-600 transition" title="Edit Exam">
                      <Edit className="h-4 w-4" />
                    </button>
                    <button onClick={() => handleDeleteExam(exam.id)} className="hover:text-red-600 transition" title="Delete Exam">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Exam Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100">
            <h2 className="text-xl font-bold text-slate-900 mb-4">{editingExam ? 'Edit Exam' : 'Create New Exam'}</h2>
            <form onSubmit={handleSaveExam} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Exam Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Logical Reasoning Test 1"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Category / Subject</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="Numeric">Numeric</option>
                  <option value="Logic & Reasoning">Logic & Reasoning</option>
                  <option value="English">English</option>
                  <option value="General Knowledge">General Knowledge</option>
                  <option value="Technical">Technical</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Short summary of exam scope"
                  rows={2}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Duration (Mins)</label>
                  <input
                    type="number"
                    min={1}
                    value={durationMinutes}
                    onChange={(e) => setDurationMinutes(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Pass Marks</label>
                  <input
                    type="number"
                    min={1}
                    value={passingMarks}
                    onChange={(e) => setPassingMarks(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Max Attempts</label>
                  <input
                    type="number"
                    min={1}
                    value={maxAttempts}
                    onChange={(e) => setMaxAttempts(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
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
                  Save Exam
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
