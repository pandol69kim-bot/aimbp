'use client'

import { useState } from 'react'
import { Sliders, Sparkles, Music2 } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useTrackList } from '@/hooks/useMusic'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/common/StatusBadge'
import { AudioPlayer } from '@/components/audio/AudioPlayer'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatRelativeTime } from '@/lib/utils'
import { Arrangement } from '@/types'

const INSTRUMENTS = [
  { id: 'drums', label: '드럼' },
  { id: 'bass', label: '베이스' },
  { id: 'guitar', label: '기타' },
  { id: 'piano', label: '피아노' },
  { id: 'strings', label: '스트링' },
  { id: 'synth', label: '신스' },
  { id: 'brass', label: '브라스' },
  { id: 'vocals', label: '보컬 코러스' },
]

export default function ArrangementPage() {
  const queryClient = useQueryClient()
  const { data: tracks } = useTrackList()
  const [selectedTrackId, setSelectedTrackId] = useState('')
  const [selectedInstruments, setSelectedInstruments] = useState<string[]>([])

  const { data: arrangements, isLoading } = useQuery({
    queryKey: ['arrangements'],
    queryFn: async () => {
      const res = await api.get<Arrangement[]>('/arrangement')
      return res.data
    },
  })

  const generateMutation = useMutation({
    mutationFn: async (data: { track_id: string; instruments: string[] }) => {
      const res = await api.post('/arrangement/generate', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['arrangements'] })
    },
  })

  const completedTracks = tracks?.filter((t) => t.status === 'completed') || []
  const trackOptions = completedTracks.map((t) => ({ value: t.id, label: t.title }))

  const toggleInstrument = (id: string) => {
    setSelectedInstruments((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTrackId || selectedInstruments.length === 0) return
    await generateMutation.mutateAsync({ track_id: selectedTrackId, instruments: selectedInstruments })
  }

  if (isLoading) return <PageLoader label="편곡 목록 로딩 중..." />

  return (
    <div className="page-container">
      <div className="mb-6">
        <h1 className="section-title flex items-center gap-2">
          <Sliders className="h-5 w-5 text-primary-400" />
          편곡
        </h1>
        <p className="section-desc">트랙에 다양한 악기를 추가하여 편곡하세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>편곡 설정</CardTitle>
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
                  <p className="text-sm font-medium text-gray-300 mb-2">악기 선택</p>
                  <div className="grid grid-cols-2 gap-2">
                    {INSTRUMENTS.map(({ id, label }) => (
                      <label
                        key={id}
                        className={`flex items-center gap-2 rounded-lg border p-3 cursor-pointer transition-colors ${
                          selectedInstruments.includes(id)
                            ? 'border-primary-500/50 bg-primary-900/20 text-primary-300'
                            : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/20 hover:text-gray-300'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedInstruments.includes(id)}
                          onChange={() => toggleInstrument(id)}
                          className="hidden"
                        />
                        <div
                          className={`h-3.5 w-3.5 rounded border transition-colors ${
                            selectedInstruments.includes(id)
                              ? 'border-primary-500 bg-primary-500'
                              : 'border-white/30'
                          }`}
                        />
                        <span className="text-xs font-medium">{label}</span>
                      </label>
                    ))}
                  </div>
                  {selectedInstruments.length === 0 && (
                    <p className="text-xs text-gray-500 mt-2">최소 1개 이상 선택하세요</p>
                  )}
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  isLoading={generateMutation.isPending}
                  disabled={!selectedTrackId || selectedInstruments.length === 0}
                >
                  <Sparkles className="h-4 w-4" />
                  편곡 생성하기
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Arrangement Results */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">편곡 결과</h2>
            <span className="text-sm text-gray-500">{arrangements?.length || 0}개</span>
          </div>

          {!arrangements || arrangements.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <Music2 className="h-12 w-12 text-gray-600 mb-3" />
                <p className="text-sm text-gray-400">편곡 결과가 없습니다</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {arrangements.map((arr) => {
                const track = tracks?.find((t) => t.id === arr.track_id)
                return (
                  <Card key={arr.id} className="hover:border-white/20 transition-colors">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-base">{track?.title || '알 수 없는 트랙'}</CardTitle>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {arr.instruments.map((inst) => (
                              <span
                                key={inst}
                                className="rounded-full bg-primary-900/30 border border-primary-500/20 px-2 py-0.5 text-xs text-primary-300"
                              >
                                {INSTRUMENTS.find((i) => i.id === inst)?.label || inst}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <StatusBadge status={arr.status as 'pending' | 'processing' | 'completed' | 'failed'} />
                          <span className="text-xs text-gray-500">{formatRelativeTime(arr.created_at)}</span>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {arr.mp3_url && (
                          <div>
                            <p className="text-xs text-gray-400 mb-1.5">Full Mix (MP3)</p>
                            <AudioPlayer src={arr.mp3_url} status={arr.status as 'completed'} />
                          </div>
                        )}
                        {arr.stems && Object.keys(arr.stems).length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-gray-400 mb-2">STEM 파일</p>
                            <div className="grid grid-cols-2 gap-2">
                              {Object.entries(arr.stems).map(([stem, url]) => (
                                <div key={stem} className="rounded-lg bg-white/5 p-2">
                                  <p className="text-xs text-gray-500 mb-1.5 capitalize">{stem}</p>
                                  <AudioPlayer src={url} status="completed" compact />
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        {arr.status !== 'completed' && (
                          <div className="flex items-center justify-center py-4">
                            <StatusBadge status={arr.status as 'pending' | 'processing' | 'completed' | 'failed'} />
                          </div>
                        )}
                      </div>
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
