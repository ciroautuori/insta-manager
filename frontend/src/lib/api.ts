import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Se esiste già un token salvato, imposta l'header Authorization a livello globale
try {
  const existingToken = localStorage.getItem('auth_token')
  if (existingToken) {
    api.defaults.headers.common['Authorization'] = `Bearer ${existingToken}`
  }
} catch (_) {
  // In ambienti non-browser, localStorage potrebbe non essere disponibile
}

// Request interceptor per aggiungere token auth
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      if ((import.meta as any).env?.MODE !== 'production') {
        // Log non sensibile (non stampa il token)
        // Aiuta a diagnosticare i 403 in sviluppo
        console.info('[API] Authorization header applied:', true, 'URL:', config.baseURL + (config.url || ''))
      }
    }
    else if ((import.meta as any).env?.MODE !== 'production') {
      console.info('[API] No auth token in localStorage for request:', config.baseURL + (config.url || ''))
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor per gestire errori auth
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('admin_data')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const body = new URLSearchParams()
    body.append('username', email)
    body.append('password', password)

    const response = await api.post('/auth/login', body.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  getCurrentAdmin: async () => {
    const response = await api.get('/admin/me')
    return response.data
  }
}

// Instagram accounts API
export const instagramApi = {
  getAccounts: async () => {
    const response = await api.get('/instagram/accounts')
    return response.data
  },

  getAccount: async (id: number) => {
    const response = await api.get(`/instagram/accounts/${id}`)
    return response.data
  },

  syncAccount: async (id: number) => {
    const response = await api.post(`/instagram/accounts/${id}/sync`)
    return response.data
  },

  deleteAccount: async (id: number) => {
    const response = await api.delete(`/instagram/accounts/${id}`)
    return response.data
  },

  getAuthUrl: async () => {
    const response = await api.get('/instagram/auth/url')
    return response.data
  },

  connectCallback: async (code: string, state: string) => {
    const response = await api.post('/instagram/auth/callback', { code, state })
    return response.data
  },

  getAccountStats: async (id: number) => {
    const response = await api.get(`/instagram/accounts/${id}/stats`)
    return response.data
  }
}

// Posts API
export const postsApi = {
  getPosts: async (params?: { account_id?: number; status_filter?: string; limit?: number; offset?: number }) => {
    const response = await api.get('/posts', { params })
    return response.data
  },

  getPost: async (id: number) => {
    const response = await api.get(`/posts/${id}`)
    return response.data
  },

  createPost: async (data: any) => {
    const response = await api.post('/posts', data)
    return response.data
  },

  updatePost: async (id: number, data: any) => {
    const response = await api.put(`/posts/${id}`, data)
    return response.data
  },

  deletePost: async (id: number) => {
    const response = await api.delete(`/posts/${id}`)
    return response.data
  },

  publishPost: async (id: number) => {
    const response = await api.post(`/posts/${id}/publish`)
    return response.data
  },

  getPostAnalytics: async (id: number) => {
    const response = await api.get(`/posts/${id}/analytics`)
    return response.data
  },

  getPostsStats: async (account_id?: number) => {
    const params = account_id ? { account_id } : {}
    const response = await api.get('/posts/stats/overview', { params })
    return response.data
  }
}

// Media API
export const mediaApi = {
  uploadMedia: async (file: File, altText?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (altText) formData.append('alt_text', altText)

    const response = await api.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getMedia: async (limit?: number, offset?: number, mediaType?: string) => {
    const params = { limit, offset, media_type: mediaType }
    const response = await api.get('/media', { params })
    return response.data
  },

  getMediaItem: async (id: number) => {
    const response = await api.get(`/media/${id}`)
    return response.data
  },

  updateMedia: async (id: number, data: any) => {
    const response = await api.put(`/media/${id}`, data)
    return response.data
  },

  deleteMedia: async (id: number) => {
    const response = await api.delete(`/media/${id}`)
    return response.data
  }
}

// Scheduled posts API
export const scheduledApi = {
  getScheduledPosts: async (params?: { account_id?: number; status_filter?: string; limit?: number; offset?: number }) => {
    const response = await api.get('/scheduled', { params })
    return response.data
  },

  createScheduledPost: async (data: any) => {
    const response = await api.post('/scheduled', data)
    return response.data
  },

  updateScheduledPost: async (id: number, data: any) => {
    const response = await api.put(`/scheduled/${id}`, data)
    return response.data
  },

  cancelScheduledPost: async (id: number) => {
    const response = await api.delete(`/scheduled/${id}`)
    return response.data
  },

  executeNow: async (id: number) => {
    const response = await api.post(`/scheduled/${id}/execute`)
    return response.data
  },

  getScheduledStats: async (account_id?: number) => {
    const params = account_id ? { account_id } : {}
    const response = await api.get('/scheduled/stats/overview', { params })
    return response.data
  },

  getCalendarData: async (year: number, month: number, account_id?: number) => {
    const params = account_id ? { account_id } : {}
    const response = await api.get(`/scheduled/calendar/${year}/${month}`, { params })
    return response.data
  }
}

// Analytics API
export const analyticsApi = {
  getAnalytics: async (params?: { account_id?: number; start_date?: string; end_date?: string; limit?: number }) => {
    const response = await api.get('/analytics', { params })
    return response.data
  },

  getAccountAnalytics: async (accountId: number, days?: number) => {
    const params = days ? { days } : {}
    const response = await api.get(`/analytics/account/${accountId}`, { params })
    return response.data
  },

  syncAccountAnalytics: async (accountId: number) => {
    const response = await api.post(`/analytics/sync/${accountId}`)
    return response.data
  },

  getAccountInsights: async (accountId: number, days?: number) => {
    const params = days ? { days } : {}
    const response = await api.get(`/analytics/insights/${accountId}`, { params })
    return response.data
  },

  exportAnalytics: async (accountId: number, params?: { start_date?: string; end_date?: string; format?: string }) => {
    const response = await api.get(`/analytics/export/${accountId}`, { params })
    return response.data
  }
}

// Dashboard API
export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats')
    return response.data
  },

  getRecentActivity: async (limit?: number) => {
    const params = limit ? { limit } : {}
    const response = await api.get('/dashboard/recent-activity', { params })
    return response.data
  },

  getPerformanceMetrics: async (days?: number) => {
    const params = days ? { days } : {}
    const response = await api.get('/dashboard/performance-metrics', { params })
    return response.data
  },

  getContentInsights: async () => {
    const response = await api.get('/dashboard/content-insights')
    return response.data
  }
}
