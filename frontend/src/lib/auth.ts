import api from './api'
import { ApiResponse, LoginRequest, RegisterRequest, User } from '@/types'

interface TokenData {
  access_token: string
  refresh_token: string
}

export async function loginUser(data: LoginRequest): Promise<TokenData> {
  const response = await api.post<ApiResponse<TokenData>>('/auth/login', data)
  return response.data.data!
}

export async function registerUser(data: RegisterRequest): Promise<{ user: User }> {
  const response = await api.post<ApiResponse<User>>('/auth/register', data)
  return { user: response.data.data! }
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await api.get<ApiResponse<User>>('/auth/me')
  return response.data.data!
}

export async function logoutUser(): Promise<void> {
  try {
    await api.post('/auth/logout')
  } catch {
    // Ignore logout errors
  } finally {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
  }
}

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export function setStoredToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token)
  }
}

export function clearStoredToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
  }
}
