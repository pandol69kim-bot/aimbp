'use client'

import * as React from 'react'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface DialogProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  className?: string
}

function Dialog({ open, onClose, children, className }: DialogProps) {
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (open) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={cn(
          'relative z-10 w-full max-w-lg rounded-xl border border-white/10 bg-dark-800 p-6 shadow-2xl',
          'animate-in fade-in-0 zoom-in-95 duration-200',
          className
        )}
      >
        {children}
      </div>
    </div>
  )
}

interface DialogHeaderProps {
  title: string
  onClose?: () => void
  className?: string
}

function DialogHeader({ title, onClose, className }: DialogHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between mb-4', className)}>
      <h2 className="text-lg font-semibold text-white">{title}</h2>
      {onClose && (
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}

function DialogBody({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('text-gray-300', className)}>{children}</div>
}

function DialogFooter({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('flex items-center justify-end gap-3 mt-6', className)}>{children}</div>
  )
}

export { Dialog, DialogHeader, DialogBody, DialogFooter }
