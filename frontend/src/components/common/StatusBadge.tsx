import { cn } from '@/lib/utils'

type Status = 'pending' | 'processing' | 'completed' | 'failed' | 'draft' | 'published'

interface StatusBadgeProps {
  status: Status
  className?: string
}

const statusConfig: Record<
  Status,
  { label: string; className: string; dotClassName: string; animate?: boolean }
> = {
  pending: {
    label: '대기 중',
    className: 'border-gray-500/30 bg-gray-900/30 text-gray-400',
    dotClassName: 'bg-gray-400',
  },
  processing: {
    label: '처리 중',
    className: 'border-yellow-500/30 bg-yellow-900/20 text-yellow-400',
    dotClassName: 'bg-yellow-400',
    animate: true,
  },
  completed: {
    label: '완료',
    className: 'border-green-500/30 bg-green-900/20 text-green-400',
    dotClassName: 'bg-green-400',
  },
  failed: {
    label: '실패',
    className: 'border-red-500/30 bg-red-900/20 text-red-400',
    dotClassName: 'bg-red-400',
  },
  draft: {
    label: '초안',
    className: 'border-gray-500/30 bg-gray-900/30 text-gray-400',
    dotClassName: 'bg-gray-400',
  },
  published: {
    label: '발행됨',
    className: 'border-green-500/30 bg-green-900/20 text-green-400',
    dotClassName: 'bg-green-400',
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium',
        config.className,
        className
      )}
    >
      <span
        className={cn(
          'h-1.5 w-1.5 rounded-full',
          config.dotClassName,
          config.animate && 'animate-pulse'
        )}
      />
      {config.label}
    </span>
  )
}
