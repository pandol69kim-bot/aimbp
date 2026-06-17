'use client'

import { useState } from 'react'
import { Wand2, Sparkles, Download, Music } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useTrackList } from '@/hooks/useMusic'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusBadge } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatRelativeTime } from '@/lib/utils'
import { MasteringJob } from '@/types'

const platformOptions = [
  { value: 'spotify', label: 'Spotify (-14 LUFS)' },
  { value: 'apple_music', label: 'Apple Music (-16 LUFS)' },
  { value: 'youtube_music', label: 'YouTube Music (-13 LUFS)' },
]

const platformInfo: Record<string, { lufs: string; description: string; color: string }> = {
  spotify: { lufs: '-14 LUFS', description: 'Spotify 스트리밍 최적화', color: 'text-green-400' },
  apple_music: { lufs: '-16 LUFS', description: 'Apple Music 고음질 최적화', color: 'text-pink-400' },
  youtube_music: { lufs: '-13 LUFS', description: 'YouTube Music 최적화', color: 'text-red-400' },
}

export default function MasteringPage() {
  const queryClient = useQueryClient()
  const { data: tracks } = useTrackList()
  const [selectedTrackId, setSelectedTrackId] = useState('')
  const [platform, setPlatform] = useState('spotify')

  const { data: masteringJobs, isLoading } = useQuery({
    queryKey: ['mastering'],
    queryFn: async () => {
      const res = await api.get<MasteringJob[]>('/mastering')
      return res.data
    },
  })

  const processMutation = useMutation({
    mutationFn: async (data: { track_id: string; platform: string }) => {
      const res = await api.post('/mastering/process', data)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mastering'] })
    },
  })

  const completedTracks = tracks?.filter((t) => t.status === 'completed') || []
  const trackOptions = completedTracks.map((t) => ({ value: t.id, label: t.title }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTrackId) return
    await processMutation.mutateAsync({ track_id: selectedTrackId, platform })
  }

  if (isLoading) return <PageLoader label="마스터링 데이터 로딩 중..." />

  const selectedPlatformInfo = platformInfo[platform]

  return (
    <div className="page-container">
      <div className="mb-6">
        <h1 className="section-title flex items-center gap-2">
          <Wand2 className="h-5 w-5 text-primary-400" />
          마스터링
        </h1>
        <p className="section-desc">각 플랫폼에 최적화된 마스터링을 적용하세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>마스터링 설정</CardTitle>
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
                <Select
                  label="타겟 플랫폼"
                  options={platformOptions}
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                />

                {/* Platform Info */}
                <div className="rounded-lg border border-white/10 bg-white/5 p-4">
                  <p className={`text-sm font-semibold mb-1 ${selectedPlatformInfo.color}`}>
                    {selectedPlatformInfo.description}
                  </p>
                  <p className="text-xs text-gray-400">목표 음량: {selectedPlatformInfo.lufs}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    AI가 자동으로 EQ, 컴프레서, 리미터를 조정하여 플랫폼에 최적화합니다.
                  </p>
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  isLoading={processMutation.isPending}
                  disabled={!selectedTrackId}
                >
                  <Sparkles className="h-4 w-4" />
                  마스터링 시작
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">마스터링 결과</h2>
            <span className="text-sm text-gray-500">{masteringJobs?.length || 0}개</span>
          </div>

          {!masteringJobs || masteringJobs.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center py-12">
                <Wand2 className="h-10 w-10 text-gray-600 mb-2" />
                <p className="text-sm text-gray-400">마스터링 결과가 없습니다</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {masteringJobs.map((job) => {
                const track = tracks?.find((t) => t.id === job.track_id)
                const info = platformInfo[job.platform]
                return (
                  <Card key={job.id} className="hover:border-white/20 transition-colors">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-base">
                            {track?.title || '알 수 없는 트랙'}
                          </CardTitle>
                          <p className={`text-xs mt-1 ${info?.color || 'text-gray-400'}`}>
                            {info?.description} · {formatRelativeTime(job.created_at)}
                          </p>
                        </div>
                        <StatusBadge status={job.status} />
                      </div>
                    </CardHeader>
                    {job.status === 'completed' && (
                      <CardContent>
                        {/* Before/After */}
                        {(job.before_info || job.after_info) && (
                          <div className="grid grid-cols-2 gap-3 mb-4">
                            {job.before_info && (
                              <div className="rounded-lg bg-white/5 p-3">
                                <p className="text-xs font-semibold text-gray-400 mb-2">원본</p>
                                {job.before_info.lufs !== undefined && (
                                  <p className="text-xs text-gray-300">LUFS: {job.before_info.lufs}</p>
                                )}
                                {job.before_info.peak !== undefined && (
                                  <p className="text-xs text-gray-300">Peak: {job.before_info.peak} dB</p>
                                )}
                                {job.before_info.dynamic_range !== undefined && (
                                  <p className="text-xs text-gray-300">DR: {job.before_info.dynamic_range}</p>
                                )}
                              </div>
                            )}
                            {job.after_info && (
                              <div className="rounded-lg bg-primary-900/20 border border-primary-500/20 p-3">
                                <p className="text-xs font-semibold text-primary-400 mb-2">마스터링 후</p>
                                {job.after_info.lufs !== undefined && (
                                  <p className="text-xs text-gray-300">LUFS: {job.after_info.lufs}</p>
                                )}
                                {job.after_info.peak !== undefined && (
                                  <p className="text-xs text-gray-300">Peak: {job.after_info.peak} dB</p>
                                )}
                                {job.after_info.dynamic_range !== undefined && (
                                  <p className="text-xs text-gray-300">DR: {job.after_info.dynamic_range}</p>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                        {/* Download */}
                        {job.mastered_url && (
                          <a
                            href={job.mastered_url}
                            download
                            className="flex items-center gap-2 rounded-lg border border-primary-500/30 bg-primary-900/20 px-4 py-2.5 text-sm text-primary-300 hover:bg-primary-900/40 transition-colors w-fit"
                          >
                            <Download className="h-4 w-4" />
                            마스터링 파일 다운로드
                          </a>
                        )}
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
