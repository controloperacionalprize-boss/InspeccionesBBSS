import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle2, Clock, FileDown, Pencil, Plus, Trash2 } from 'lucide-react'
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
import { api } from '../../services/apiClient'
import type { Consulta } from '../../types/api'

function Seguimiento({ fila }: { fila: Consulta }) {
  return fila.RESPUESTA_POSTERIOR?.trim() ? (
    <Pill tono="success" icono={<CheckCircle2 className="size-3.5" />}>
      Respondida
    </Pill>
  ) : (
    <Pill tono="warning" icono={<Clock className="size-3.5" />}>
      Por responder
    </Pill>
  )
}

export function ConsultasPage() {
  const { esAdmin } = useAuth()
  const catalogos = useCatalogos()
  const { nombre } = catalogos
  const navigate = useNavigate()
  const location = useLocation()
  const [filtros, setFiltros] = useState<Filtros>(() => ({
    ...filtrosVacios,
    ...(location.state as { filtros?: Partial<Filtros> } | null)?.filtros,
  }))
  const listado = useListado<Consulta>('/consultas', filtros)
  const [ocultas, setOcultas] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [exportando, setExportando] = useState(false)

  const exportar = async () => {
    setError(null)
    setExportando(true)
    try {
      await api.descargar(`/consultas/exportar?${aQueryExportar(filtros)}`, 'consultas.xlsx')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo exportar a Excel')
    } finally {
      setExportando(false)
    }
  }

  const eliminar = async (fila: Consulta) => {
    if (!window.confirm('¿Eliminar esta consulta?')) return
    setError(null)
    try {
      await api.delete(`/consultas/${fila.ID}`)
      setOcultas((prev) => new Set(prev).add(fila.ID))
      listado.recargar()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar')
    }
  }

  const columnas: Columna<Consulta>[] = [
    {
      titulo: 'Fecha / Tipo',
      className: 'whitespace-nowrap',
      celda: (f) => (
        <div className="space-y-1">
          <p>{formatFecha(f.FECHA_CONSULTA)}</p>
          <TipoBadge tipo={f.TIPO_CONSULTA} />
        </div>
      ),
    },
    {
      titulo: 'Trabajador',
      celda: (f) => <DosLineas principal={f.APELLIDOS_NOMBRES} secundario={`DNI ${f.DNI_TRABAJADOR}`} />,
    },
    {
      titulo: 'Empresa / Fundo',
      className: 'hidden 2xl:table-cell',
      celda: (f) => <DosLineas principal={nombre.empresa[f.ID_EMPRESA] ?? '—'} secundario={nombre.fundo[f.ID_FUNDO]} />,
    },
    {
      titulo: 'Área responsable',
      className: 'hidden xl:table-cell',
      celda: (f) => (
        <span className="block max-w-44 truncate" title={f.AREA_RESPONSABLE}>
          {f.AREA_RESPONSABLE}
        </span>
      ),
    },
    { titulo: 'Seguimiento', celda: (f) => <Seguimiento fila={f} /> },
  ]

  const hayFiltros = contarFiltrosActivos(filtros) > 0

  return (
    <Page
      titulo="Consultas"
      descripcion="Consultas de trabajadores: respuesta inmediata en campo y seguimiento desde la web."
      accion={
        <>
          <Button variant="secondary" onClick={() => void exportar()} loading={exportando}>
            <FileDown className="size-4" />
            Exportar a Excel
          </Button>
          <Link to="/consultas/nueva">
            <Button>
              <Plus className="size-4" />
              Nueva consulta
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
          onAbrir={(f) => navigate(`/consultas/${f.ID}`)}
          vacio={
            hayFiltros
              ? { titulo: 'Sin resultados', detalle: 'Ninguna consulta coincide con los filtros aplicados.' }
              : { titulo: 'Sin consultas', detalle: 'Registre la primera consulta con “Nueva consulta”.' }
          }
          tarjeta={(f) => (
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <TipoBadge tipo={f.TIPO_CONSULTA} />
                <span className="text-xs text-muted">{formatFecha(f.FECHA_CONSULTA)}</span>
              </div>
              <p className="truncate text-sm font-semibold text-ink">{f.APELLIDOS_NOMBRES}</p>
              <p className="truncate text-xs text-muted">
                DNI {f.DNI_TRABAJADOR} · {f.AREA_RESPONSABLE}
              </p>
              <Seguimiento fila={f} />
            </div>
          )}
          acciones={(f) => (
            <>
              <IconButton label="Responder o editar" onClick={() => navigate(`/consultas/${f.ID}`)}>
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
