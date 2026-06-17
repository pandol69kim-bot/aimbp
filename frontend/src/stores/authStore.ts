'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '@/types'

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      setAuth: (user: User, token: string) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', token)
        }
        set({ user, accessToken: token, isAuthenticated: true })
      },
      clearAuth: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
        }
        set({ user: null, accessToken: null, isAuthenticated: false })
      },
      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...updates } })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
