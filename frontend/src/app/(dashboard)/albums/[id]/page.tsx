'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Plus, Trash2, GripVertical, Image as ImageIcon, Music, Download, CheckCircle2, RotateCcw } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useAlbumById, useAddTrackToAlbum, useRemoveTrackFromAlbum, useUpdateAlbum } from '@/hooks/useAlbums'
import { useTrackList } from '@/hooks/useMusic'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogHeader, DialogBody, DialogFooter } from '@/components/ui/dialog'
import { StatusBadge } from '@/components/common/StatusBadge'
import { AudioPlayer } from '@/components/audio/AudioPlayer'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { Badge } from '@/components/ui/badge'
import { CoverImage } from '@/types'
import { formatDate } from '@/lib/utils'

interface CoverGroup {
  key: string
  genre: string
  mood: string
  keywords: string
  ai_model: string
  created_at: string
  images: Array<{ ratio: '1:1' | '16:9' | '9:16'; url: string; cover_id: string }>
}

function groupCompletedCovers(covers: CoverImage[]): CoverGroup[] {
  const map = new Map<string, CoverGroup>()
  covers
    .filter((c) => c.status === 'completed' && c.image_url)
    .forEach((c) => {
      const key = `${c.created_at}-${c.prompt_genre}-${c.prompt_mood}`
      if (!map.has(key)) {
        map.set(key, {
          key,
          genre: c.prompt_genre || c.genre,
          mood: c.prompt_mood || c.mood,
          keywords: c.prompt_keywords || c.keywords,
          ai_model: c.ai_model,
          created_at: c.created_at,
          images: [],
        })
      }
      map.get(key)!.images.push({
        ratio: c.size as '1:1' | '16:9' | '9:16',
        url: c.image_url!,
        cover_id: c.id,
      })
    })
  return Array.from(map.values()).sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
}

export default function AlbumDetailPage() {
  const params = useParams()
  const router = useRouter()
  const albumId = params.id as string

  const { data: album, isLoading } = useAlbumById(albumId)
  const { data: allTracks } = useTrackList()
  const queryClient = useQueryClient()
  const addTrackMutation = useAddTrackToAlbum()
  const removeTrackMutation = useRemoveTrackFromAlbum()
  const updateAlbumMutation = useUpdateAlbum()

  const [isUploadMp3Open, setIsUploadMp3Open] = useState(false)
  const [uploadFiles, setUploadFiles] = useState<File[]>([])
  const [isDragActive, setIsDragActive] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: number}>({})
  const [isUploading, setIsUploading] = useState(false)

  const [isPickCoverOpen, setIsPickCoverOpen] = useState(false)
  const [selectedCoverUrl, setSelectedCoverUrl] = useState<string | null>(null)
  const [selectedCoverId, setSelectedCoverId] = useState<string | null>(null)
  const [isApplyingCover, setIsApplyingCover] = useState(false)

  const { data: allCovers } = useQuery({
    queryKey: ['covers'],
    queryFn: async () => {
      const res = await api.get<CoverImage[]>('/cover')
      return res.data
    },
    enabled: isPickCoverOpen,
  })

  const coverGroups = allCovers ? groupCompletedCovers(allCovers) : []

  const handleApplyCover = async () => {
    if (!selectedCoverId) return
    setIsApplyingCover(true)
    try {
      await api.post(`/albums/${albumId}/cover`, { cover_id: selectedCoverId })
      queryClient.invalidateQueries({ queryKey: ['albums', albumId] })
      queryClient.invalidateQueries({ queryKey: ['albums'] })
      setIsPickCoverOpen(false)
      setSelectedCoverUrl(null)
      setSelectedCoverId(null)
    } finally {
      setIsApplyingCover(false)
    }
  }


  const handleUploadTracks = async () => {
    if (uploadFiles.length === 0) return

    setIsUploading(true)
    try {
      let uploadedCount = 0
      const totalTracks = album?.tracks.length || 0

      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i]
        const fileKey = file.name

        try {
          const formData = new FormData()
          formData.append('file', file)
          formData.append('title', file.name.replace('.mp3', ''))

          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: 0,
          }))

          const response = await api.post<any>('/music/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })

          const newTrack = response.data
          await addTrackMutation.mutateAsync({
            albumId,
            data: { track_id: newTrack.id, order: totalTracks + uploadedCount + 1 },
          })

          uploadedCount++
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: 100,
          }))
        } catch (error: any) {
          console.error(`Upload failed for ${file.name}:`, error)
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: -1, // -1 = error
          }))
        }
      }

      if (uploadedCount > 0) {
        alert(`${uploadedCount}개의 곡이 앨범에 추가되었습니다.`)
      }

      setUploadFiles([])
      setUploadProgress({})
      setIsUploadMp3Open(false)
      queryClient.invalidateQueries({ queryKey: ['tracks'] })
      queryClient.invalidateQueries({ queryKey: ['albums', albumId] })
    } catch (error: any) {
      console.error('Upload error:', error)
      alert(`업로드 실패: ${error.message}`)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true)
    } else if (e.type === 'dragleave') {
      setIsDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)

    const files = Array.from(e.dataTransfer.files).filter((file) =>
      file.name.toLowerCase().endsWith('.mp3')
    )

    if (files.length > 0) {
      setUploadFiles((prev) => [...prev, ...files])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      setUploadFiles((prev) => [...prev, ...files])
    }
  }

  const removeFile = (index: number) => {
    setUploadFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleRemoveTrack = async (trackId: string) => {
    if (confirm('이 트랙을 앨범에서 제거하시겠습니까?')) {
      await removeTrackMutation.mutateAsync({ albumId, trackId })
    }
  }

  const [isDownloading, setIsDownloading] = useState(false)
  const [isUnpublishing, setIsUnpublishing] = useState(false)

  const handlePublish = async () => {
    if (!album) return
    try {
      await api.post(`/albums/${albumId}/publish`)
      queryClient.invalidateQueries({ queryKey: ['albums', albumId] })
      queryClient.invalidateQueries({ queryKey: ['albums'] })
    } catch (error: any) {
      console.error('Publish error:', error)
      const errorDetail = error.response?.data?.detail || error.message || '알 수 없는 오류'
      alert(`발행 실패: ${errorDetail}`)
    }
  }

  const handleDownload = async () => {
    if (!album) return
    setIsDownloading(true)
    try {
      // API 라이브러리 사용 (토큰 자동 포함)
      const response = await api.get(`/albums/${albumId}/download`, {
        responseType: 'blob',
      })

      const blob = response.data
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${album.title}.zip`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      console.error('Download error:', error)
      const errorMsg =
        error.response?.data?.detail ||
        error.message ||
        '알 수 없는 오류'
      alert(`다운로드 실패: ${errorMsg}`)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleUnpublish = async () => {
    if (!album) return

    if (!confirm('발행을 취소하시겠습니까?\n앨범을 다시 수정할 수 있게 됩니다.')) {
      return
    }

    setIsUnpublishing(true)
    try {
      await api.post(`/albums/${albumId}/unpublish`)
      queryClient.invalidateQueries({ queryKey: ['albums', albumId] })
      queryClient.invalidateQueries({ queryKey: ['albums'] })
    } catch (error: any) {
      console.error('Unpublish error:', error)
      alert(`발행 취소 실패: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsUnpublishing(false)
    }
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
          <div className="flex gap-2 mt-4 flex-wrap items-center">
            {/* 발행됨 상태 */}
            {album.status === 'published' || album.is_locked ? (
              <>
                <Button
                  size="sm"
                  onClick={handleDownload}
                  isLoading={isDownloading}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  <Download className="h-3.5 w-3.5" />
                  앨범 다운로드 (ZIP)
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleUnpublish}
                  isLoading={isUnpublishing}
                  className="text-orange-400 hover:text-orange-300 border-orange-400/30 hover:border-orange-400/50"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  발행 취소
                </Button>
                <span className="text-xs text-green-400">✅ 발행됨 · 다운로드 가능</span>
              </>
            ) : (
              /* Draft 상태 */
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsPickCoverOpen(true)}
                >
                  <ImageIcon className="h-3.5 w-3.5" />
                  생성된 커버 가져오기
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push('/music')}
                >
                  <Plus className="h-3.5 w-3.5" />
                  작곡 추가
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsUploadMp3Open(true)}
                >
                  <Plus className="h-3.5 w-3.5" />
                  MP3 업로드
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePublish}
                >
                  발행하기
                </Button>
                <Button
                  size="sm"
                  onClick={() => setIsAddTrackOpen(true)}
                  disabled={trackOptions.length === 0}
                >
                  <Plus className="h-3.5 w-3.5" />
                  트랙 추가
                </Button>
              </>
            )}
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
              <div className="flex gap-2 mt-3">
                <Button
                  size="sm"
                  onClick={() => router.push('/music')}
                >
                  <Plus className="h-3.5 w-3.5" />
                  작곡 추가
                </Button>
                <Button
                  size="sm"
                  onClick={() => setIsUploadMp3Open(true)}
                  variant="outline"
                >
                  <Plus className="h-3.5 w-3.5" />
                  MP3 업로드
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {sortedTracks.map((albumTrack, index) => {
                const track = allTracks?.find((t) => t.id === albumTrack.track_id) || albumTrack.track
                if (!track) return null
                return (
                  <div
                    key={albumTrack.id}
                    className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 rounded-lg border border-white/5 bg-white/3 p-3 hover:border-white/10 transition-colors group"
                  >
                    <div className="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
                      <GripVertical className="h-4 w-4 text-gray-600 cursor-grab shrink-0" />
                      <span className="text-sm text-gray-500 w-6 text-right shrink-0">{index + 1}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{track.title}</p>
                        <p className="text-xs text-gray-500">
                          {track.genre}
                          {track.bpm && ` · ${track.bpm} BPM`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 sm:gap-3 sm:ml-auto">
                      <div className="w-32 sm:w-40 md:w-48 shrink-0">
                        <AudioPlayer
                          src={track.file_url}
                          status={track.status}
                          compact
                        />
                      </div>
                      <StatusBadge status={track.status} />
                      <button
                        onClick={() => handleRemoveTrack(albumTrack.track_id)}
                        disabled={album.status === 'published' || album.is_locked}
                        title={album.status === 'published' || album.is_locked ? "발행된 앨범은 수정할 수 없습니다" : ""}
                        className={`p-1.5 rounded-lg transition-colors opacity-0 group-hover:opacity-100 shrink-0 ${
                          album.status === 'published' || album.is_locked
                            ? 'text-gray-700 cursor-not-allowed'
                            : 'text-gray-600 hover:text-red-400 hover:bg-red-900/20'
                        }`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pick Cover Dialog */}
      <Dialog open={isPickCoverOpen} onClose={() => { setIsPickCoverOpen(false); setSelectedCoverUrl(null); setSelectedCoverId(null) }}>
        <DialogHeader title="생성된 커버 가져오기" onClose={() => { setIsPickCoverOpen(false); setSelectedCoverUrl(null); setSelectedCoverId(null) }} />
        <DialogBody>
          {coverGroups.length === 0 ? (
            <div className="flex flex-col items-center py-10 text-center">
              <ImageIcon className="h-10 w-10 text-gray-600 mb-3" />
              <p className="text-sm text-gray-400">생성된 커버가 없습니다</p>
              <p className="text-xs text-gray-500 mt-1">
                커버 생성 페이지에서 먼저 커버를 만들어주세요
              </p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
              {coverGroups.map((group) => (
                <div key={group.key} className="border border-white/5 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-2 font-medium">
                    {group.genre} · {group.mood}
                    {group.keywords && <span className="text-gray-600"> · {group.keywords}</span>}
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    {group.images.map((img) => {
                      const isSelected = selectedCoverUrl === img.url
                      return (
                        <button
                          key={img.ratio}
                          onClick={() => { setSelectedCoverUrl(img.url); setSelectedCoverId(img.cover_id) }}
                          className={`group relative rounded-lg overflow-hidden transition-all focus:outline-none ${
                            isSelected
                              ? 'ring-2 ring-primary-500 ring-offset-1 ring-offset-dark-900'
                              : 'hover:ring-1 hover:ring-white/30'
                          }`}
                        >
                          <div className={`relative bg-white/5 ${
                            img.ratio === '1:1' ? 'aspect-square' :
                            img.ratio === '16:9' ? 'aspect-video' : 'aspect-[9/16]'
                          }`}>
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={img.url}
                              alt={`Cover ${img.ratio}`}
                              className="h-full w-full object-cover"
                            />
                            {isSelected && (
                              <div className="absolute inset-0 bg-primary-500/20 flex items-center justify-center">
                                <CheckCircle2 className="h-6 w-6 text-primary-400 drop-shadow" />
                              </div>
                            )}
                            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent py-1">
                              <p className="text-center text-xs text-gray-300">{img.ratio}</p>
                            </div>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => { setIsPickCoverOpen(false); setSelectedCoverUrl(null); setSelectedCoverId(null) }}>
            취소
          </Button>
          <Button
            onClick={handleApplyCover}
            disabled={!selectedCoverId}
            isLoading={isApplyingCover}
          >
            <CheckCircle2 className="h-4 w-4" />
            앨범에 적용
          </Button>
        </DialogFooter>
      </Dialog>

      {/* MP3 Upload Dialog */}
      <Dialog open={isUploadMp3Open} onClose={() => setIsUploadMp3Open(false)}>
        <DialogHeader title="MP3 업로드" onClose={() => setIsUploadMp3Open(false)} />
        <DialogBody>
          <div className="space-y-4">
              {/* Drag Drop Area */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-500/5'
                    : 'border-white/20 bg-white/5 hover:border-white/30'
                }`}
              >
                <input
                  type="file"
                  multiple
                  accept=".mp3"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-input"
                />
                <label htmlFor="file-input" className="cursor-pointer space-y-2">
                  <div className="text-3xl">📁</div>
                  <p className="text-sm font-medium text-white">MP3 파일을 드래그하거나 클릭해서 선택</p>
                  <p className="text-xs text-gray-400">여러 개 선택 가능</p>
                </label>
              </div>

              {/* File List */}
              {uploadFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-300">
                    선택된 파일 ({uploadFiles.length}개)
                  </p>
                  <div className="space-y-2 max-h-[200px] overflow-y-auto">
                    {uploadFiles.map((file, index) => {
                      const progress = uploadProgress[file.name] ?? 0
                      const isError = progress === -1

                      return (
                        <div
                          key={`${file.name}-${index}`}
                          className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 p-2"
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-white truncate">{file.name}</p>
                            {isUploading && progress > 0 && progress < 100 && (
                              <div className="mt-1 h-1 bg-white/10 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-primary-500 transition-all"
                                  style={{ width: `${progress}%` }}
                                />
                              </div>
                            )}
                            {progress === 100 && (
                              <p className="text-xs text-green-400 mt-1">✓ 완료</p>
                            )}
                            {isError && (
                              <p className="text-xs text-red-400 mt-1">✗ 실패</p>
                            )}
                          </div>
                          {!isUploading && (
                            <button
                              onClick={() => removeFile(index)}
                              className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                              type="button"
                            >
                              ✕
                            </button>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
          </div>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsUploadMp3Open(false)}>
            취소
          </Button>
          <Button
            onClick={handleUploadTracks}
            isLoading={isUploading}
            disabled={uploadFiles.length === 0}
          >
            {uploadFiles.length > 0 ? `${uploadFiles.length}개 업로드` : '선택 후 업로드'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  )
}
