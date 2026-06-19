'use client'

import { useState } from 'react'
import { Sparkles, FileText, Trash2, ChevronDown, ChevronUp, Upload, Download } from 'lucide-react'
import { useLyricsList, useGenerateLyrics, useDeleteLyrics } from '@/hooks/useLyrics'
import api from '@/lib/api'
import { useQueryClient } from '@tanstack/react-query'
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
  { value: 'openai', label: 'OpenAI GPT-4o-mini' },
  { value: 'claude', label: 'Anthropic Claude Haiku' },
]

function LyricsCard({ lyrics, onDelete }: { lyrics: Lyrics; onDelete: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false)

  const handleDownloadMd = () => {
    // MD 형식으로 가사 변환
    const mdContent = `# ${lyrics.title}

**Genre:** ${lyrics.prompt_genre || 'Unknown'}
**Mood:** ${lyrics.prompt_mood || 'Unknown'}
**Created:** ${new Date(lyrics.created_at).toLocaleString()}

---

## Verse

${lyrics.verse || '(No verse)'}

---

## Chorus

${lyrics.chorus || '(No chorus)'}

---

## Bridge

${lyrics.bridge || '(No bridge)'}

---

## Hook

${lyrics.hook || '(No hook)'}
`

    // Blob 생성
    const blob = new Blob([mdContent], { type: 'text/markdown' })
    const url = window.URL.createObjectURL(blob)

    // 다운로드
    const link = document.createElement('a')
    link.href = url
    link.download = `${lyrics.title}.md`
    document.body.appendChild(link)
    link.click()
    link.parentNode?.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

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
              onClick={handleDownloadMd}
              className="p-1.5 text-gray-400 hover:text-primary-400 rounded-lg hover:bg-primary-900/20 transition-colors"
              title="MD 파일 다운로드"
            >
              <Download className="h-4 w-4" />
            </button>
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
          <div className="bg-gray-950/50 rounded-lg p-6 font-mono text-xs">
            {/* 제목과 메타데이터 */}
            <div className="mb-6 pb-4 border-b border-white/10">
              <p className="text-base font-bold text-primary-300 mb-2"># {lyrics.title}</p>
              <p className="text-gray-400">
                {lyrics.prompt_genre && `Genre: ${lyrics.prompt_genre}`}
                {lyrics.prompt_genre && lyrics.prompt_mood && ' • '}
                {lyrics.prompt_mood && `Mood: ${lyrics.prompt_mood}`}
              </p>
            </div>

            {/* 가사 내용 - 원본 형식 그대로 */}
            <div className="space-y-4 text-gray-200 leading-relaxed">
              {lyrics.verse && (
                <div>
                  <p className="text-sm font-semibold text-primary-300 mb-2">## Verse</p>
                  <p className="whitespace-pre-line text-xs">{lyrics.verse}</p>
                </div>
              )}

              {lyrics.chorus && (
                <div>
                  <p className="text-sm font-semibold text-accent-300 mb-2 mt-4">## Chorus</p>
                  <p className="whitespace-pre-line text-xs">{lyrics.chorus}</p>
                </div>
              )}

              {lyrics.bridge && (
                <div>
                  <p className="text-sm font-semibold text-secondary-300 mb-2 mt-4">## Bridge</p>
                  <p className="whitespace-pre-line text-xs">{lyrics.bridge}</p>
                </div>
              )}

              {lyrics.hook && (
                <div>
                  <p className="text-sm font-semibold text-yellow-300 mb-2 mt-4">## Hook</p>
                  <p className="whitespace-pre-line text-xs">{lyrics.hook}</p>
                </div>
              )}
            </div>
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
  const queryClient = useQueryClient()

  const [title, setTitle] = useState('')
  const [subject, setSubject] = useState('')
  const [mood, setMood] = useState('')
  const [genre, setGenre] = useState('')
  const [artistStyle, setArtistStyle] = useState('')
  const [language, setLanguage] = useState('korean')
  const [uploadFiles, setUploadFiles] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<{[key: string]: number}>({})
  const [isUploading, setIsUploading] = useState(false)
  const [isDragActive, setIsDragActive] = useState(false)
  const [aiModel, setAiModel] = useState('openai')
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
      file.name.toLowerCase().endsWith('.md')
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

  const handleUploadMd = async () => {
    if (uploadFiles.length === 0) return

    setIsUploading(true)
    try {
      let uploadedCount = 0

      for (let i = 0; i < uploadFiles.length; i++) {
        const file = uploadFiles[i]
        const fileKey = file.name

        try {
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: 0,
          }))

          const formData = new FormData()
          formData.append('file', file)

          const response = await api.post('/lyrics/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })

          const newLyrics = response.data.data
          if (i === uploadFiles.length - 1) {
            setGeneratedLyrics(newLyrics)
          }

          uploadedCount++
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: 100,
          }))
        } catch (error: any) {
          console.error(`Upload failed for ${file.name}:`, error)
          setUploadProgress((prev) => ({
            ...prev,
            [fileKey]: -1,
          }))
        }
      }

      if (uploadedCount > 0) {
        alert(`${uploadedCount}개의 가사가 생성 목록에 추가되었습니다.`)
      }

      setUploadFiles([])
      setUploadProgress({})
      queryClient.invalidateQueries({ queryKey: ['lyricsList'] })
    } catch (error: any) {
      console.error('Upload error:', error)
      alert(`업로드 실패: ${error.message}`)
    } finally {
      setIsUploading(false)
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
        <div className="space-y-6">
          {/* MD Upload Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-4 w-4" />
                MD 파일 업로드
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Drag Drop Area */}
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  className={`relative rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
                    isDragActive
                      ? 'border-primary-500 bg-primary-500/5'
                      : 'border-white/20 bg-white/5 hover:border-white/30'
                  }`}
                >
                  <input
                    type="file"
                    accept=".md"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    id="md-file-input"
                  />
                  <label htmlFor="md-file-input" className="cursor-pointer space-y-2">
                    <div className="text-2xl">📝</div>
                    <p className="text-sm font-medium text-white">MD 파일을 드래그하거나 클릭</p>
                    <p className="text-xs text-gray-400">작사된 마크다운 파일 업로드</p>
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

                {/* Upload Button */}
                <Button
                  onClick={handleUploadMd}
                  isLoading={isUploading}
                  disabled={uploadFiles.length === 0}
                  className="w-full"
                >
                  <Upload className="h-3.5 w-3.5" />
                  {uploadFiles.length > 0 ? `${uploadFiles.length}개 업로드` : '파일 선택'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Form */}
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
