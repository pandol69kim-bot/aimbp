'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Play, Pause, Volume2, VolumeX, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatDuration } from '@/lib/utils'

interface AudioPlayerProps {
  src?: string
  title?: string
  status?: 'pending' | 'processing' | 'completed' | 'failed'
  className?: string
  compact?: boolean
}

export function AudioPlayer({ src, title, status, className, compact = false }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const isDisabled = !src || status === 'processing' || status === 'pending' || status === 'failed'

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime)
    const handleDurationChange = () => setDuration(audio.duration)
    const handleEnded = () => setIsPlaying(false)
    const handleWaiting = () => setIsLoading(true)
    const handleCanPlay = () => setIsLoading(false)

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('durationchange', handleDurationChange)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('waiting', handleWaiting)
    audio.addEventListener('canplay', handleCanPlay)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('durationchange', handleDurationChange)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('waiting', handleWaiting)
      audio.removeEventListener('canplay', handleCanPlay)
    }
  }, [])

  const togglePlay = useCallback(async () => {
    const audio = audioRef.current
    if (!audio || isDisabled) return

    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
    } else {
      setIsLoading(true)
      try {
        await audio.play()
        setIsPlaying(true)
      } catch {
        setIsPlaying(false)
      } finally {
        setIsLoading(false)
      }
    }
  }, [isPlaying, isDisabled])

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return
    const newTime = parseFloat(e.target.value)
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current
    if (!audio) return
    const newVolume = parseFloat(e.target.value)
    audio.volume = newVolume
    setVolume(newVolume)
    setIsMuted(newVolume === 0)
  }

  const toggleMute = () => {
    const audio = audioRef.current
    if (!audio) return
    if (isMuted) {
      audio.volume = volume || 0.5
      setIsMuted(false)
    } else {
      audio.volume = 0
      setIsMuted(true)
    }
  }

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0

  const renderDisabledState = () => {
    if (status === 'processing' || status === 'pending') {
      return (
        <div className="flex items-center gap-2 text-yellow-400">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-xs">생성 중...</span>
        </div>
      )
    }
    if (status === 'failed') {
      return <span className="text-xs text-red-400">생성 실패</span>
    }
    return <span className="text-xs text-gray-500">파일 없음</span>
  }

  if (compact) {
    return (
      <div className={cn('flex items-center gap-3', className)}>
        {src && <audio ref={audioRef} src={src} preload="metadata" />}
        <button
          onClick={togglePlay}
          disabled={isDisabled}
          className={cn(
            'flex h-8 w-8 items-center justify-center rounded-full transition-colors',
            isDisabled
              ? 'bg-white/5 text-gray-600 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-500 active:bg-primary-700'
          )}
        >
          {isLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : isPlaying ? (
            <Pause className="h-3.5 w-3.5" />
          ) : (
            <Play className="h-3.5 w-3.5 ml-0.5" />
          )}
        </button>
        {isDisabled ? (
          renderDisabledState()
        ) : (
          <div className="flex flex-1 items-center gap-2">
            <span className="text-xs text-gray-500 w-10 text-right">
              {formatDuration(currentTime)}
            </span>
            <div className="relative flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className="absolute inset-y-0 left-0 bg-primary-500 rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
              <input
                type="range"
                min={0}
                max={duration || 100}
                value={currentTime}
                onChange={handleSeek}
                className="absolute inset-0 w-full opacity-0 cursor-pointer"
              />
            </div>
            <span className="text-xs text-gray-500 w-10">{formatDuration(duration)}</span>
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      className={cn(
        'rounded-xl border border-white/10 bg-white/5 p-4',
        className
      )}
    >
      {src && <audio ref={audioRef} src={src} preload="metadata" />}
      {title && <p className="mb-3 text-sm font-medium text-white truncate">{title}</p>}

      {isDisabled ? (
        <div className="flex items-center justify-center py-4">{renderDisabledState()}</div>
      ) : (
        <div className="space-y-3">
          {/* Progress Bar */}
          <div className="space-y-1">
            <div className="relative h-2 bg-white/10 rounded-full overflow-hidden cursor-pointer">
              <div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary-600 to-accent-500 rounded-full transition-all"
                style={{ width: `${progressPercent}%` }}
              />
              <input
                type="range"
                min={0}
                max={duration || 100}
                value={currentTime}
                onChange={handleSeek}
                className="absolute inset-0 w-full opacity-0 cursor-pointer"
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>{formatDuration(currentTime)}</span>
              <span>{formatDuration(duration)}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-600 text-white hover:bg-primary-500 active:bg-primary-700 transition-colors"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : isPlaying ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4 ml-0.5" />
              )}
            </button>

            {/* Volume */}
            <div className="flex items-center gap-2 ml-auto">
              <button
                onClick={toggleMute}
                className="text-gray-400 hover:text-white transition-colors"
              >
                {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
              </button>
              <div className="relative w-20 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 bg-white/40 rounded-full"
                  style={{ width: `${isMuted ? 0 : volume * 100}%` }}
                />
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="absolute inset-0 w-full opacity-0 cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
