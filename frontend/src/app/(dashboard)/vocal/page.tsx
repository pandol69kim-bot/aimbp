'use client'

import { useState } from 'react'
import { Mic, Sparkles, Play } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useTrackList } from '@/hooks/useMusic'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { StatusBadge } from '@/components/common/StatusBadge'
import { AudioPlayer } from '@/components/audio/AudioPlayer'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatRelativeTime } from '@/lib/utils'
import { VocalLibrary, VocalTrack } from '@/types'

const languageOptions = [
  { value: 'korean', label: '한국어' },
  { value: 'english', label: 'English' },
  { value: 'japanese', label: '日本語' },
]

export default function VocalPage() {
  const queryClient = useQueryClient()
  const { data: tracks } = useTrackList()
  const [selectedTrackId, setSelectedTrackId] = useState('')
  const [selectedVocalId, setSelectedVocalId] = useState('')
  const [language, setLanguage] = useState('korean')

  const { data: vocalLibrary, isLoading: libraryLoading } = useQuery({
    queryKey: ['vocal-library'],
    queryFn: async () => {
      const res = await api.get<VocalLibrary[]>('/vocal/library')
      return res.data
    },
  })

  const { data: vocalTracks, isLoading: tracksLoading } = useQuery({
    queryKey: ['vocal-tracks'],
    queryFn: async () => {
      const res = await api.get<VocalTrack[]>('/vocal')
      return res.data
    },
  })

  const generateMutation = useMutation({
    mutationFn: async (data: { track_id: string; library_id: string; language: string }) => {
      const res = await api.post('/vocal/generate', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vocal-tracks'] })
    },
  })

  const completedTracks = tracks?.filter((t) => t.status === 'completed') || []
  const trackOptions = completedTracks.map((t) => ({ value: t.id, label: t.title }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTrackId || !selectedVocalId) return
    await generateMutation.mutateAsync({ track_id: selectedTrackId, library_id: selectedVocalId, language })
  }

  if (libraryLoading || tracksLoading) return <PageLoader label="보컬 데이터 로딩 중..." />

  const genderLabel = { male: '남성', female: '여성', neutral: '중성' }

  return (
    <div className="page-container">
      <div className="mb-6">
        <h1 className="section-title flex items-center gap-2">
          <Mic className="h-5 w-5 text-primary-400" />
          보컬
        </h1>
        <p className="section-desc">AI 보컬을 선택하고 트랙에 적용하세요</p>
      </div>

      {/* Vocal Library */}
      <div className="mb-8">
        <h2 className="text-base font-semibold text-white mb-4">보컬 라이브러리</h2>
        {!vocalLibrary || vocalLibrary.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center py-12">
              <Mic className="h-10 w-10 text-gray-600 mb-2" />
              <p className="text-sm text-gray-400">보컬 라이브러리가 비어있습니다</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {vocalLibrary.map((vocal) => (
              <Card
                key={vocal.id}
                className={`cursor-pointer transition-all ${
                  selectedVocalId === vocal.id
                    ? 'border-primary-500/50 bg-primary-900/20'
                    : 'hover:border-white/20'
                }`}
                onClick={() => setSelectedVocalId(vocal.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-600/40 to-accent-600/40 border border-primary-500/30">
                      <Mic className="h-5 w-5 text-primary-300" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{vocal.name}</p>
                      <div className="flex gap-1 mt-0.5">
                        <Badge variant="outline" className="text-xs px-1.5 py-0">
                          {genderLabel[vocal.gender]}
                        </Badge>
                        <Badge variant="secondary" className="text-xs px-1.5 py-0">
                          {vocal.genre}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  {vocal.description && (
                    <p className="text-xs text-gray-400 line-clamp-2 mb-2">{vocal.description}</p>
                  )}
                  {vocal.sample_url && (
                    <AudioPlayer src={vocal.sample_url} status="completed" compact />
                  )}
                  {selectedVocalId === vocal.id && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-primary-400">
                      <Play className="h-3 w-3" />
                      <span>선택됨</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Generate Form + Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div>
          <Card>
            <CardHeader>
              <CardTitle>보컬 적용</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Select
                  label="트랙 선택"
                  options={trackOptions}
                  placeholder="완료된 트랙 선택"
                  value={selectedTrackId}
                  onChange={(e) => setSelectedTrackId(e.target.value)}
                  required
                />
                <div>
                  <p className="text-sm font-medium text-gray-300 mb-1">선택된 보컬</p>
                  <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm">
                    {selectedVocalId ? (
                      <span className="text-primary-300">
                        {vocalLibrary?.find((v) => v.id === selectedVocalId)?.name}
                      </span>
                    ) : (
                      <span className="text-gray-500">위에서 보컬을 선택하세요</span>
                    )}
                  </div>
                </div>
                <Select
                  label="언어"
                  options={languageOptions}
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                />
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={generateMutation.isPending}
                  disabled={!selectedTrackId || !selectedVocalId}
                >
                  <Sparkles className="h-4 w-4" />
                  보컬 적용하기
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">생성 결과</h2>
            <span className="text-sm text-gray-500">{vocalTracks?.length || 0}개</span>
          </div>
          {!vocalTracks || vocalTracks.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center py-12">
                <Mic className="h-10 w-10 text-gray-600 mb-2" />
                <p className="text-sm text-gray-400">생성된 보컬 트랙이 없습니다</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {vocalTracks.map((vt) => {
                const track = tracks?.find((t) => t.id === vt.track_id)
                const vocal = vocalLibrary?.find((v) => v.id === vt.library_id)
                return (
                  <Card key={vt.id} className="hover:border-white/20 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <p className="text-sm font-medium text-white">{track?.title || '알 수 없는 트랙'}</p>
                          <p className="text-xs text-gray-500">
                            {vocal?.name} · {vt.language} · {formatRelativeTime(vt.created_at)}
                          </p>
                        </div>
                        <StatusBadge status={vt.status} />
                      </div>
                      <AudioPlayer src={vt.file_url} status={vt.status} compact />
                    </CardContent>
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
