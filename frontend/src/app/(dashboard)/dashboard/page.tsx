'use client'

import { FileText, Music, Disc, TrendingUp, Clock, Plus } from 'lucide-react'
import Link from 'next/link'
import { useAuthStore } from '@/stores/authStore'
import { useLyricsList } from '@/hooks/useLyrics'
import { useTrackList } from '@/hooks/useMusic'
import { useAlbumList } from '@/hooks/useAlbums'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/common/StatusBadge'
import { AudioPlayer } from '@/components/audio/AudioPlayer'
import { formatRelativeTime, truncate } from '@/lib/utils'
import { PageLoader } from '@/components/common/LoadingSpinner'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { data: lyrics, isLoading: lyricsLoading } = useLyricsList()
  const { data: tracks, isLoading: tracksLoading } = useTrackList()
  const { data: albums, isLoading: albumsLoading } = useAlbumList()

  if (lyricsLoading || tracksLoading || albumsLoading) {
    return <PageLoader label="대시보드 로딩 중..." />
  }

  const recentTracks = tracks?.slice(0, 5) || []
  const recentLyrics = lyrics?.slice(0, 3) || []
  const completedTracks = tracks?.filter((t) => t.status === 'completed').length || 0

  return (
    <div className="page-container space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          안녕하세요, {user?.nickname}님 👋
        </h1>
        <p className="text-gray-400 mt-1">오늘도 멋진 음악을 만들어보세요.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="hover:border-primary-500/30 transition-colors">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">총 작사</p>
                <p className="text-3xl font-bold text-white mt-1">{lyrics?.length || 0}</p>
                <p className="text-xs text-gray-500 mt-1">
                  최근 생성:{' '}
                  {lyrics?.[0] ? formatRelativeTime(lyrics[0].created_at) : '없음'}
                </p>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600/20">
                <FileText className="h-6 w-6 text-primary-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-secondary-500/30 transition-colors">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">총 트랙</p>
                <p className="text-3xl font-bold text-white mt-1">{tracks?.length || 0}</p>
                <p className="text-xs text-gray-500 mt-1">완료: {completedTracks}개</p>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary-600/20">
                <Music className="h-6 w-6 text-secondary-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-accent-500/30 transition-colors">
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">총 앨범</p>
                <p className="text-3xl font-bold text-white mt-1">{albums?.length || 0}</p>
                <p className="text-xs text-gray-500 mt-1">
                  발행:{' '}
                  {albums?.filter((a) => a.status === 'published').length || 0}개
                </p>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent-600/20">
                <Disc className="h-6 w-6 text-accent-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Tracks */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary-400" />
            <h2 className="text-lg font-semibold text-white">최근 트랙</h2>
          </div>
          <Link
            href="/music"
            className="text-sm text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1"
          >
            <Plus className="h-3.5 w-3.5" />
            새 트랙
          </Link>
        </div>

        {recentTracks.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Music className="h-12 w-12 text-gray-600 mb-3" />
              <p className="text-gray-400 text-sm">아직 생성된 트랙이 없습니다</p>
              <Link href="/music" className="mt-3 text-sm text-primary-400 hover:text-primary-300">
                첫 트랙 만들기 →
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {recentTracks.map((track) => (
              <Card key={track.id} className="hover:border-white/20 transition-colors">
                <CardContent className="p-4">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium text-white truncate">{track.title}</p>
                        <StatusBadge status={track.status} />
                      </div>
                      <p className="text-xs text-gray-500">
                        {track.genre} · {formatRelativeTime(track.created_at)}
                      </p>
                    </div>
                    <div className="w-full sm:w-64">
                      <AudioPlayer
                        src={track.file_url}
                        status={track.status}
                        compact
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Recent Lyrics */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-accent-400" />
            <h2 className="text-lg font-semibold text-white">최근 작사</h2>
          </div>
          <Link
            href="/lyrics"
            className="text-sm text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1"
          >
            <Plus className="h-3.5 w-3.5" />
            새 작사
          </Link>
        </div>

        {recentLyrics.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-12 w-12 text-gray-600 mb-3" />
              <p className="text-gray-400 text-sm">아직 생성된 작사가 없습니다</p>
              <Link href="/lyrics" className="mt-3 text-sm text-primary-400 hover:text-primary-300">
                첫 작사 만들기 →
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {recentLyrics.map((lyric) => (
              <Card key={lyric.id} className="hover:border-white/20 transition-colors">
                <CardHeader>
                  <CardTitle className="text-base">{lyric.title}</CardTitle>
                  <p className="text-xs text-gray-500">
                    {lyric.prompt_genre} · {lyric.prompt_mood}
                  </p>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-400 line-clamp-3">
                    {truncate(lyric.verse || lyric.chorus || '', 120)}
                  </p>
                  <p className="text-xs text-gray-600 mt-2">
                    {formatRelativeTime(lyric.created_at)}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
