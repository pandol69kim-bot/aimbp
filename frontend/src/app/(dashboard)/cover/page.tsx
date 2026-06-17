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

export default function CoverPage() {
  const queryClient = useQueryClient()
  const [genre, setGenre] = useState('')
  const [mood, setMood] = useState('')
  const [keywords, setKeywords] = useState('')
  const [aiModel, setAiModel] = useState('dalle-3')

  const { data: covers, isLoading } = useQuery({
    queryKey: ['covers'],
    queryFn: async () => {
      const res = await api.get<CoverImage[]>('/cover')
      return res.data
    },
  })

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
            <div className="space-y-6">
              {covers.map((cover) => (
                <Card key={cover.id} className="hover:border-white/20 transition-colors">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base">{cover.genre} · {cover.mood}</CardTitle>
                        <p className="text-xs text-gray-500 mt-1">
                          {cover.keywords} · {cover.ai_model} · {formatRelativeTime(cover.created_at)}
                        </p>
                      </div>
                      <StatusBadge status={cover.status} />
                    </div>
                  </CardHeader>
                  {cover.status === 'completed' && cover.images && cover.images.length > 0 && (
                    <CardContent>
                      <div className="grid grid-cols-3 gap-3">
                        {cover.images.map((img) => (
                          <div key={img.ratio} className="group relative">
                            <div
                              className={`relative overflow-hidden rounded-lg bg-white/5 ${
                                img.ratio === '1:1'
                                  ? 'aspect-square'
                                  : img.ratio === '16:9'
                                  ? 'aspect-video'
                                  : 'aspect-[9/16]'
                              }`}
                            >
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img
                                src={img.url}
                                alt={`Cover ${img.ratio}`}
                                className="h-full w-full object-cover"
                              />
                              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <a
                                  href={img.url}
                                  download
                                  className="flex items-center gap-1.5 rounded-lg bg-white/20 px-3 py-1.5 text-xs text-white hover:bg-white/30 transition-colors"
                                >
                                  <Download className="h-3.5 w-3.5" />
                                  다운로드
                                </a>
                              </div>
                            </div>
                            <p className="mt-1.5 text-center text-xs text-gray-500">
                              {ratioLabels[img.ratio]}
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
