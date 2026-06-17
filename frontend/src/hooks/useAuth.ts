'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import { loginUser, registerUser, logoutUser, fetchCurrentUser } from '@/lib/auth'
import { LoginRequest, RegisterRequest } from '@/types'

export function useAuth() {
  const router = useRouter()
  const { user, accessToken, isAuthenticated, setAuth, clearAuth } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const login = async (data: LoginRequest) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await loginUser(data)
      const token = response.access_token

      // 먼저 토큰을 저장 (localStorage)
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', token)
      }

      // 그 다음 user 정보 조회
      const userData = await fetchCurrentUser()
      setAuth(userData, token)
      router.push('/dashboard')
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            '로그인에 실패했습니다.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (data: RegisterRequest) => {
    setIsLoading(true)
    setError(null)
    try {
      const { user: userData } = await registerUser(data)
      const tokenData = await loginUser({ email: data.email, password: data.password })
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', tokenData.access_token)
      }
      setAuth(userData, tokenData.access_token)
      router.push('/dashboard')
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            '회원가입에 실패했습니다.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await logoutUser()
    } finally {
      clearAuth()
      setIsLoading(false)
      router.push('/login')
    }
  }

  const fetchMe = async () => {
    try {
      const userData = await fetchCurrentUser()
      if (accessToken) {
        setAuth(userData, accessToken)
      }
      return userData
    } catch {
      clearAuth()
      return null
    }
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    fetchMe,
    clearError: () => setError(null),
  }
}
