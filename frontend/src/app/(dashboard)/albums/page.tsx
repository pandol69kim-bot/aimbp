'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Disc, Plus, Image as ImageIcon } from 'lucide-react'
import { useAlbumList, useCreateAlbum } from '@/hooks/useAlbums'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import { Dialog, DialogHeader, DialogBody, DialogFooter } from '@/components/ui/dialog'
import { StatusBadge } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { formatDate } from '@/lib/utils'

export default function AlbumsPage() {
  const { data: albums, isLoading } = useAlbumList()
  const createMutation = useCreateAlbum()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await createMutation.mutateAsync({ title, description })
    setTitle('')
    setDescription('')
    setIsDialogOpen(false)
  }

  if (isLoading) return <PageLoader label="앨범 목록 로딩 중..." />

  return (
    <div className="page-container">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="section-title flex items-center gap-2">
            <Disc className="h-5 w-5 text-primary-400" />
            앨범 관리
          </h1>
          <p className="section-desc">음악을 앨범으로 묶어 관리하세요</p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="h-4 w-4" />
          새 앨범
        </Button>
      </div>

      {!albums || albums.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center py-16">
            <Disc className="h-14 w-14 text-gray-600 mb-4" />
            <p className="text-base text-gray-300 font-medium">앨범이 없습니다</p>
            <p className="text-sm text-gray-500 mt-1 mb-4">첫 앨범을 만들어보세요</p>
            <Button onClick={() => setIsDialogOpen(true)}>
              <Plus className="h-4 w-4" />
              앨범 만들기
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {albums.map((album) => (
            <Link key={album.id} href={`/albums/${album.id}`}>
              <Card className="cursor-pointer hover:border-primary-500/30 hover:-translate-y-1 transition-all duration-200 group">
                <div className="aspect-square rounded-t-xl overflow-hidden bg-gradient-to-br from-dark-700 to-dark-800 flex items-center justify-center">
                  {album.cover_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={album.cover_url}
                      alt={album.title}
                      className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="flex flex-col items-center gap-2">
                      <ImageIcon className="h-12 w-12 text-gray-600" />
                      <span className="text-xs text-gray-600">커버 없음</span>
                    </div>
                  )}
                </div>
                <CardContent className="p-4">
                  <p className="text-sm font-semibold text-white truncate mb-1">{album.title}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {album.tracks.length}개 트랙
                    </span>
                    <StatusBadge status={album.status} />
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{formatDate(album.created_at)}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Create Album Dialog */}
      <Dialog open={isDialogOpen} onClose={() => setIsDialogOpen(false)}>
        <DialogHeader title="새 앨범 만들기" onClose={() => setIsDialogOpen(false)} />
        <DialogBody>
          <form id="create-album-form" onSubmit={handleCreate} className="space-y-4">
            <Input
              label="앨범 제목"
              placeholder="앨범 이름을 입력하세요"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <Textarea
              label="설명 (선택)"
              placeholder="앨범에 대한 설명을 입력하세요"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </form>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
            취소
          </Button>
          <Button
            type="submit"
            form="create-album-form"
            isLoading={createMutation.isPending}
          >
            만들기
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  )
}
