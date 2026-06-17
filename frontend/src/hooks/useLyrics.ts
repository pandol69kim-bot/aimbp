'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { Lyrics, LyricsGenerateRequest, ApiResponse } from '@/types'

export function useLyricsList() {
  return useQuery({
    queryKey: ['lyrics'],
    queryFn: async () => {
      const response = await api.get('/lyrics')
      return response.data.data || []
    },
  })
}

export function useLyricsById(id: string) {
  return useQuery({
    queryKey: ['lyrics', id],
    queryFn: async () => {
      const response = await api.get<Lyrics>(`/lyrics/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useGenerateLyrics() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: LyricsGenerateRequest) => {
      const response = await api.post<ApiResponse<Lyrics>>('/lyrics/generate', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lyrics'] })
    },
  })
}

export function useDeleteLyrics() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.delete(`/lyrics/${id}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lyrics'] })
    },
  })
}
