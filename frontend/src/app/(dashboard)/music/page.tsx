'use client'

import { useState } from 'react'
import { Music, Sparkles, Download } from 'lucide-react'
import { useTrackList, useGenerateMusic, useTrackStatus } from '@/hooks/useMusic'
import { useLyricsList } from '@/hooks/useLyrics'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/common/StatusBadge'
import { AudioPlayer } from '@/components/audio/AudioPlayer'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatRelativeTime } from '@/lib/utils'
import { Track } from '@/types'

const genreOptions = [
  { value: 'pop', label: 'Pop' },
  { value: 'kpop', label: 'K-Pop' },
  { value: 'rnb', label: 'R&B' },
  { value: 'hiphop', label: 'Hip-Hop' },
  { value: 'rock', label: 'Rock' },
  { value: 'ballad', label: 'Ballad' },
  { value: 'electronic', label: 'Electronic' },
  { value: 'jazz', label: 'Jazz' },
  { value: 'classical', label: 'Classical' },
]

const moodOptions = [
  { value: 'happy', label: '밝고 신나는' },
  { value: 'sad', label: '슬프고 감성적' },
  { value: 'romantic', label: '로맨틱' },
  { value: 'energetic', label: '에너제틱' },
  { value: 'calm', label: '차분하고 잔잔한' },
  { value: 'dark', label: '어둡고 강렬한' },
]

const aiServiceOptions = [
  { value: 'suno', label: 'Suno AI' },
  { value: 'mureka', label: 'Mureka' },
  { value: 'udio', label: 'Udio' },
]

function TrackItem({ track }: { track: Track }) {
  const isPolling = track.status === 'processing' || track.status === 'pending'
  const { data: updatedTrack } = useTrackStatus(track.id, isPolling)
  const displayTrack = updatedTrack || track

  const handleDownload = () => {
    if (!displayTrack.file_url) return
    const link = document.createElement('a')
    link.href = displayTrack.file_url
    link.download = `${displayTrack.title || 'track'}.mp3`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const isCompleted = displayTrack.status === 'completed'

  return (
    <Card className="hover:border-white/20 transition-colors">
      <CardContent className="p-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <p className="text-sm font-medium text-white truncate">{displayTrack.title}</p>
              <StatusBadge status={displayTrack.status} />
            </div>
            <p className="text-xs text-gray-500">
              {displayTrack.genre}
              {displayTrack.bpm && ` · ${displayTrack.bpm} BPM`}
              {' · '}{formatRelativeTime(displayTrack.created_at)}
            </p>
            {displayTrack.error_message && (
              <p className="text-xs text-red-400 mt-2 bg-red-500/10 px-2 py-1 rounded">
                ❌ {displayTrack.error_message}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <div className="flex-1 sm:flex-none sm:w-64">
              <AudioPlayer
                src={displayTrack.file_url}
                status={displayTrack.status}
                compact
              />
            </div>
            <button
              onClick={handleDownload}
              disabled={!isCompleted}
              className={`p-2 rounded-lg transition-colors ${
                isCompleted
                  ? 'text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer'
                  : 'text-gray-600 cursor-not-allowed opacity-50'
              }`}
              title={isCompleted ? '다운로드' : '생성 완료 후 다운로드 가능'}
            >
              <Download className="h-5 w-5" />
            </button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function MusicPage() {
  const { data: tracks, isLoading } = useTrackList()
  const { data: lyricsList } = useLyricsList()
  const generateMutation = useGenerateMusic()

  const [title, setTitle] = useState('')
  const [genre, setGenre] = useState('')
  const [bpm, setBpm] = useState('')
  const [mood, setMood] = useState('')
  const [lyricsId, setLyricsId] = useState('')
  const [aiService, setAiService] = useState('suno')

  const lyricsOptions = [
    { value: '', label: '가사 없이 생성' },
    ...(lyricsList?.map((l) => ({ value: l.id, label: l.title })) || []),
  ]

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    await generateMutation.mutateAsync({
      title,
      genre,
      bpm: bpm ? parseInt(bpm) : undefined,
      mood,
      lyrics_id: lyricsId || undefined,
      ai_service: aiService,
    })
    setTitle('')
    setBpm('')
  }

  if (isLoading) return <PageLoader label="트랙 목록 로딩 중..." />

  return (
    <div className="page-container">
      <div className="mb-6">
        <h1 className="section-title flex items-center gap-2">
          <Music className="h-5 w-5 text-primary-400" />
          작곡 생성
        </h1>
        <p className="section-desc">AI가 당신의 음악을 작곡해드립니다</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>생성 설정</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleGenerate} className="space-y-4">
                <Input
                  label="제목"
                  placeholder="곡 제목"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
                <Select
                  label="장르"
                  options={genreOptions}
                  placeholder="장르 선택"
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  required
                />
                <Input
                  label="BPM (선택)"
                  type="number"
                  placeholder="ex) 120"
                  min="60"
                  max="200"
                  value={bpm}
                  onChange={(e) => setBpm(e.target.value)}
                />
                <Select
                  label="분위기 (선택)"
                  options={moodOptions}
                  placeholder="분위기 선택"
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
                />
                <Select
                  label="가사 연동 (선택)"
                  options={lyricsOptions}
                  value={lyricsId}
                  onChange={(e) => setLyricsId(e.target.value)}
                />
                <Select
                  label="AI 서비스"
                  options={aiServiceOptions}
                  value={aiService}
                  onChange={(e) => setAiService(e.target.value)}
                  required
                />
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={generateMutation.isPending}
                >
                  <Sparkles className="h-4 w-4" />
                  작곡 생성하기
                </Button>
              </form>
              {generateMutation.isError && (
                <p className="mt-3 text-xs text-red-400">생성에 실패했습니다. 다시 시도해주세요.</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Track List */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">트랙 목록</h2>
            <span className="text-sm text-gray-500">{tracks?.length || 0}개</span>
          </div>

          {!tracks || tracks.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <Music className="h-12 w-12 text-gray-600 mb-3" />
                <p className="text-sm text-gray-400">아직 생성된 트랙이 없습니다</p>
                <p className="text-xs text-gray-500 mt-1">왼쪽 폼에서 첫 트랙을 생성해보세요</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {tracks.map((track) => (
                <TrackItem key={track.id} track={track} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
