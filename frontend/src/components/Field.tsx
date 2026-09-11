import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes, ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'

const control =
  'w-full rounded-lg border border-line bg-white px-3.5 text-sm text-ink outline-none transition-[border-color,box-shadow] placeholder:text-muted/60 focus:border-brand-500 focus:ring-4 focus:ring-brand-100 disabled:bg-sand disabled:text-muted'

interface FieldProps {
  label: string
  children: ReactNode
  hint?: ReactNode
  className?: string
}

export function Field({ label, children, hint, className = '' }: FieldProps) {
  return (
    <label className={`block space-y-1.5 ${className}`}>
      <span className="text-[13px] font-semibold text-ink-soft">{label}</span>
      {children}
      {hint ? <span className="block text-xs text-muted">{hint}</span> : null}
    </label>
  )
}

export function Input({ className = '', ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`${control} h-10 ${className}`} {...props} />
}

export function Select({ className = '', ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <div className="relative">
      <select className={`${control} h-10 appearance-none pr-9 ${className}`} {...props} />
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
    </div>
  )
}

export function Textarea({ className = '', ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={`${control} min-h-24 resize-y py-2.5 leading-relaxed ${className}`} {...props} />
}

export function SegmentedControl<T extends string>({
  opciones,
  value,
  onChange,
  etiqueta,
  disabled,
}: {
  opciones: { valor: T; texto: string }[]
  value: T
  onChange: (valor: T) => void
  etiqueta: string
  disabled?: boolean
}) {
  return (
    <div
      role="radiogroup"
      aria-label={etiqueta}
      className="flex h-10 rounded-lg border border-line bg-white p-1"
    >
      {opciones.map((opcion) => {
        const activo = opcion.valor === value
        return (
          <button
            key={opcion.valor}
            type="button"
            role="radio"
            aria-checked={activo}
            disabled={disabled}
            onClick={() => onChange(opcion.valor)}
            className={`min-w-0 flex-1 truncate rounded-md px-3 text-[13px] font-semibold transition-colors disabled:cursor-not-allowed ${
              activo ? 'bg-brand-700 text-white shadow-soft' : 'text-muted hover:text-ink'
            }`}
          >
            {opcion.texto}
          </button>
        )
      })}
    </div>
  )
}
