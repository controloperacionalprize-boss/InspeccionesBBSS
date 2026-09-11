import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Loader2 } from 'lucide-react'

const variantes = {
  primary:
    'bg-brand-700 text-white shadow-soft hover:bg-brand-800 disabled:bg-brand-200 disabled:text-white disabled:shadow-none',
  secondary:
    'bg-white text-ink-soft border border-line hover:border-brand-300 hover:text-brand-700 disabled:opacity-50',
  danger: 'bg-red-600 text-white shadow-soft hover:bg-red-700 disabled:bg-red-200',
  ghost: 'text-brand-700 hover:bg-brand-50 disabled:opacity-50',
} as const

const tamanos = {
  md: 'h-10 px-4 text-sm',
  sm: 'h-8 px-3 text-[13px]',
} as const

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: keyof typeof variantes
  size?: keyof typeof tamanos
  loading?: boolean
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  type = 'button',
  loading = false,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`inline-flex shrink-0 items-center justify-center gap-2 rounded-lg font-semibold transition-colors duration-150 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand-100 disabled:cursor-not-allowed ${tamanos[size]} ${variantes[variant]} ${className}`}
      {...props}
    >
      {loading ? <Loader2 className="size-4 animate-spin" /> : null}
      {children}
    </button>
  )
}

export function IconButton({
  label,
  children,
  tono = 'neutral',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  label: string
  children: ReactNode
  tono?: 'neutral' | 'danger'
}) {
  const color =
    tono === 'danger'
      ? 'text-muted hover:bg-red-50 hover:text-red-700'
      : 'text-muted hover:bg-brand-50 hover:text-brand-700'
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`inline-flex size-8 items-center justify-center rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-brand-100 ${color}`}
      {...props}
    >
      {children}
    </button>
  )
}
