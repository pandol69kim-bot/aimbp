'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { Track, MusicGenerateRequest, ApiResponse } from '@/types'

export function useTrackList() {
  return useQuery({
    queryKey: ['tracks'],
    queryFn: async () => {
      const response = await api.get('/music')
      return response.data.data || []
    },
  })
}

export function useTrackById(id: string) {
  return useQuery({
    queryKey: ['tracks', id],
    queryFn: async () => {
      const response = await api.get<Track>(`/music/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useGenerateMusic() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: MusicGenerateRequest) => {
      const response = await api.post<ApiResponse<Track>>('/music/generate', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tracks'] })
    },
  })
}

export function useTrackStatus(id: string, enabled: boolean) {
  return useQuery({
    queryKey: ['tracks', id, 'status'],
    queryFn: async () => {
      const response = await api.get<Track>(`/music/${id}`)
      return response.data
    },
    enabled: enabled && !!id,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 5000
      }
      return false
    },
  })
}
