import type { ReactNode } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export function Card({
  titulo,
  descripcion,
  accion,
  children,
  className = '',
  sinPadding = false,
}: {
  titulo?: string
  descripcion?: string
  accion?: ReactNode
  children: ReactNode
  className?: string
  sinPadding?: boolean
}) {
  return (
    <section className={`rounded-xl border border-line bg-white shadow-soft ${className}`}>
      {titulo ? (
        <div
          className={`flex flex-wrap items-start justify-between gap-3 ${sinPadding ? 'border-b border-line px-5 py-4' : 'px-5 pt-5 sm:px-6'}`}
        >
          <div>
            <h2 className="font-display text-[15px] font-bold text-ink">{titulo}</h2>
            {descripcion ? <p className="mt-0.5 text-[13px] text-muted">{descripcion}</p> : null}
          </div>
          {accion}
        </div>
      ) : null}
      <div className={sinPadding ? '' : `px-5 pb-5 sm:px-6 ${titulo ? 'pt-4' : 'pt-5'}`}>{children}</div>
    </section>
  )
}

export function FormFooter({ children }: { children: ReactNode }) {
  return (
    <div className="sticky bottom-0 z-10 -mx-4 mt-6 border-t border-line bg-white/95 px-4 py-3 backdrop-blur sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
      <div className="flex flex-wrap items-center justify-end gap-3">{children}</div>
    </div>
  )
}

export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">{children}</table>
    </div>
  )
}

export function Th({ children, className = '' }: { children?: ReactNode; className?: string }) {
  return (
    <th
      scope="col"
      className={`whitespace-nowrap border-b border-line px-3 py-3 text-[11.5px] font-semibold uppercase tracking-wide text-muted first:pl-4 last:pr-4 sm:px-4 sm:first:pl-5 sm:last:pr-5 ${className}`}
    >
      {children}
    </th>
  )
}

export function Td({ children, className = '' }: { children?: ReactNode; className?: string }) {
  return (
    <td
      className={`px-3 py-3.5 align-middle text-ink-soft first:pl-4 last:pr-4 sm:px-4 sm:first:pl-5 sm:last:pr-5 ${className}`}
    >
      {children}
    </td>
  )
}

export function DosLineas({ principal, secundario }: { principal: ReactNode; secundario?: ReactNode }) {
  return (
    // En una tabla el ancho máximo debe ir en el contenido: en la celda no trunca.
    <div className="min-w-0 max-w-48">
      <p className="truncate font-semibold text-ink" title={typeof principal === 'string' ? principal : undefined}>
        {principal}
      </p>
      {secundario ? (
        <p className="truncate text-xs text-muted" title={typeof secundario === 'string' ? secundario : undefined}>
          {secundario}
        </p>
      ) : null}
    </div>
  )
}

function numerosDePagina(actual: number, total: number): (number | '…')[] {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i)
  const visibles = new Set([0, total - 1, actual - 1, actual, actual + 1].filter((n) => n >= 0 && n < total))
  const ordenadas = [...visibles].sort((a, b) => a - b)
  const resultado: (number | '…')[] = []
  ordenadas.forEach((n, i) => {
    if (i > 0 && n - ordenadas[i - 1] > 1) resultado.push('…')
    resultado.push(n)
  })
  return resultado
}

export function Paginacion({
  pagina,
  paginas,
  tamano,
  total,
  cantidadEnPagina,
  opcionesTamano,
  onPagina,
  onTamano,
}: {
  pagina: number
  paginas: number
  tamano: number
  total: number
  cantidadEnPagina: number
  opcionesTamano: readonly number[]
  onPagina: (pagina: number) => void
  onTamano: (tamano: number) => void
}) {
  const desde = total === 0 ? 0 : pagina * tamano + 1
  const hasta = pagina * tamano + cantidadEnPagina
  const boton =
    'inline-flex size-8 items-center justify-center rounded-lg border border-line text-ink-soft transition-colors hover:border-brand-300 hover:text-brand-700 disabled:pointer-events-none disabled:opacity-40'

  return (
    <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3 border-t border-line px-4 py-3 sm:px-5">
      <div className="flex items-center gap-3 text-[13px] text-muted">
        <span>
          {desde}–{hasta} de <span className="font-semibold text-ink-soft">{total}</span>
        </span>
        <label className="flex items-center gap-2">
          <span className="hidden sm:inline">Filas por página</span>
          <select
            value={tamano}
            onChange={(e) => onTamano(Number(e.target.value))}
            aria-label="Filas por página"
            className="h-8 rounded-lg border border-line bg-white px-2 text-[13px] font-semibold text-ink-soft outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
          >
            {opcionesTamano.map((opcion) => (
              <option key={opcion} value={opcion}>
                {opcion}
              </option>
            ))}
          </select>
        </label>
      </div>

      {paginas > 1 ? (
        <nav className="flex items-center gap-1" aria-label="Paginación">
          <button type="button" className={boton} disabled={pagina === 0} onClick={() => onPagina(pagina - 1)} aria-label="Página anterior">
            <ChevronLeft className="size-4" />
          </button>
          <span className="px-2 text-[13px] text-muted sm:hidden">
            Página <span className="font-semibold text-ink">{pagina + 1}</span> de {paginas}
          </span>
          <div className="hidden items-center gap-1 sm:flex">
            {numerosDePagina(pagina, paginas).map((n, i) =>
              n === '…' ? (
                <span key={`e${i}`} className="w-6 text-center text-[13px] text-muted">
                  …
                </span>
              ) : (
                <button
                  key={n}
                  type="button"
                  onClick={() => onPagina(n)}
                  aria-current={n === pagina ? 'page' : undefined}
                  className={`inline-flex h-8 min-w-8 items-center justify-center rounded-lg px-2 text-[13px] font-semibold transition-colors ${
                    n === pagina ? 'bg-brand-700 text-white' : 'text-ink-soft hover:bg-brand-50 hover:text-brand-700'
                  }`}
                >
                  {n + 1}
                </button>
              ),
            )}
          </div>
          <button
            type="button"
            className={boton}
            disabled={pagina >= paginas - 1}
            onClick={() => onPagina(pagina + 1)}
            aria-label="Página siguiente"
          >
            <ChevronRight className="size-4" />
          </button>
        </nav>
      ) : null}
    </div>
  )
}
