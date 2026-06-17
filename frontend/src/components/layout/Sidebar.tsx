'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  FileText,
  Music,
  Sliders,
  Mic,
  Wand2,
  Image,
  Disc,
  LogOut,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: '대시보드' },
  { href: '/lyrics', icon: FileText, label: '작사' },
  { href: '/music', icon: Music, label: '작곡' },
  { href: '/arrangement', icon: Sliders, label: '편곡' },
  { href: '/vocal', icon: Mic, label: '보컬' },
  { href: '/mastering', icon: Wand2, label: '마스터링' },
  { href: '/cover', icon: Image, label: '앨범 커버' },
  { href: '/albums', icon: Disc, label: '앨범' },
]

const planLabels: Record<string, string> = {
  free: 'Free',
  creator: 'Creator',
  studio: 'Studio',
  label: 'Label',
}

const planColors: Record<string, string> = {
  free: 'text-gray-400',
  creator: 'text-accent-400',
  studio: 'text-primary-400',
  label: 'text-yellow-400',
}

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout, isLoading } = useAuth()

  return (
    <aside className="flex h-full w-64 flex-col border-r border-white/10 bg-dark-900/80 backdrop-blur-md">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-600 to-accent-600">
          <Music className="h-4 w-4 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-wider">AIMBP</h1>
          <p className="text-xs text-gray-500">AI Music Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map(({ href, icon: Icon, label }) => {
          const isActive = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-primary-600/20 text-primary-300 border border-primary-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              )}
            >
              <Icon
                className={cn(
                  'h-4 w-4 shrink-0 transition-colors',
                  isActive ? 'text-primary-400' : 'text-gray-500 group-hover:text-gray-300'
                )}
              />
              <span className="flex-1">{label}</span>
              {isActive && <ChevronRight className="h-3.5 w-3.5 text-primary-400" />}
            </Link>
          )
        })}
      </nav>

      {/* User Info */}
      {user && (
        <div className="border-t border-white/10 p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-accent-600 shrink-0">
              <span className="text-sm font-bold text-white">
                {user.nickname.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user.nickname}</p>
              <p className={cn('text-xs font-medium', planColors[user.plan] || 'text-gray-400')}>
                {planLabels[user.plan] || user.plan} Plan
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            disabled={isLoading}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            <span>로그아웃</span>
          </button>
        </div>
      )}
    </aside>
  )
}
