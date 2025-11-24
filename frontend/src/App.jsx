import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import OrganizationDashboard from './pages/OrganizationDashboard';
import EmployeeDashboard from './pages/EmployeeDashboard';
import './index.css';

// Protected Route Component
const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  // Super admin and admin can access organization dashboard
  if (adminOnly && user.role !== 'admin' && user.role !== 'super_admin') {
    return <Navigate to="/employee" />;
  }
  
  return children;
};

// Main App Component
function AppRoutes() {
  const { isAuthenticated, isAdmin } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to={isAdmin ? '/organization' : '/employee'} replace />
          ) : (
            <Login />
          )
        }
      />
      <Route
        path="/organization"
        element={
          <ProtectedRoute adminOnly>
            <OrganizationDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/employee"
        element={
          <ProtectedRoute>
            <EmployeeDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/"
        element={
          <Navigate
            to={isAuthenticated ? (isAdmin ? '/organization' : '/employee') : '/login'}
            replace
          />
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
