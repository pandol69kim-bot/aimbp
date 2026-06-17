'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { Album, CreateAlbumRequest, AddTrackToAlbumRequest, ApiResponse } from '@/types'

export function useAlbumList() {
  return useQuery({
    queryKey: ['albums'],
    queryFn: async () => {
      const response = await api.get('/albums')
      return response.data || []
    },
  })
}

export function useAlbumById(id: string) {
  return useQuery({
    queryKey: ['albums', id],
    queryFn: async () => {
      const response = await api.get<Album>(`/albums/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateAlbum() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreateAlbumRequest) => {
      const response = await api.post<ApiResponse<Album>>('/albums', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['albums'] })
    },
  })
}

export function useAddTrackToAlbum() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ albumId, data }: { albumId: string; data: AddTrackToAlbumRequest }) => {
      const response = await api.post<ApiResponse<Album>>(`/albums/${albumId}/tracks`, data)
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['albums', variables.albumId] })
    },
  })
}

export function useRemoveTrackFromAlbum() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ albumId, trackId }: { albumId: string; trackId: string }) => {
      const response = await api.delete(`/albums/${albumId}/tracks/${trackId}`)
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['albums', variables.albumId] })
    },
  })
}

export function useUpdateAlbum() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CreateAlbumRequest & { status: string }> }) => {
      const response = await api.patch<ApiResponse<Album>>(`/albums/${id}`, data)
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['albums', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['albums'] })
    },
  })
}
