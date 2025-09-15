import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, api } from '../lib/api'

interface Admin {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  last_login?: string
}

interface AuthContextType {
  isAuthenticated: boolean
  admin: Admin | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshAdmin: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [admin, setAdmin] = useState<Admin | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verifica se utente è già autenticato
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (token) {
        // Imposta header Authorization di default per tutte le richieste
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        // Verifica lato server: se fallisce, pulisci stato ma NON fare redirect qui
        try {
          const adminData = await authApi.getCurrentAdmin()
          localStorage.setItem('admin_data', JSON.stringify(adminData))
          setAdmin(adminData)
          setIsAuthenticated(true)
        } catch (err) {
          console.error('Auth non valida, pulizia stato:', err)
          localStorage.removeItem('auth_token')
          localStorage.removeItem('admin_data')
          setAdmin(null)
          setIsAuthenticated(false)
          delete api.defaults.headers.common['Authorization']
        }
      }
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      setLoading(true)
      
      // Login API call
      const tokenData = await authApi.login(email, password)
      
      // Salva token immediatamente
      localStorage.setItem('auth_token', tokenData.access_token)
      
      // Forza il refresh degli interceptors
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`
      
      // Ottieni dati admin
      const adminData = await authApi.getCurrentAdmin()
      
      // Salva dati admin
      localStorage.setItem('admin_data', JSON.stringify(adminData))
      
      setAdmin(adminData)
      setIsAuthenticated(true)
      
      // Naviga alla dashboard dopo aver settato tutto
      window.location.href = '/'
      
    } catch (error: any) {
      console.error('Errore login:', error)
      
      // Pulisci storage in caso di errore
      localStorage.removeItem('auth_token')
      localStorage.removeItem('admin_data')
      delete api.defaults.headers.common['Authorization']
      
      throw new Error(
        error.response?.data?.detail || 
        'Errore durante il login. Verifica le credenziali.'
      )
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('admin_data')
    setAdmin(null)
    setIsAuthenticated(false)
    delete api.defaults.headers.common['Authorization']
    
    // Redirect a login
    window.location.href = '/login'
  }

  const refreshAdmin = async () => {
    try {
      const adminData = await authApi.getCurrentAdmin()
      localStorage.setItem('admin_data', JSON.stringify(adminData))
      setAdmin(adminData)
    } catch (error) {
      console.error('Errore refresh admin:', error)
      // Non reindirizzare qui: evita loop. Lascia che ProtectedRoute gestisca.
      localStorage.removeItem('auth_token')
      localStorage.removeItem('admin_data')
      setAdmin(null)
      setIsAuthenticated(false)
      throw error
    }
  }

  const value: AuthContextType = {
    isAuthenticated,
    admin,
    loading,
    login,
    logout,
    refreshAdmin,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth deve essere usato dentro AuthProvider')
  }
  return context
}
