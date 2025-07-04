import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/useAuth";
import LoginPage from "./auth/LoginPage";
import LandingPage from "./pages/LandingPage";
import NotFound from "./pages/NotFound";
import Dashboard from "./components/Dashboard";
import AnalyticsPage from "./pages/AnalyticsPage";
import Layout from "./components/Layout";
import BatchUploadPage from "./pages/BatchUploadPage";
import AssessmentHistoryPage from "./pages/AssessmentHistoryPage";
import SettingsPage from "./pages/SettingsPage";
import HelpPage from "./pages/HelpPage";
import CompanyAnalyticsDashboardWrapper from "./components/CompanyAnalyticsDashboardWrapper";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const RouterConfig = () => {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout currentPage="search">
              <LandingPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout currentPage="dashboard">
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <ProtectedRoute>
            <Layout currentPage="analytics">
              <AnalyticsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <Layout currentPage="history">
              <AssessmentHistoryPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/batch"
        element={
          <ProtectedRoute>
            <Layout currentPage="batch">
              <BatchUploadPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Layout currentPage="settings">
              <SettingsPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/help"
        element={
          <ProtectedRoute>
            <Layout currentPage="help">
              <HelpPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/companies/:companyName/analytics"
        element={
          <ProtectedRoute>
            <Layout currentPage="analytics">
              <CompanyAnalyticsDashboardWrapper />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="/login" element={<LoginPage />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};
