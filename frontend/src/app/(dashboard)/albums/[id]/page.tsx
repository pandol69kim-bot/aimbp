'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Plus, Trash2, GripVertical, Image as ImageIcon, Music } from 'lucide-react'
import { useAlbumById, useAddTrackToAlbum, useRemoveTrackFromAlbum, useUpdateAlbum } from '@/hooks/useAlbums'
import { useTrackList } from '@/hooks/useMusic'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogHeader, DialogBody, DialogFooter } from '@/components/ui/dialog'
import { StatusBadge } from '@/components/common/StatusBadge'
import { AudioPlayer } from '@/components/audio/AudioPlayer'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'

export default function AlbumDetailPage() {
  const params = useParams()
  const router = useRouter()
  const albumId = params.id as string

  const { data: album, isLoading } = useAlbumById(albumId)
  const { data: allTracks } = useTrackList()
  const addTrackMutation = useAddTrackToAlbum()
  const removeTrackMutation = useRemoveTrackFromAlbum()
  const updateAlbumMutation = useUpdateAlbum()

  const [isAddTrackOpen, setIsAddTrackOpen] = useState(false)
  const [selectedTrackId, setSelectedTrackId] = useState('')

  const completedTracks = allTracks?.filter((t) => t.status === 'completed') || []
  const albumTrackIds = album?.tracks.map((at) => at.track_id) || []
  const availableTracks = completedTracks.filter((t) => !albumTrackIds.includes(t.id))
  const trackOptions = availableTracks.map((t) => ({ value: t.id, label: t.title }))

  const handleAddTrack = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTrackId) return
    await addTrackMutation.mutateAsync({ albumId, data: { track_id: selectedTrackId } })
    setSelectedTrackId('')
    setIsAddTrackOpen(false)
  }

  const handleRemoveTrack = async (trackId: string) => {
    if (confirm('이 트랙을 앨범에서 제거하시겠습니까?')) {
      await removeTrackMutation.mutateAsync({ albumId, trackId })
    }
  }

  const handlePublish = async () => {
    if (!album) return
    const newStatus = album.status === 'published' ? 'draft' : 'published'
    await updateAlbumMutation.mutateAsync({ id: albumId, data: { status: newStatus } })
  }

  if (isLoading) return <PageLoader label="앨범 로딩 중..." />
  if (!album) {
    return (
      <div className="page-container">
        <p className="text-gray-400">앨범을 찾을 수 없습니다</p>
      </div>
    )
  }

  const sortedTracks = [...album.tracks].sort((a, b) => a.order - b.order)

  return (
    <div className="page-container">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        앨범 목록으로
      </button>

      {/* Album Header */}
      <div className="flex flex-col sm:flex-row gap-6 mb-8">
        <div className="h-40 w-40 shrink-0 rounded-xl overflow-hidden bg-gradient-to-br from-dark-700 to-dark-800 flex items-center justify-center">
          {album.cover_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={album.cover_url} alt={album.title} className="h-full w-full object-cover" />
          ) : (
            <ImageIcon className="h-12 w-12 text-gray-600" />
          )}
        </div>
        <div className="flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-white">{album.title}</h1>
              <StatusBadge status={album.status} />
            </div>
            {album.description && (
              <p className="text-sm text-gray-400 mb-2">{album.description}</p>
            )}
            <p className="text-xs text-gray-500">
              {sortedTracks.length}개 트랙 · 생성: {formatDate(album.created_at)}
            </p>
          </div>
          <div className="flex gap-2 mt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePublish}
              isLoading={updateAlbumMutation.isPending}
            >
              {album.status === 'published' ? '비공개로 전환' : '발행하기'}
            </Button>
            <Button
              size="sm"
              onClick={() => setIsAddTrackOpen(true)}
              disabled={trackOptions.length === 0}
            >
              <Plus className="h-3.5 w-3.5" />
              트랙 추가
            </Button>
          </div>
        </div>
      </div>

      {/* Track List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Music className="h-4 w-4 text-primary-400" />
            트랙 목록
            <Badge variant="outline" className="ml-1">{sortedTracks.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sortedTracks.length === 0 ? (
            <div className="flex flex-col items-center py-10">
              <Music className="h-10 w-10 text-gray-600 mb-3" />
              <p className="text-sm text-gray-400">앨범에 트랙이 없습니다</p>
              <Button
                size="sm"
                className="mt-3"
                onClick={() => setIsAddTrackOpen(true)}
                disabled={trackOptions.length === 0}
              >
                <Plus className="h-3.5 w-3.5" />
                트랙 추가
              </Button>
              {trackOptions.length === 0 && (
                <p className="text-xs text-gray-500 mt-2">
                  완료된 트랙이 없습니다. 먼저 작곡을 완료하세요.
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {sortedTracks.map((albumTrack, index) => {
                const track = allTracks?.find((t) => t.id === albumTrack.track_id) || albumTrack.track
                if (!track) return null
                return (
                  <div
                    key={albumTrack.id}
                    className="flex items-center gap-4 rounded-lg border border-white/5 bg-white/3 p-3 hover:border-white/10 transition-colors group"
                  >
                    <GripVertical className="h-4 w-4 text-gray-600 cursor-grab" />
                    <span className="text-sm text-gray-500 w-6 text-right shrink-0">{index + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{track.title}</p>
                      <p className="text-xs text-gray-500">
                        {track.genre}
                        {track.bpm && ` · ${track.bpm} BPM`}
                      </p>
                    </div>
                    <div className="w-48 shrink-0">
                      <AudioPlayer
                        src={track.file_url}
                        status={track.status}
                        compact
                      />
                    </div>
                    <StatusBadge status={track.status} />
                    <button
                      onClick={() => handleRemoveTrack(albumTrack.track_id)}
                      className="p-1.5 text-gray-600 hover:text-red-400 hover:bg-red-900/20 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Track Dialog */}
      <Dialog open={isAddTrackOpen} onClose={() => setIsAddTrackOpen(false)}>
        <DialogHeader title="트랙 추가" onClose={() => setIsAddTrackOpen(false)} />
        <DialogBody>
          <form id="add-track-form" onSubmit={handleAddTrack} className="space-y-4">
            {trackOptions.length > 0 ? (
              <Select
                label="트랙 선택"
                options={trackOptions}
                placeholder="추가할 트랙 선택"
                value={selectedTrackId}
                onChange={(e) => setSelectedTrackId(e.target.value)}
                required
              />
            ) : (
              <p className="text-sm text-gray-400">
                추가 가능한 트랙이 없습니다. 완료된 트랙이 필요합니다.
              </p>
            )}
          </form>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsAddTrackOpen(false)}>
            취소
          </Button>
          <Button
            type="submit"
            form="add-track-form"
            isLoading={addTrackMutation.isPending}
            disabled={trackOptions.length === 0 || !selectedTrackId}
          >
            추가
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  )
}
