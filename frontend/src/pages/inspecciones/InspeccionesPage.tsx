import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle2, CircleDashed, FileDown, Pencil, Plus, Trash2 } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { Page } from '../../components/AppShell'
import { Button, IconButton } from '../../components/Button'
import { Alert, Pill, TipoBadge } from '../../components/Feedback'
import { BarraFiltros } from '../../components/Filtros'
import { DosLineas } from '../../components/Surface'
import { TablaRegistros, type Columna } from '../../components/TablaRegistros'
import { useCatalogos } from '../../hooks/useCatalogos'
import { aQueryExportar, contarFiltrosActivos, filtrosVacios, useListado, type Filtros } from '../../hooks/useListado'
import { formatFecha } from '../../lib/fechas'
import { tipoVisible } from '../../lib/tipoConsulta'
import { api } from '../../services/apiClient'
import type { Inspeccion } from '../../types/api'

function EstadoAccion({ fila }: { fila: Inspeccion }) {
  return fila.ACCION_CORRECTIVA?.trim() ? (
    <Pill tono="success" icono={<CheckCircle2 className="size-3.5" />}>
      Acción definida
    </Pill>
  ) : (
    <Pill tono="warning" icono={<CircleDashed className="size-3.5" />}>
      Sin acción
    </Pill>
  )
}

export function InspeccionesPage() {
  const { esAdmin } = useAuth()
  const catalogos = useCatalogos()
  const { nombre } = catalogos
  const navigate = useNavigate()
  const location = useLocation()
  const [filtros, setFiltros] = useState<Filtros>(() => ({
    ...filtrosVacios,
    ...(location.state as { filtros?: Partial<Filtros> } | null)?.filtros,
  }))
  const listado = useListado<Inspeccion>('/inspecciones', filtros)
  const [ocultas, setOcultas] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [exportando, setExportando] = useState(false)

  const exportar = async () => {
    setError(null)
    setExportando(true)
    try {
      await api.descargar(`/inspecciones/exportar?${aQueryExportar(filtros)}`, 'inspecciones.xlsx')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo exportar a Excel')
    } finally {
      setExportando(false)
    }
  }

  const eliminar = async (fila: Inspeccion) => {
    if (!window.confirm('¿Eliminar esta inspección?')) return
    setError(null)
    try {
      await api.delete(`/inspecciones/${fila.ID}`)
      setOcultas((prev) => new Set(prev).add(fila.ID))
      listado.recargar()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar')
    }
  }

  const columnas: Columna<Inspeccion>[] = [
    {
      titulo: 'Fecha / Tipo',
      className: 'whitespace-nowrap',
      celda: (f) => (
        <div className="space-y-1">
          <p>{formatFecha(f.FECHA_OBSERVACION)}</p>
          <TipoBadge tipo={tipoVisible(nombre.division[f.ID_DIVISION], f.TIPO_CONSULTA)} />
        </div>
      ),
    },
    {
      titulo: 'Empresa / Fundo',
      celda: (f) => (
        <DosLineas principal={nombre.empresa[f.ID_EMPRESA] ?? '—'} secundario={nombre.fundo[f.ID_FUNDO]} />
      ),
    },
    {
      titulo: 'División / Área',
      className: 'hidden 2xl:table-cell',
      celda: (f) => <DosLineas principal={nombre.division[f.ID_DIVISION] ?? '—'} secundario={nombre.area[f.ID_AREA]} />,
    },
    {
      titulo: 'Categoría',
      celda: (f) => (
        <DosLineas principal={nombre.categoria[f.ID_CATEGORIA] ?? '—'} secundario={nombre.subcategoria[f.ID_SUBCATEGORIA]} />
      ),
    },
    { titulo: 'Seguimiento', className: 'hidden xl:table-cell', celda: (f) => <EstadoAccion fila={f} /> },
  ]

  const hayFiltros = contarFiltrosActivos(filtros) > 0

  return (
    <Page
      titulo="Inspecciones"
      descripcion="Observaciones de Campo o Packing, con evidencia fotográfica."
      accion={
        <>
          <Button variant="secondary" onClick={() => void exportar()} loading={exportando}>
            <FileDown className="size-4" />
            Exportar a Excel
          </Button>
          <Link to="/inspecciones/nueva">
            <Button>
              <Plus className="size-4" />
              Nueva inspección
            </Button>
          </Link>
        </>
      }
    >
      <div className="space-y-4">
        <BarraFiltros value={filtros} onChange={setFiltros} empresas={catalogos.empresas} fundos={catalogos.fundos} />
        {error ? <Alert mensaje={error} /> : null}
        <TablaRegistros
          listado={{ ...listado, filas: listado.filas.filter((f) => !ocultas.has(f.ID)) }}
          columnas={columnas}
          onAbrir={(f) => navigate(`/inspecciones/${f.ID}`)}
          vacio={
            hayFiltros
              ? { titulo: 'Sin resultados', detalle: 'Ninguna inspección coincide con los filtros aplicados.' }
              : { titulo: 'Sin inspecciones', detalle: 'Todavía no hay registros. Cree el primero con “Nueva inspección”.' }
          }
          tarjeta={(f) => (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <TipoBadge tipo={tipoVisible(nombre.division[f.ID_DIVISION], f.TIPO_CONSULTA)} />
                <span className="text-xs text-muted">{formatFecha(f.FECHA_OBSERVACION)}</span>
              </div>
              <p className="truncate text-sm font-semibold text-ink">
                {nombre.fundo[f.ID_FUNDO] ?? '—'}
                <span className="font-normal text-muted"> · {nombre.area[f.ID_AREA] ?? '—'}</span>
              </p>
              <p className="truncate text-xs text-muted">
                {nombre.categoria[f.ID_CATEGORIA] ?? '—'} · {nombre.subcategoria[f.ID_SUBCATEGORIA] ?? '—'}
              </p>
              <EstadoAccion fila={f} />
            </div>
          )}
          acciones={(f) => (
            <>
              <IconButton label="Editar" onClick={() => navigate(`/inspecciones/${f.ID}`)}>
                <Pencil className="size-4" />
              </IconButton>
              {esAdmin ? (
                <IconButton label="Eliminar" tono="danger" onClick={() => void eliminar(f)}>
                  <Trash2 className="size-4" />
                </IconButton>
              ) : null}
            </>
          )}
        />
      </div>
    </Page>
  )
}
