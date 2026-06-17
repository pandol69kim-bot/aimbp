'use client'

import { useState } from 'react'
import { Sparkles, FileText, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { useLyricsList, useGenerateLyrics, useDeleteLyrics } from '@/hooks/useLyrics'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatRelativeTime } from '@/lib/utils'
import { Lyrics } from '@/types'

const genreOptions = [
  { value: 'pop', label: 'Pop' },
  { value: 'kpop', label: 'K-Pop' },
  { value: 'rnb', label: 'R&B' },
  { value: 'hiphop', label: 'Hip-Hop' },
  { value: 'rock', label: 'Rock' },
  { value: 'ballad', label: 'Ballad' },
  { value: 'electronic', label: 'Electronic' },
  { value: 'jazz', label: 'Jazz' },
]

const moodOptions = [
  { value: 'happy', label: '밝고 신나는' },
  { value: 'sad', label: '슬프고 감성적' },
  { value: 'romantic', label: '로맨틱' },
  { value: 'energetic', label: '에너제틱' },
  { value: 'calm', label: '차분하고 잔잔한' },
  { value: 'dark', label: '어둡고 강렬한' },
  { value: 'hopeful', label: '희망적' },
  { value: 'nostalgic', label: '노스탤지어' },
]

const languageOptions = [
  { value: 'korean', label: '한국어' },
  { value: 'english', label: 'English' },
  { value: 'mixed', label: '한/영 혼합' },
]

const aiModelOptions = [
  { value: 'gpt-4', label: 'GPT-4' },
  { value: 'claude-3', label: 'Claude 3' },
  { value: 'gemini-pro', label: 'Gemini Pro' },
]

function LyricsCard({ lyrics, onDelete }: { lyrics: Lyrics; onDelete: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <Card className="hover:border-white/20 transition-colors">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{lyrics.title}</CardTitle>
            <p className="text-xs text-gray-500 mt-1">
              {lyrics.prompt_genre} · {lyrics.prompt_mood} · {formatRelativeTime(lyrics.created_at)}
            </p>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
            >
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
            <button
              onClick={() => onDelete(lyrics.id)}
              className="p-1.5 text-gray-400 hover:text-red-400 rounded-lg hover:bg-red-900/20 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </CardHeader>
      {expanded && (
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {lyrics.verse && (
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-xs font-semibold text-primary-400 mb-2">VERSE</p>
                <p className="text-sm text-gray-300 whitespace-pre-line">{lyrics.verse}</p>
              </div>
            )}
            {lyrics.chorus && (
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-xs font-semibold text-accent-400 mb-2">CHORUS</p>
                <p className="text-sm text-gray-300 whitespace-pre-line">{lyrics.chorus}</p>
              </div>
            )}
            {lyrics.bridge && (
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-xs font-semibold text-secondary-400 mb-2">BRIDGE</p>
                <p className="text-sm text-gray-300 whitespace-pre-line">{lyrics.bridge}</p>
              </div>
            )}
            {lyrics.hook && (
              <div className="rounded-lg bg-white/5 p-3">
                <p className="text-xs font-semibold text-yellow-400 mb-2">HOOK</p>
                <p className="text-sm text-gray-300 whitespace-pre-line">{lyrics.hook}</p>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

export default function LyricsPage() {
  const { data: lyricsList, isLoading } = useLyricsList()
  const generateMutation = useGenerateLyrics()
  const deleteMutation = useDeleteLyrics()

  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [mood, setMood] = useState('')
  const [genre, setGenre] = useState('')
  const [artistStyle, setArtistStyle] = useState('')
  const [language, setLanguage] = useState('korean')
  const [aiModel, setAiModel] = useState('gpt-4')
  const [generatedLyrics, setGeneratedLyrics] = useState<Lyrics | null>(null)

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await generateMutation.mutateAsync({
      title,
      prompt_subject: subject,
      prompt_mood: mood,
      prompt_genre: genre,
      artist_style: artistStyle,
      language,
      ai_model: aiModel,
    })
    if (result.data) {
      setGeneratedLyrics(result.data)
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('이 작사를 삭제하시겠습니까?')) {
      await deleteMutation.mutateAsync(id)
      if (generatedLyrics?.id === id) setGeneratedLyrics(null)
    }
  }

  if (isLoading) return <PageLoader label="작사 목록 로딩 중..." />

  return (
    <div className="page-container">
      <div className="mb-6">
        <h1 className="section-title flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary-400" />
          작사 생성
        </h1>
        <p className="section-desc">AI가 당신만의 가사를 만들어드립니다</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>생성 설정</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleGenerate} className="space-y-4">
                <Input
                  label="제목"
                  placeholder="곡 제목을 입력하세요"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
                <Input
                  label="주제 / 컨셉"
                  placeholder="ex) 첫사랑, 이별 후 성장, 새벽의 도시"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  required
                />
                <Select
                  label="분위기"
                  options={moodOptions}
                  placeholder="분위기 선택"
                  value={mood}
                  onChange={(e) => setMood(e.target.value)}
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
                  label="아티스트 스타일 (선택)"
                  placeholder="ex) IU, BTS, NewJeans 스타일"
                  value={artistStyle}
                  onChange={(e) => setArtistStyle(e.target.value)}
                />
                <div className="grid grid-cols-2 gap-3">
                  <Select
                    label="언어"
                    options={languageOptions}
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  />
                  <Select
                    label="AI 모델"
                    options={aiModelOptions}
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value)}
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={generateMutation.isPending}
                >
                  <Sparkles className="h-4 w-4" />
                  작사 생성하기
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div>
          {generateMutation.isPending ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <div className="flex items-center gap-3 text-primary-400 mb-3">
                  <svg className="h-6 w-6 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span className="text-sm font-medium">AI가 가사를 작성하고 있습니다...</span>
                </div>
                <p className="text-xs text-gray-500">잠시만 기다려주세요</p>
              </CardContent>
            </Card>
          ) : generatedLyrics ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary-400" />
                  {generatedLyrics.title}
                </CardTitle>
                <p className="text-xs text-gray-500">
                  {generatedLyrics.prompt_genre} · {generatedLyrics.prompt_mood} · {generatedLyrics.ai_model}
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                {generatedLyrics.verse && (
                  <div className="rounded-lg bg-primary-900/20 border border-primary-500/20 p-4">
                    <p className="text-xs font-bold text-primary-400 uppercase tracking-wider mb-2">Verse</p>
                    <p className="text-sm text-gray-200 whitespace-pre-line">{generatedLyrics.verse}</p>
                  </div>
                )}
                {generatedLyrics.chorus && (
                  <div className="rounded-lg bg-accent-900/20 border border-accent-500/20 p-4">
                    <p className="text-xs font-bold text-accent-400 uppercase tracking-wider mb-2">Chorus</p>
                    <p className="text-sm text-gray-200 whitespace-pre-line">{generatedLyrics.chorus}</p>
                  </div>
                )}
                {generatedLyrics.bridge && (
                  <div className="rounded-lg bg-secondary-900/20 border border-secondary-500/20 p-4">
                    <p className="text-xs font-bold text-secondary-400 uppercase tracking-wider mb-2">Bridge</p>
                    <p className="text-sm text-gray-200 whitespace-pre-line">{generatedLyrics.bridge}</p>
                  </div>
                )}
                {generatedLyrics.hook && (
                  <div className="rounded-lg bg-yellow-900/20 border border-yellow-500/20 p-4">
                    <p className="text-xs font-bold text-yellow-400 uppercase tracking-wider mb-2">Hook</p>
                    <p className="text-sm text-gray-200 whitespace-pre-line">{generatedLyrics.hook}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <FileText className="h-12 w-12 text-gray-600 mb-3" />
                <p className="text-sm text-gray-400">생성 결과가 여기에 표시됩니다</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* History */}
      {lyricsList && lyricsList.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4">생성 이력</h2>
          <div className="space-y-3">
            {lyricsList.map((lyric) => (
              <LyricsCard key={lyric.id} lyrics={lyric} onDelete={handleDelete} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
