import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery } from 'react-query'
import { dashboardApi, instagramApi } from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'

interface DashboardStats {
  total_accounts: number
  active_accounts: number
  total_followers: number
  total_posts: number
  total_media: number
  scheduled_posts: number
  engagement_rate: number
  top_performing_accounts: any[]
}

export interface InstagramAccount {
  id: number
  username: string
  full_name?: string
  followers_count: number
  following_count: number
  posts_count: number
  media_count: number
  is_active: boolean
  is_business_account: boolean
  is_business: boolean
  is_connected: boolean
  profile_picture_url?: string
  last_sync?: string
  created_at: string
  engagement_rate?: number
  account_type?: string
  permissions: string[]
  recent_posts_performance?: {
    avg_likes: number
    avg_comments: number
    trend: 'up' | 'down' | 'stable'
  }
}

interface FilterType {
  dateRange: string
  accountId: number | null
  postType: string
}

interface DashboardContextType {
  stats: DashboardStats | null
  accounts: InstagramAccount[]
  selectedAccount: InstagramAccount | null
  loading: boolean
  error: string | null
  refreshStats: () => void
  refreshAccounts: () => void
  selectAccount: (account: InstagramAccount | null) => void
  setFilter: (filter: FilterType) => void
  filter: FilterType
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

interface DashboardProviderProps {
  children: ReactNode
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children }) => {
  const [selectedAccount, setSelectedAccount] = useState<InstagramAccount | null>(null)
  const [filter, setFilter] = useState<FilterType>({
    dateRange: '30d',
    accountId: null,
    postType: 'all'
  })
  const { isAuthenticated } = useAuth()

  // Query per dashboard stats
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats
  } = useQuery('dashboard-stats', dashboardApi.getStats, {
    refetchInterval: 5 * 60 * 1000, // Refresh ogni 5 minuti
    staleTime: 2 * 60 * 1000, // Considera stale dopo 2 minuti
    enabled: isAuthenticated,
  })

  // Query per instagram accounts
  const {
    data: accounts = [],
    isLoading: accountsLoading,
    error: accountsError,
    refetch: refetchAccounts
  } = useQuery('instagram-accounts', instagramApi.getAccounts, {
    refetchInterval: 10 * 60 * 1000, // Refresh ogni 10 minuti
    staleTime: 5 * 60 * 1000,
    enabled: isAuthenticated,
  })

  const loading = statsLoading || accountsLoading
  const error = statsError || accountsError

  const selectAccount = (account: InstagramAccount | null) => {
    setSelectedAccount(account)
    setFilter(prev => ({
      ...prev,
      accountId: account?.id || null
    }))
  }

  const refreshStats = () => {
    refetchStats()
  }

  const refreshAccounts = () => {
    refetchAccounts()
  }

  // Auto-seleziona primo account se nessuno selezionato
  useEffect(() => {
    if (!selectedAccount && accounts.length > 0) {
      setSelectedAccount(accounts[0])
    }
  }, [accounts, selectedAccount])

  const value: DashboardContextType = {
    stats: stats || null,
    accounts,
    selectedAccount,
    loading,
    error: (error as any)?.message || null,
    refreshStats,
    refreshAccounts,
    selectAccount,
    setFilter,
    filter,
  }

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

export const useDashboard = () => {
  const context = useContext(DashboardContext)
  if (context === undefined) {
    throw new Error('useDashboard deve essere usato dentro DashboardProvider')
  }
  return context
}
