import type { ReactNode } from 'react'
import { Alert, EmptyState } from './Feedback'
import { Paginacion } from './Surface'
import { TAMANOS_PAGINA } from '../hooks/useListado'

export interface Columna<T> {
  titulo: string
  celda: (fila: T) => ReactNode
  /** Clases para th y td, p. ej. 'hidden xl:table-cell' para ocultar en pantallas medianas. */
  className?: string
}

interface ListadoPaginado<T> {
  filas: T[]
  total: number
  pagina: number
  paginas: number
  tamano: number
  cargando: boolean
  error: string | null
  setPagina: (pagina: number) => void
  setTamano: (tamano: number) => void
}

export function TablaRegistros<T extends { ID: number }>({
  listado,
  columnas,
  tarjeta,
  acciones,
  onAbrir,
  vacio,
}: {
  listado: ListadoPaginado<T>
  columnas: Columna<T>[]
  tarjeta: (fila: T) => ReactNode
  acciones: (fila: T) => ReactNode
  onAbrir: (fila: T) => void
  vacio: { titulo: string; detalle: string }
}) {
  const { filas, cargando } = listado
  const primeraCarga = cargando && !filas.length

  return (
    <div className="space-y-3">
      {listado.error ? <Alert mensaje={listado.error} /> : null}
      <div className="overflow-hidden rounded-xl border border-line bg-white shadow-soft">
        {primeraCarga ? (
          <div className="space-y-3 p-5" aria-busy="true" aria-label="Cargando">
            {Array.from({ length: 4 }, (_, i) => (
              <div key={i} className="h-10 animate-pulse rounded-lg bg-sand" />
            ))}
          </div>
        ) : !filas.length ? (
          <EmptyState titulo={vacio.titulo} detalle={vacio.detalle} />
        ) : (
          <>
            <div className={`transition-opacity ${cargando ? 'opacity-50' : ''}`} aria-busy={cargando}>
              <div className="hidden overflow-x-auto md:block">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr>
                      {columnas.map((columna) => (
                        <th
                          key={columna.titulo}
                          scope="col"
                          className={`whitespace-nowrap border-b border-line px-4 py-3 text-[11.5px] font-semibold uppercase tracking-wide text-muted first:pl-5 ${columna.className ?? ''}`}
                        >
                          {columna.titulo}
                        </th>
                      ))}
                      <th scope="col" className="border-b border-line py-3 pr-5">
                        <span className="sr-only">Acciones</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filas.map((fila) => (
                      <tr
                        key={fila.ID}
                        onClick={() => onAbrir(fila)}
                        className="cursor-pointer border-b border-line last:border-0 hover:bg-sand"
                      >
                        {columnas.map((columna) => (
                          <td
                            key={columna.titulo}
                            className={`px-4 py-3.5 align-middle text-ink-soft first:pl-5 ${columna.className ?? ''}`}
                          >
                            {columna.celda(fila)}
                          </td>
                        ))}
                        <td className="py-3.5 pr-5 text-right" onClick={(e) => e.stopPropagation()}>
                          <div className="flex justify-end gap-1">{acciones(fila)}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <ul className="divide-y divide-line md:hidden">
                {filas.map((fila) => (
                  <li key={fila.ID} className="flex items-start gap-2 px-4 py-3.5">
                    <button type="button" onClick={() => onAbrir(fila)} className="min-w-0 flex-1 text-left">
                      {tarjeta(fila)}
                    </button>
                    <div className="flex shrink-0 gap-0.5">{acciones(fila)}</div>
                  </li>
                ))}
              </ul>
            </div>
            <Paginacion
              pagina={listado.pagina}
              paginas={listado.paginas}
              tamano={listado.tamano}
              total={listado.total}
              cantidadEnPagina={filas.length}
              opcionesTamano={TAMANOS_PAGINA}
              onPagina={listado.setPagina}
              onTamano={listado.setTamano}
            />
          </>
        )}
      </div>
    </div>
  )
}
