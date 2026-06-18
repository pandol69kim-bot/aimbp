'use client'

import { Bell, Search, Menu } from 'lucide-react'
import { usePathname } from 'next/navigation'
import { useSidebarStore } from '@/stores/sidebarStore'

const pageTitles: Record<string, string> = {
  '/dashboard': '대시보드',
  '/lyrics': '작사 생성',
  '/music': '작곡 생성',
  '/arrangement': '편곡',
  '/vocal': '보컬',
  '/mastering': '마스터링',
  '/cover': '앨범 커버 생성',
  '/albums': '앨범 관리',
}

function getPageTitle(pathname: string): string {
  if (pathname.startsWith('/albums/') && pathname !== '/albums') {
    return '앨범 상세'
  }
  return pageTitles[pathname] || '대시보드'
}

export function Header() {
  const pathname = usePathname()
  const title = getPageTitle(pathname)
  const { toggleSidebar } = useSidebarStore()

  return (
    <header className="flex h-16 items-center justify-between border-b border-white/10 bg-dark-900/50 px-4 sm:px-6 backdrop-blur-md">
      <div className="flex items-center gap-3 flex-1">
        <button
          onClick={toggleSidebar}
          className="lg:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <Menu className="h-4 w-4" />
        </button>
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>
      <div className="flex items-center gap-3">
        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
          <input
            type="text"
            placeholder="검색..."
            className="h-9 w-48 rounded-lg border border-white/10 bg-white/5 pl-9 pr-3 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 transition-all"
          />
        </div>
        <button className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary-500" />
        </button>
      </div>
    </header>
  )
}
