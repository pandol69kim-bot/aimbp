'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Music, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function RegisterPage() {
  const { register, isLoading, error } = useAuth()
  const [email, setEmail] = useState('')
  const [nickname, setNickname] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError(null)

    if (password !== confirmPassword) {
      setValidationError('비밀번호가 일치하지 않습니다.')
      return
    }
    if (password.length < 8) {
      setValidationError('비밀번호는 8자 이상이어야 합니다.')
      return
    }

    await register({ email, password, nickname })
  }

  const displayError = validationError || error

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-primary-600/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-accent-600/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md px-4 py-8">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-600 to-accent-600 shadow-xl shadow-primary-900/50 mb-4">
            <Music className="h-7 w-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">AIMBP</h1>
          <p className="text-sm text-gray-500 mt-1">AI Music Business Platform</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-8 shadow-2xl">
          <h2 className="text-xl font-semibold text-white mb-1">회원가입</h2>
          <p className="text-sm text-gray-400 mb-6">계정을 만들고 AI 음악 제작을 시작하세요</p>

          {displayError && (
            <div className="mb-4 rounded-lg border border-red-500/30 bg-red-900/20 p-3 text-sm text-red-400">
              {displayError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              label="이메일"
              placeholder="example@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />

            <Input
              type="text"
              label="닉네임"
              placeholder="아티스트 이름"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              required
              autoComplete="nickname"
            />

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-300">비밀번호</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="8자 이상"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                  className="flex h-10 w-full rounded-lg border border-white/10 bg-white/5 px-3 pr-10 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-300">비밀번호 확인</label>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="비밀번호 재입력"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
                className="flex h-10 w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              isLoading={isLoading}
            >
              회원가입
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-400">
            이미 계정이 있으신가요?{' '}
            <Link href="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              로그인
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
