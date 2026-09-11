import { useEffect, useState, type ComponentType } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertTriangle, ArrowRight, ClipboardList, MessageSquareText, Plus, Shirt } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { Page } from '../components/AppShell'
import { Button } from '../components/Button'
import { Alert, EmptyState, TipoBadge } from '../components/Feedback'
import { Card, DosLineas, Table, Td, Th } from '../components/Surface'
import { useCatalogos } from '../hooks/useCatalogos'
import { formatFecha, inicioMesIso } from '../lib/fechas'
import { tipoVisible } from '../lib/tipoConsulta'
import { cacheado, invalidar, leerCache } from '../lib/cache'
import { onTiempoReal } from '../lib/tiempoReal'
import { api } from '../services/apiClient'
import type { Inspeccion, Resumen } from '../types/api'

// Conteos del inicio: una respuesta chica calculada en SQL, cacheada 1 min e invalidada al guardar.
const TTL_RESUMEN = 60_000

function Kpi({
  etiqueta,
  valor,
  detalle,
  icono: Icono,
  tono,
  to,
  delMes = false,
}: {
  etiqueta: string
  valor: number | null
  detalle: string
  icono: ComponentType<{ className?: string }>
  tono: 'brand' | 'amber'
  to: string
  delMes?: boolean
}) {
  const fondo = tono === 'amber' ? 'bg-amber-50 text-amber-700' : 'bg-brand-50 text-brand-700'
  return (
    <Link
      to={to}
      state={delMes ? { filtros: { fecha_desde: inicioMesIso() } } : undefined}
      className="group rounded-xl border border-line bg-white p-5 shadow-soft transition-colors hover:border-brand-300"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-[13px] font-semibold text-muted">{etiqueta}</span>
        <span className={`flex size-8 items-center justify-center rounded-lg ${fondo}`}>
          <Icono className="size-4" />
        </span>
      </div>
      <p className="mt-2 font-display text-3xl font-extrabold tracking-tight text-ink">{valor ?? '—'}</p>
      <p className="mt-1 text-[13px] text-muted group-hover:text-brand-700">{detalle}</p>
    </Link>
  )
}

const segmentos = [
  { clave: 'campo', etiqueta: 'Campo', color: 'var(--color-campo)' },
  { clave: 'packing', etiqueta: 'Packing', color: 'var(--color-packing)' },
  { clave: 'sin_tipo', etiqueta: 'Sin tipo', color: '#cbd5e1' },
] as const

function DistribucionTipo({ porTipo }: { porTipo: Resumen['inspecciones_por_tipo'] }) {
  const [activo, setActivo] = useState<number | null>(null)
  const datos = segmentos.map((s) => ({ ...s, valor: porTipo[s.clave] })).filter((s) => s.valor > 0)
  const total = datos.reduce((suma, d) => suma + d.valor, 0)

  if (!total) {
    return <p className="py-8 text-center text-sm text-muted">Aún no hay inspecciones este mes.</p>
  }

  const pct = (valor: number) => Math.round((valor / total) * 100)

  return (
    <div>
      <div className="relative">
        <div
          className="flex h-4 gap-0.5 overflow-hidden rounded"
          role="img"
          aria-label={datos.map((d) => `${d.etiqueta}: ${d.valor}`).join(', ')}
        >
          {datos.map((d, i) => (
            <div
              key={d.etiqueta}
              onMouseEnter={() => setActivo(i)}
              onMouseLeave={() => setActivo(null)}
              className="h-full transition-opacity"
              style={{
                width: `${(d.valor / total) * 100}%`,
                background: d.color,
                opacity: activo === null || activo === i ? 1 : 0.45,
              }}
            />
          ))}
        </div>
        {activo !== null ? (
          <div className="pointer-events-none absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md bg-ink px-2.5 py-1 text-xs font-medium text-white shadow-lift">
            {datos[activo].etiqueta} · {datos[activo].valor} ({pct(datos[activo].valor)}%)
          </div>
        ) : null}
      </div>
      <ul className="mt-5 space-y-3">
        {datos.map((d, i) => (
          <li
            key={d.etiqueta}
            className="flex items-center justify-between text-[13px]"
            onMouseEnter={() => setActivo(i)}
            onMouseLeave={() => setActivo(null)}
          >
            <span className="flex items-center gap-2 text-ink-soft">
              <span className="size-2.5 rounded-full" style={{ background: d.color }} />
              {d.etiqueta}
            </span>
            <span className="font-semibold text-ink">
              {d.valor} <span className="font-normal text-muted">· {pct(d.valor)}%</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function HomePage() {
  const { usuario } = useAuth()
  const { nombre } = useCatalogos()
  const navigate = useNavigate()
  const desde = inicioMesIso()
  const claveResumen = `resumen:${desde}`
  const [resumen, setResumen] = useState<Resumen | undefined>(() => leerCache<Resumen>(claveResumen))
  const [recientes, setRecientes] = useState<Inspeccion[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)

  useEffect(
    () =>
      onTiempoReal((recurso) => {
        if (recurso === 'inspecciones' || recurso === 'consultas' || recurso === 'indumentaria') {
          invalidar(claveResumen)
          setTick((n) => n + 1)
        }
      }),
    [claveResumen],
  )

  useEffect(() => {
    const control = new AbortController()
    cacheado(claveResumen, TTL_RESUMEN, () => api.get<Resumen>(`/resumen?desde=${desde}`))
      .then(setResumen)
      .catch((err: Error) => setError(err.message))
    api
      .get<Inspeccion[]>('/inspecciones?limit=5', control.signal)
      .then(setRecientes)
      .catch((err: Error) => err.name !== 'AbortError' && setError(err.message))
    return () => control.abort()
  }, [claveResumen, desde, tick])

  const mes = new Intl.DateTimeFormat('es-PE', { month: 'long', year: 'numeric' }).format(new Date())
  const unidades = resumen?.unidades_entregadas ?? 0

  return (
    <Page
      titulo={`Hola, ${usuario?.nombre ?? ''}`}
      descripcion={`Resumen de ${mes} · Campo y Packing`}
      accion={
        <>
          <Link to="/consultas/nueva" className="hidden sm:block">
            <Button variant="secondary">Nueva consulta</Button>
          </Link>
          <Link to="/inspecciones/nueva">
            <Button>
              <Plus className="size-4" />
              Nueva inspección
            </Button>
          </Link>
        </>
      }
    >
      {error ? <Alert mensaje={error} /> : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Kpi
          etiqueta="Inspecciones del mes"
          valor={resumen?.inspecciones ?? null}
          detalle="Ver las del mes"
          icono={ClipboardList}
          tono="brand"
          to="/inspecciones"
          delMes
        />
        <Kpi
          etiqueta="Sin acción correctiva"
          valor={resumen?.inspecciones_sin_accion ?? null}
          detalle="Hallazgos del mes por atender"
          icono={AlertTriangle}
          tono="amber"
          to="/inspecciones"
          delMes
        />
        <Kpi
          etiqueta="Consultas por responder"
          valor={resumen?.consultas_por_responder ?? null}
          detalle="Sin respuesta posterior"
          icono={MessageSquareText}
          tono="brand"
          to="/consultas"
        />
        <Kpi
          etiqueta="Entregas del mes"
          valor={resumen?.entregas ?? null}
          detalle={`${unidades} ${unidades === 1 ? 'unidad entregada' : 'unidades entregadas'}`}
          icono={Shirt}
          tono="brand"
          to="/indumentaria"
          delMes
        />
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
        <Card
          titulo="Inspecciones recientes"
          sinPadding
          accion={
            <Link
              to="/inspecciones"
              className="inline-flex items-center gap-1 text-[13px] font-semibold text-brand-700 hover:text-brand-800"
            >
              Ver todas <ArrowRight className="size-3.5" />
            </Link>
          }
        >
          {recientes && !recientes.length ? (
            <EmptyState titulo="Sin inspecciones" detalle="Registre la primera para verla aquí." />
          ) : (
            <Table>
              <thead>
                <tr>
                  <Th>Fundo / Área</Th>
                  <Th className="hidden sm:table-cell xl:hidden 2xl:table-cell">Categoría</Th>
                  <Th>Tipo</Th>
                  <Th>Fecha</Th>
                </tr>
              </thead>
              <tbody>
                {(recientes ?? []).map((fila) => (
                  <tr
                    key={fila.ID}
                    onClick={() => navigate(`/inspecciones/${fila.ID}`)}
                    className="cursor-pointer border-b border-line last:border-0 hover:bg-sand"
                  >
                    <Td>
                      <DosLineas
                        principal={nombre.fundo[fila.ID_FUNDO] ?? `Fundo ${fila.ID_FUNDO}`}
                        secundario={nombre.area[fila.ID_AREA]}
                      />
                    </Td>
                    <Td className="hidden sm:table-cell xl:hidden 2xl:table-cell">{nombre.categoria[fila.ID_CATEGORIA] ?? '—'}</Td>
                    <Td>
                      <TipoBadge tipo={tipoVisible(nombre.division[fila.ID_DIVISION], fila.TIPO_CONSULTA)} />
                    </Td>
                    <Td className="whitespace-nowrap text-muted">{formatFecha(fila.FECHA_OBSERVACION)}</Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card>

        <Card titulo="Inspecciones del mes por tipo" descripcion="Pase el cursor para ver el detalle.">
          {resumen ? (
            <DistribucionTipo porTipo={resumen.inspecciones_por_tipo} />
          ) : (
            <div className="h-24 animate-pulse rounded-lg bg-sand" />
          )}
        </Card>
      </div>
    </Page>
  )
}
