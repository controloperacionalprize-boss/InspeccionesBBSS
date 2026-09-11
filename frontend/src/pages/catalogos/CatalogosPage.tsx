import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { Check, ChevronRight, Pencil, Plus, Trash2, X } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { Page } from '../../components/AppShell'
import { IconButton } from '../../components/Button'
import { Alert, Notice } from '../../components/Feedback'
import { SegmentedControl } from '../../components/Field'
import { useCatalogos } from '../../hooks/useCatalogos'
import { api } from '../../services/apiClient'
import type { Area, CatalogoItem, Fundo, Subcategoria } from '../../types/api'

type Grupo = 'ubicacion' | 'organizacion' | 'clasificacion'

interface Nivel {
  titulo: string
  singular: string
  ruta: string
  maxLength: number
}

function idPadre(hijo: Fundo | Area | Subcategoria) {
  if ('ID_EMPRESA' in hijo) return hijo.ID_EMPRESA
  if ('ID_DIVISION' in hijo) return hijo.ID_DIVISION
  return hijo.ID_CATEGORIA
}

const grupos: Record<Grupo, { etiqueta: string; padre: Nivel; hijo: Nivel & { fk: string } }> = {
  ubicacion: {
    etiqueta: 'Empresas',
    padre: { titulo: 'Empresas', singular: 'empresa', ruta: '/empresas', maxLength: 30 },
    hijo: { titulo: 'Fundos', singular: 'fundo', ruta: '/fundos', maxLength: 50, fk: 'ID_EMPRESA' },
  },
  organizacion: {
    etiqueta: 'Divisiones',
    padre: { titulo: 'Divisiones', singular: 'división', ruta: '/divisiones', maxLength: 100 },
    hijo: { titulo: 'Áreas', singular: 'área', ruta: '/areas', maxLength: 100, fk: 'ID_DIVISION' },
  },
  clasificacion: {
    etiqueta: 'Categorías',
    padre: { titulo: 'Categorías', singular: 'categoría', ruta: '/categorias', maxLength: 150 },
    hijo: { titulo: 'Subcategorías', singular: 'subcategoría', ruta: '/subcategorias', maxLength: 150, fk: 'ID_CATEGORIA' },
  },
}

function ListaEditable({
  nivel,
  items,
  conteo,
  seleccionado,
  onSeleccionar,
  onGuardar,
  onEliminar,
  bloqueada,
  vacio,
}: {
  nivel: Nivel
  items: CatalogoItem[]
  conteo?: (id: number) => number
  seleccionado?: number | null
  onSeleccionar?: (id: number) => void
  onGuardar: (nombre: string, id?: number) => Promise<boolean>
  onEliminar: (item: CatalogoItem) => void
  bloqueada?: string
  vacio: string
}) {
  const [editando, setEditando] = useState<number | 'nuevo' | null>(null)
  const [texto, setTexto] = useState('')

  const abrir = (objetivo: number | 'nuevo', valor = '') => {
    setEditando(objetivo)
    setTexto(valor.toLocaleUpperCase('es'))
  }

  const guardar = async (evento: FormEvent) => {
    evento.preventDefault()
    const nombre = texto.trim().toLocaleUpperCase('es')
    if (!nombre) return
    const ok = await onGuardar(nombre, editando === 'nuevo' ? undefined : (editando ?? undefined))
    if (ok) setEditando(null)
  }

  const editor = (
    <form onSubmit={(e) => void guardar(e)} className="flex items-center gap-1.5 px-3 py-2">
      <input
        autoFocus
        maxLength={nivel.maxLength}
        value={texto}
        onChange={(e) => setTexto(e.target.value.toLocaleUpperCase('es'))}
        onKeyDown={(e) => e.key === 'Escape' && setEditando(null)}
        placeholder={`NOMBRE DE ${nivel.singular.toLocaleUpperCase('es')}`}
        aria-label={`Nombre de ${nivel.singular}`}
        className="h-9 min-w-0 flex-1 rounded-lg border border-brand-400 px-3 text-sm uppercase outline-none ring-4 ring-brand-100"
      />
      <IconButton label="Guardar" type="submit">
        <Check className="size-4" />
      </IconButton>
      <IconButton label="Cancelar" onClick={() => setEditando(null)}>
        <X className="size-4" />
      </IconButton>
    </form>
  )

  return (
    <section className="flex min-h-48 flex-col rounded-xl border border-line bg-white shadow-soft md:min-h-[22rem]">
      <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-3">
        <div>
          <h2 className="font-display text-[15px] font-bold text-ink">{nivel.titulo}</h2>
          <p className="text-xs text-muted">{items.length} registrados</p>
        </div>
        <button
          type="button"
          disabled={Boolean(bloqueada)}
          onClick={() => abrir('nuevo')}
          className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-brand-50 px-3 text-[13px] font-semibold text-brand-700 transition-colors hover:bg-brand-100 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Plus className="size-4" />
          Agregar
        </button>
      </div>

      {editando === 'nuevo' ? <div className="border-b border-line bg-brand-50/40">{editor}</div> : null}

      {bloqueada ? (
        <p className="m-auto max-w-56 px-4 text-center text-sm text-muted">{bloqueada}</p>
      ) : !items.length && editando !== 'nuevo' ? (
        <p className="m-auto max-w-56 px-4 text-center text-sm text-muted">{vacio}</p>
      ) : (
        <ul className="flex-1 divide-y divide-line overflow-y-auto">
          {items.map((item) =>
            editando === item.ID ? (
              <li key={item.ID} className="bg-brand-50/40">
                {editor}
              </li>
            ) : (
              <li
                key={item.ID}
                className={`group flex items-center gap-2 px-4 py-2.5 ${
                  seleccionado === item.ID ? 'bg-brand-50' : onSeleccionar ? 'hover:bg-sand' : ''
                }`}
              >
                <button
                  type="button"
                  disabled={!onSeleccionar}
                  onClick={() => onSeleccionar?.(item.ID)}
                  className="flex min-w-0 flex-1 items-center gap-2 text-left disabled:cursor-default"
                >
                  <span
                    className={`truncate text-sm ${seleccionado === item.ID ? 'font-semibold text-brand-800' : 'text-ink'}`}
                  >
                    {item.NOMBRE}
                  </span>
                  {conteo ? (
                    <span className="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-muted">
                      {conteo(item.ID)}
                    </span>
                  ) : null}
                </button>
                <div className="flex shrink-0 gap-0.5 opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100">
                  <IconButton label={`Renombrar ${nivel.singular}`} onClick={() => abrir(item.ID, item.NOMBRE)}>
                    <Pencil className="size-3.5" />
                  </IconButton>
                  <IconButton label={`Eliminar ${nivel.singular}`} tono="danger" onClick={() => onEliminar(item)}>
                    <Trash2 className="size-3.5" />
                  </IconButton>
                </div>
                {onSeleccionar ? (
                  <ChevronRight
                    className={`size-4 shrink-0 ${seleccionado === item.ID ? 'text-brand-600' : 'text-line'}`}
                  />
                ) : null}
              </li>
            ),
          )}
        </ul>
      )}
    </section>
  )
}

export function CatalogosPage() {
  const { esAdmin } = useAuth()
  const catalogos = useCatalogos()
  const [grupo, setGrupo] = useState<Grupo>('ubicacion')
  const [seleccion, setSeleccion] = useState<Record<Grupo, number | null>>({
    ubicacion: null,
    organizacion: null,
    clasificacion: null,
  })
  const [error, setError] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)

  if (!esAdmin) return <Navigate to="/" replace />

  const config = grupos[grupo]
  const padres =
    grupo === 'ubicacion' ? catalogos.empresas : grupo === 'organizacion' ? catalogos.divisiones : catalogos.categorias
  const hijosTodos: Array<Fundo | Area | Subcategoria> =
    grupo === 'ubicacion' ? catalogos.fundos : grupo === 'organizacion' ? catalogos.areas : catalogos.subcategorias
  const padreId = seleccion[grupo] ?? padres[0]?.ID ?? null
  const padre = padres.find((p) => p.ID === padreId)
  const hijos = hijosTodos.filter((h) => idPadre(h) === padreId)

  const ejecutar = async (accion: () => Promise<unknown>, mensaje: string) => {
    setError(null)
    setAviso(null)
    try {
      await accion()
      await catalogos.recargar()
      setAviso(mensaje)
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo completar la operación')
      return false
    }
  }

  const guardarPadre = (nombre: string, id?: number) =>
    ejecutar(
      () => (id ? api.put(`${config.padre.ruta}/${id}`, { NOMBRE: nombre }) : api.post(config.padre.ruta, { NOMBRE: nombre })),
      id ? `Se renombró la ${config.padre.singular}.` : `Se agregó la ${config.padre.singular} “${nombre}”.`,
    )

  const guardarHijo = (nombre: string, id?: number) => {
    const cuerpo = { NOMBRE: nombre, [config.hijo.fk]: padreId }
    return ejecutar(
      () => (id ? api.put(`${config.hijo.ruta}/${id}`, cuerpo) : api.post(config.hijo.ruta, cuerpo)),
      id ? `Se renombró el registro.` : `Se agregó “${nombre}” a ${padre?.NOMBRE ?? ''}.`,
    )
  }

  const eliminar = (nivel: Nivel, item: CatalogoItem) => {
    if (!window.confirm(`¿Eliminar “${item.NOMBRE}”? No se puede eliminar si tiene registros asociados.`)) return
    void ejecutar(() => api.delete(`${nivel.ruta}/${item.ID}`), `Se eliminó “${item.NOMBRE}”.`)
  }

  return (
    <Page
      titulo="Catálogos"
      descripcion="Maestros de ubicación y de clasificación de inspecciones. Solo administradores."
    >
      <div className="space-y-4">
        <div className="max-w-md">
          <SegmentedControl<Grupo>
            etiqueta="Catálogo"
            value={grupo}
            onChange={(g) => {
              setGrupo(g)
              setError(null)
              setAviso(null)
            }}
            opciones={(Object.keys(grupos) as Grupo[]).map((g) => ({ valor: g, texto: grupos[g].etiqueta }))}
          />
        </div>
        {error ? <Alert mensaje={error} /> : null}
        {catalogos.error ? <Alert mensaje={catalogos.error} /> : null}
        {aviso ? <Notice tono="success">{aviso}</Notice> : null}

        <div className="grid gap-4 md:grid-cols-[minmax(0,20rem)_minmax(0,1fr)]">
          <ListaEditable
            key={`${grupo}-padre`}
            nivel={config.padre}
            items={padres}
            conteo={(id) => hijosTodos.filter((h) => idPadre(h) === id).length}
            seleccionado={padreId}
            onSeleccionar={(id) => setSeleccion((s) => ({ ...s, [grupo]: id }))}
            onGuardar={guardarPadre}
            onEliminar={(item) => eliminar(config.padre, item)}
            vacio={`Aún no hay ${config.padre.titulo.toLowerCase()}.`}
          />
          <ListaEditable
            key={`${grupo}-hijo-${padreId}`}
            nivel={{ ...config.hijo, titulo: padre ? `${config.hijo.titulo} de ${padre.NOMBRE}` : config.hijo.titulo }}
            items={hijos}
            onGuardar={guardarHijo}
            onEliminar={(item) => eliminar(config.hijo, item)}
            bloqueada={padre ? undefined : `Primero agregue o elija una ${config.padre.singular}.`}
            vacio={`${padre?.NOMBRE ?? ''} no tiene ${config.hijo.titulo.toLowerCase()} todavía.`}
          />
        </div>
      </div>
    </Page>
  )
}
