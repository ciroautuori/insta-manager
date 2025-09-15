import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { AuthProvider } from '@/contexts/AuthContext'
import { DashboardProvider } from '@/contexts/DashboardContext'
import { Toaster } from '@/components/ui/toast'
import ProtectedRoute from '@/components/ProtectedRoute'
import Layout from '@/components/layout/Layout'
import Login from '@/pages/Login'
import Dashboard from '@/pages/Dashboard'
import Accounts from '@/pages/Accounts'
import Posts from '@/pages/Posts'
import Scheduled from '@/pages/Scheduled'
import './App.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route 
              path="/*" 
              element={
                <ProtectedRoute>
                  <DashboardProvider>
                    <Layout />
                  </DashboardProvider>
                </ProtectedRoute>
              }
            >
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="accounts" element={<Accounts />} />
              <Route path="posts" element={<Posts />} />
              <Route path="scheduled" element={<Scheduled />} />
              <Route 
                path="media" 
                element={<div>Media Management (Placeholder)</div>} 
              />
              <Route 
                path="calendar" 
                element={<div>Calendar View (Placeholder)</div>} 
              />
              <Route 
                path="analytics" 
                element={<div>Analytics Dashboard (Placeholder)</div>} 
              />
              <Route index element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
          <Toaster />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
