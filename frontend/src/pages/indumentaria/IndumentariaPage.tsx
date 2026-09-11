import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { FileDown, Pencil, Plus, Trash2 } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { Page } from '../../components/AppShell'
import { Button, IconButton } from '../../components/Button'
import { Alert, TipoBadge } from '../../components/Feedback'
import { BarraFiltros } from '../../components/Filtros'
import { DosLineas } from '../../components/Surface'
import { TablaRegistros, type Columna } from '../../components/TablaRegistros'
import { useCatalogos } from '../../hooks/useCatalogos'
import { aQueryExportar, contarFiltrosActivos, filtrosVacios, useListado, type Filtros } from '../../hooks/useListado'
import { formatFecha } from '../../lib/fechas'
import { tipoVisible } from '../../lib/tipoConsulta'
import { api } from '../../services/apiClient'
import type { Indumentaria } from '../../types/api'

export function IndumentariaPage() {
  const { esAdmin } = useAuth()
  const catalogos = useCatalogos()
  const { nombre } = catalogos
  const navigate = useNavigate()
  const location = useLocation()
  const [filtros, setFiltros] = useState<Filtros>(() => ({
    ...filtrosVacios,
    ...(location.state as { filtros?: Partial<Filtros> } | null)?.filtros,
  }))
  const listado = useListado<Indumentaria>('/indumentaria', filtros)
  const [ocultas, setOcultas] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [exportando, setExportando] = useState(false)

  const exportar = async () => {
    setError(null)
    setExportando(true)
    try {
      await api.descargar(`/indumentaria/exportar?${aQueryExportar(filtros)}`, 'indumentaria.xlsx')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo exportar a Excel')
    } finally {
      setExportando(false)
    }
  }

  const eliminar = async (fila: Indumentaria) => {
    if (!window.confirm('¿Eliminar esta entrega?')) return
    setError(null)
    try {
      await api.delete(`/indumentaria/${fila.ID}`)
      setOcultas((prev) => new Set(prev).add(fila.ID))
      listado.recargar()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar')
    }
  }

  const columnas: Columna<Indumentaria>[] = [
    {
      titulo: 'Fecha / Tipo',
      className: 'whitespace-nowrap',
      celda: (f) => (
        <div className="space-y-1">
          <p>{formatFecha(f.FECHA_ENTREGA)}</p>
          <TipoBadge tipo={tipoVisible(nombre.division[f.ID_DIVISION], f.TIPO_CONSULTA)} />
        </div>
      ),
    },
    {
      titulo: 'Trabajador',
      celda: (f) => <DosLineas principal={f.APELLIDOS_NOMBRES} secundario={`DNI ${f.DNI_TRABAJADOR}`} />,
    },
    { titulo: 'Ítem', celda: (f) => <span className="font-medium text-ink">{f.TIPO}</span> },
    { titulo: 'Cant.', className: 'text-right tabular-nums', celda: (f) => f.CANTIDAD },
    {
      titulo: 'Empresa / Fundo',
      className: 'hidden xl:table-cell',
      celda: (f) => <DosLineas principal={nombre.empresa[f.ID_EMPRESA] ?? '—'} secundario={nombre.fundo[f.ID_FUNDO]} />,
    },
    {
      titulo: 'Registró',
      className: 'hidden text-muted 2xl:table-cell',
      celda: (f) => (
        <span className="block max-w-40 truncate" title={f.RESPONSABLE_REGISTRO}>
          {f.RESPONSABLE_REGISTRO}
        </span>
      ),
    },
  ]

  const hayFiltros = contarFiltrosActivos(filtros) > 0

  return (
    <Page
      titulo="Indumentaria"
      descripcion="Entregas de EPP o uniforme a trabajadores."
      accion={
        <>
          <Button variant="secondary" onClick={() => void exportar()} loading={exportando}>
            <FileDown className="size-4" />
            Exportar a Excel
          </Button>
          <Link to="/indumentaria/nueva">
            <Button>
              <Plus className="size-4" />
              Nueva entrega
            </Button>
          </Link>
        </>
      }
    >
      <div className="space-y-4">
        <BarraFiltros
          value={filtros}
          onChange={setFiltros}
          empresas={catalogos.empresas}
          fundos={catalogos.fundos}
          conDni
        />
        {error ? <Alert mensaje={error} /> : null}
        <TablaRegistros
          listado={{ ...listado, filas: listado.filas.filter((f) => !ocultas.has(f.ID)) }}
          columnas={columnas}
          onAbrir={(f) => navigate(`/indumentaria/${f.ID}`)}
          vacio={
            hayFiltros
              ? { titulo: 'Sin resultados', detalle: 'Ninguna entrega coincide con los filtros aplicados.' }
              : { titulo: 'Sin entregas', detalle: 'Registre la primera entrega con “Nueva entrega”.' }
          }
          tarjeta={(f) => (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <TipoBadge tipo={tipoVisible(nombre.division[f.ID_DIVISION], f.TIPO_CONSULTA)} />
                <span className="text-xs text-muted">{formatFecha(f.FECHA_ENTREGA)}</span>
              </div>
              <p className="truncate text-sm font-semibold text-ink">
                {f.TIPO} <span className="font-normal text-muted">× {f.CANTIDAD}</span>
              </p>
              <p className="truncate text-xs text-muted">
                {f.APELLIDOS_NOMBRES} · DNI {f.DNI_TRABAJADOR}
              </p>
            </div>
          )}
          acciones={(f) => (
            <>
              <IconButton label="Editar" onClick={() => navigate(`/indumentaria/${f.ID}`)}>
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
