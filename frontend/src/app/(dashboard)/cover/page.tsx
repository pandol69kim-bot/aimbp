'use client'

import { useState } from 'react'
import { Image as ImageIcon, Sparkles, Download } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatRelativeTime } from '@/lib/utils'
import { CoverImage } from '@/types'

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
  { value: 'dreamy', label: '몽환적' },
  { value: 'energetic', label: '에너제틱' },
  { value: 'dark', label: '다크' },
  { value: 'romantic', label: '로맨틱' },
  { value: 'minimalist', label: '미니멀리스트' },
  { value: 'vintage', label: '빈티지' },
  { value: 'futuristic', label: '미래적' },
  { value: 'natural', label: '자연적' },
]

const aiModelOptions = [
  { value: 'dalle-3', label: 'DALL-E 3' },
  { value: 'midjourney', label: 'Midjourney' },
  { value: 'stable-diffusion', label: 'Stable Diffusion' },
]

const ratioLabels: Record<string, string> = {
  '1:1': '정사각형 (1:1)',
  '16:9': '가로형 (16:9)',
  '9:16': '세로형 (9:16)',
}

interface GroupedCover {
  id: string
  genre: string
  mood: string
  keywords: string
  ai_model: string
  created_at: string
  status: string
  images: Array<{ ratio: '1:1' | '16:9' | '9:16'; url?: string; size: string }>
}

function groupCoversByPrompt(covers: CoverImage[]): GroupedCover[] {
  const grouped = new Map<string, GroupedCover>()

  covers.forEach((cover) => {
    const key = `${cover.created_at}-${cover.prompt_genre}-${cover.prompt_mood}`

    if (!grouped.has(key)) {
      grouped.set(key, {
        id: cover.id,
        genre: cover.genre || cover.prompt_genre,
        mood: cover.mood || cover.prompt_mood,
        keywords: cover.keywords || cover.prompt_keywords,
        ai_model: cover.ai_model,
        created_at: cover.created_at,
        status: cover.status,
        images: [],
      })
    }

    const groupedCover = grouped.get(key)!
    const ratioMap: Record<string, '1:1' | '16:9' | '9:16'> = {
      '1:1': '1:1',
      '16:9': '16:9',
      '9:16': '9:16',
    }

    groupedCover.images.push({
      ratio: ratioMap[cover.size] || ('1:1' as const),
      url: cover.image_url,
      size: cover.size,
    })
  })

  return Array.from(grouped.values()).sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

export default function CoverPage() {
  const queryClient = useQueryClient()
  const [genre, setGenre] = useState('')
  const [mood, setMood] = useState('')
  const [keywords, setKeywords] = useState('')
  const [aiModel, setAiModel] = useState('dalle-3')

  const { data: rawCovers, isLoading } = useQuery({
    queryKey: ['covers'],
    queryFn: async () => {
      const res = await api.get<CoverImage[]>('/cover')
      return res.data
    },
  })

  const covers = rawCovers ? groupCoversByPrompt(rawCovers) : []

  const generateMutation = useMutation({
    mutationFn: async (data: { genre: string; mood: string; keywords: string; ai_model: string }) => {
      const res = await api.post('/cover/generate', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['covers'] })
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await generateMutation.mutateAsync({ genre, mood, keywords, ai_model: aiModel })
  }

  if (isLoading) return <PageLoader label="커버 데이터 로딩 중..." />

  return (
    <div className="page-container">
      <div className="mb-6">
        <h1 className="section-title flex items-center gap-2">
          <ImageIcon className="h-5 w-5 text-primary-400" />
          앨범 커버 생성
        </h1>
        <p className="section-desc">AI로 독창적인 앨범 커버 아트를 만드세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>생성 설정</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Select
                  label="장르"
                  options={genreOptions}
                  placeholder="장르 선택"
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
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
                <Input
                  label="키워드"
                  placeholder="ex) 야경, 도시, 별빛, 감성"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  required
                  helperText="쉼표로 구분하여 여러 키워드 입력 가능"
                />
                <Select
                  label="AI 모델"
                  options={aiModelOptions}
                  value={aiModel}
                  onChange={(e) => setAiModel(e.target.value)}
                />
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={generateMutation.isPending}
                >
                  <Sparkles className="h-4 w-4" />
                  커버 생성하기
                </Button>
                <p className="text-xs text-gray-500 text-center">
                  1:1, 16:9, 9:16 3가지 비율로 생성됩니다
                </p>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">생성 이력</h2>
            <span className="text-sm text-gray-500">{covers?.length || 0}개</span>
          </div>

          {generateMutation.isPending && (
            <Card className="mb-4 border-primary-500/30">
              <CardContent className="flex flex-col items-center py-8">
                <div className="flex items-center gap-2 text-primary-400 mb-2">
                  <svg className="h-5 w-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span className="text-sm">AI가 커버를 그리고 있습니다...</span>
                </div>
                <p className="text-xs text-gray-500">최대 1-2분 소요될 수 있습니다</p>
              </CardContent>
            </Card>
          )}

          {!covers || covers.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center py-12">
                <ImageIcon className="h-12 w-12 text-gray-600 mb-3" />
                <p className="text-sm text-gray-400">생성된 커버가 없습니다</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {covers.map((cover) => {
                const hasImages = cover.images && Array.isArray(cover.images) && cover.images.length > 0
                const isCompleted = cover.status === 'completed'
                const isProcessing = cover.status === 'processing'

                return (
                  <Card
                    key={cover.id}
                    className={`hover:border-white/20 transition-colors overflow-hidden ${
                      isCompleted && hasImages ? 'cursor-pointer' : ''
                    }`}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-sm truncate">
                            {cover.genre} · {cover.mood}
                          </CardTitle>
                          <p className="text-xs text-gray-500 mt-1 truncate">
                            {cover.keywords} · {cover.ai_model} · {formatRelativeTime(cover.created_at)}
                          </p>
                        </div>
                        <StatusBadge status={cover.status} />
                      </div>
                    </CardHeader>

                    {/* 완료 상태 - 이미지 표시 */}
                    {isCompleted && hasImages ? (
                      <CardContent className="pt-0">
                        <div className="grid grid-cols-3 gap-2">
                          {cover.images.map((img) => (
                            <div
                              key={img.ratio}
                              className="group relative overflow-hidden rounded-lg bg-white/5"
                            >
                              <div
                                className={`relative overflow-hidden bg-gradient-to-br from-white/10 to-white/5 ${
                                  img.ratio === '1:1'
                                    ? 'aspect-square'
                                    : img.ratio === '16:9'
                                    ? 'aspect-video'
                                    : 'aspect-[9/16]'
                                }`}
                              >
                                {/* 이미지 */}
                                {img.url ? (
                                  <>
                                    {/* eslint-disable-next-line @next/next/no-img-element */}
                                    <img
                                      src={img.url}
                                      alt={`Cover ${img.ratio}`}
                                      className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                                      onError={(e) => {
                                        e.currentTarget.style.display = 'none'
                                      }}
                                    />
                                    {/* 호버 오버레이 */}
                                    <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                      <a
                                        href={img.url}
                                        download={`cover-${img.ratio}`}
                                        className="flex items-center gap-1 rounded-md bg-primary-600 px-2 py-1.5 text-xs text-white hover:bg-primary-500 transition-colors"
                                      >
                                        <Download className="h-3.5 w-3.5" />
                                        다운로드
                                      </a>
                                    </div>
                                  </>
                                ) : (
                                  <div className="flex items-center justify-center h-full text-gray-500">
                                    <ImageIcon className="h-4 w-4" />
                                  </div>
                                )}
                              </div>
                              {/* 비율 라벨 */}
                              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent px-2 py-1.5">
                                <p className="text-xs text-gray-300 text-center font-medium">
                                  {ratioLabels[img.ratio]}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    ) : isProcessing ? (
                      <CardContent className="pt-0">
                        <div className="flex items-center justify-center gap-2 text-primary-400 py-6">
                          <svg
                            className="h-4 w-4 animate-spin flex-shrink-0"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                            />
                          </svg>
                          <span className="text-xs font-medium">생성 중... (1-2분)</span>
                        </div>
                      </CardContent>
                    ) : cover.status === 'failed' ? (
                      <CardContent className="pt-0">
                        <div className="flex items-center justify-center gap-2 text-red-400 py-6">
                          <span className="text-xs font-medium">생성 실패 - 다시 시도해주세요</span>
                        </div>
                      </CardContent>
                    ) : (
                      <CardContent className="pt-0">
                        <div className="flex items-center justify-center py-6">
                          <div className="h-16 w-full rounded-lg bg-white/5 flex items-center justify-center">
                            <p className="text-xs text-gray-500">이미지 처리 중...</p>
                          </div>
                        </div>
                      </CardContent>
                    )}
                  </Card>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
