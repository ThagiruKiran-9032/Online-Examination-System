import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';

import { Login } from './pages/Login';
import { Register } from './pages/Register';

import { AdminDashboard } from './pages/admin/Dashboard';
import { QuestionManager } from './pages/admin/QuestionManager';
import { StudentManager } from './pages/admin/StudentManager';
import { ExamResults } from './pages/admin/ExamResults';

import { StudentDashboard } from './pages/student/Dashboard';
import { TakeExam } from './pages/student/TakeExam';
import { ExamResult } from './pages/student/ExamResult';
import { ResultsList } from './pages/student/ResultsList';
import { StudentLeaderboard } from './pages/student/Leaderboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-slate-50 flex flex-col">
          <Navbar />
          <div className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Admin Protected Routes */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/exams/:examId/questions"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <QuestionManager />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/students"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <StudentManager />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/exams/:examId/results"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <ExamResults />
                  </ProtectedRoute>
                }
              />

              {/* Student Protected Routes */}
              <Route
                path="/student"
                element={
                  <ProtectedRoute requiredRole="student">
                    <StudentDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/student/results"
                element={
                  <ProtectedRoute requiredRole="student">
                    <ResultsList />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/student/attempt/:attemptId"
                element={
                  <ProtectedRoute requiredRole="student">
                    <TakeExam />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/student/result/:attemptId"
                element={
                  <ProtectedRoute requiredRole="student">
                    <ExamResult />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/student/exams/:examId/leaderboard"
                element={
                  <ProtectedRoute requiredRole="student">
                    <StudentLeaderboard />
                  </ProtectedRoute>
                }
              />

              {/* Catch all redirect */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
