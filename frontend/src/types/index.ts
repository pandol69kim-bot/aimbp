export interface User {
  id: string
  email: string
  nickname: string
  plan: 'free' | 'creator' | 'studio' | 'label'
  is_active: boolean
  created_at: string
}

export interface Lyrics {
  id: string
  title: string
  prompt_subject: string
  prompt_mood: string
  prompt_genre: string
  ai_model: string
  verse: string
  chorus: string
  bridge: string
  hook: string
  created_at: string
}

export interface Track {
  id: string
  title: string
  genre: string
  bpm?: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  file_url?: string
  duration?: number
  ai_service?: string
  error_message?: string
  created_at: string
}

export interface Album {
  id: string
  title: string
  description?: string
  cover_url?: string
  status: 'draft' | 'published'
  tracks: AlbumTrack[]
  created_at: string
}

export interface AlbumTrack {
  id: string
  track_id: string
  order: number
  track?: Track
}

export interface Arrangement {
  id: string
  track_id: string
  instruments: string[]
  wav_url?: string
  mp3_url?: string
  stems?: Record<string, string>
  status: string
  created_at: string
}

export interface VocalLibrary {
  id: string
  name: string
  gender: 'male' | 'female' | 'neutral'
  genre: string
  language: string
  sample_url?: string
  description?: string
}

export interface VocalTrack {
  id: string
  track_id: string
  vocal_id: string
  language: string
  file_url?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
}

export interface MasteringJob {
  id: string
  track_id: string
  platform: 'spotify' | 'apple_music' | 'youtube_music'
  original_url?: string
  mastered_url?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  before_info?: AudioInfo
  after_info?: AudioInfo
  created_at: string
}

export interface AudioInfo {
  lufs?: number
  peak?: number
  dynamic_range?: number
  sample_rate?: number
  bit_depth?: number
}

export interface CoverImage {
  id: string
  genre: string
  mood: string
  keywords: string
  ai_model: string
  images: CoverVariant[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
}

export interface CoverVariant {
  ratio: '1:1' | '16:9' | '9:16'
  url: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error: string | null
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  total: number
  page: number
  limit: number
  error: string | null
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  nickname: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LyricsGenerateRequest {
  title: string
  prompt_subject: string
  prompt_mood: string
  prompt_genre: string
  artist_style?: string
  language?: string
  ai_model?: string
}

export interface MusicGenerateRequest {
  title: string
  genre: string
  bpm?: number
  mood?: string
  lyrics_id?: string
}

export interface ArrangementGenerateRequest {
  track_id: string
  instruments: string[]
}

export interface VocalGenerateRequest {
  track_id: string
  vocal_id: string
  language: string
}

export interface MasteringRequest {
  track_id: string
  platform: 'spotify' | 'apple_music' | 'youtube_music'
}

export interface CoverGenerateRequest {
  genre: string
  mood: string
  keywords: string
  ai_model?: string
}

export interface CreateAlbumRequest {
  title: string
  description?: string
}

export interface AddTrackToAlbumRequest {
  track_id: string
  order?: number
}
