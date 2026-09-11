import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, CheckCircle2, Inbox, Info, Package, Sprout } from 'lucide-react'
import type { TipoConsulta } from '../types/api'

const tonos = {
  neutral: 'bg-slate-100 text-muted',
  info: 'bg-brand-50 text-brand-700',
  warning: 'bg-amber-50 text-amber-700',
  success: 'bg-emerald-50 text-emerald-700',
  danger: 'bg-red-50 text-red-700',
} as const

export function Pill({
  tono = 'neutral',
  icono,
  children,
}: {
  tono?: keyof typeof tonos
  icono?: ReactNode
  children: ReactNode
}) {
  return (
    <span
      className={`inline-flex w-fit items-center gap-1 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold ${tonos[tono]}`}
    >
      {icono}
      {children}
    </span>
  )
}

export function TipoBadge({ tipo }: { tipo: TipoConsulta | null }) {
  if (!tipo) return <Pill>Sin tipo</Pill>
  return tipo === 'Campo' ? (
    <Pill tono="info" icono={<Sprout className="size-3.5" />}>
      Campo
    </Pill>
  ) : (
    <Pill tono="warning" icono={<Package className="size-3.5" />}>
      Packing
    </Pill>
  )
}

export function Alert({ mensaje }: { mensaje: string }) {
  return (
    <div
      role="alert"
      className="flex items-start gap-2.5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
    >
      <AlertTriangle className="mt-0.5 size-4 shrink-0" />
      <span>{mensaje}</span>
    </div>
  )
}

export function Notice({ tono = 'info', children }: { tono?: 'info' | 'success'; children: ReactNode }) {
  const estilo =
    tono === 'success'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
      : 'border-brand-100 bg-brand-50 text-brand-800'
  const Icono = tono === 'success' ? CheckCircle2 : Info
  return (
    <div role="status" className={`flex items-start gap-2.5 rounded-lg border px-4 py-3 text-sm ${estilo}`}>
      <Icono className="mt-0.5 size-4 shrink-0" />
      <span>{children}</span>
    </div>
  )
}

export function EmptyState({ titulo, detalle, accion }: { titulo: string; detalle: string; accion?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-3 px-6 py-14 text-center">
      <div className="flex size-11 items-center justify-center rounded-full bg-brand-50 text-brand-600">
        <Inbox className="size-5" />
      </div>
      <div>
        <p className="font-display font-semibold text-ink">{titulo}</p>
        <p className="mt-1 text-sm text-muted">{detalle}</p>
      </div>
      {accion}
    </div>
  )
}

export function RegistroNoDisponible({ volverA, texto }: { volverA: string; texto: string }) {
  return (
    <div className="rounded-xl border border-line bg-white shadow-soft">
      <EmptyState
        titulo="Registro no disponible"
        detalle="Este registro no existe o fue eliminado."
        accion={
          <Link to={volverA} className="text-sm font-semibold text-brand-700 hover:text-brand-800">
            {texto}
          </Link>
        }
      />
    </div>
  )
}
