import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Page } from '../../components/AppShell'
import { Button } from '../../components/Button'
import { Alert, Notice, RegistroNoDisponible } from '../../components/Feedback'
import { Field, Input, Textarea } from '../../components/Field'
import { CategoriaFields, LocationFields } from '../../components/LocationFields'
import { PhotoUploader } from '../../components/PhotoUploader'
import { Card, FormFooter } from '../../components/Surface'
import { useCatalogos } from '../../hooks/useCatalogos'
import { hoyIso } from '../../lib/fechas'
import { tipoConsultaDesdeDivision } from '../../lib/tipoConsulta'
import { api, ApiError } from '../../services/apiClient'
import type { Foto, Inspeccion } from '../../types/api'

interface EstadoNavegacion {
  guardado?: boolean
  errorFotos?: string
}

export function InspeccionFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const catalogos = useCatalogos()
  const esNueva = !id
  const estadoInicial = (location.state as EstadoNavegacion | null) ?? {}

  const [ID_EMPRESA, setEmpresa] = useState<number | ''>('')
  const [ID_FUNDO, setFundo] = useState<number | ''>('')
  const [ID_DIVISION, setDivision] = useState<number | ''>('')
  const [ID_AREA, setArea] = useState<number | ''>('')
  const [ID_CATEGORIA, setCategoria] = useState<number | ''>('')
  const [ID_SUBCATEGORIA, setSubcategoria] = useState<number | ''>('')
  const [FECHA_OBSERVACION, setFecha] = useState(hoyIso())
  const [hora, setHora] = useState('')
  const [DESCRIPCION, setDescripcion] = useState('')
  const [ACCION_CORRECTIVA, setAccion] = useState('')
  const [PLAZO_LEVANTAMIENTO, setPlazo] = useState('')
  const [noDisponible, setNoDisponible] = useState(false)
  const [fotos, setFotos] = useState<Foto[]>([])
  const [archivos, setArchivos] = useState<File[]>([])
  const [error, setError] = useState<string | null>(estadoInicial.errorFotos ?? null)
  const [guardado, setGuardado] = useState(Boolean(estadoInicial.guardado))
  const [enviando, setEnviando] = useState(false)

  // El aviso viaja en el estado del historial; se limpia para que no reaparezca al recargar.
  useEffect(() => {
    if (location.state) navigate(location.pathname, { replace: true, state: null })
  }, [location.state, location.pathname, navigate])

  useEffect(() => {
    if (!id) return
    api
      .get<Inspeccion>(`/inspecciones/${id}`)
      .then((item) => {
        setEmpresa(item.ID_EMPRESA)
        setFundo(item.ID_FUNDO)
        setDivision(item.ID_DIVISION)
        setArea(item.ID_AREA)
        setCategoria(item.ID_CATEGORIA)
        setSubcategoria(item.ID_SUBCATEGORIA)
        setFecha(item.FECHA_OBSERVACION)
        setHora(item.RANGO_HORA ? item.RANGO_HORA.slice(11, 16) : '')
        setDescripcion(item.DESCRIPCION)
        setAccion(item.ACCION_CORRECTIVA ?? '')
        setPlazo(item.PLAZO_LEVANTAMIENTO ?? '')
        setNoDisponible(item.ELIMINADO)
      })
      .catch((err: Error) => (err instanceof ApiError && err.status === 404 ? setNoDisponible(true) : setError(err.message)))
    api
      .get<Foto[]>(`/inspecciones/${id}/fotos`)
      .then(setFotos)
      .catch(() => setFotos([]))
  }, [id])

  const cuerpo = () => ({
    ID_EMPRESA,
    ID_FUNDO,
    ID_DIVISION,
    ID_AREA,
    ID_CATEGORIA,
    ID_SUBCATEGORIA,
    FECHA_OBSERVACION,
    RANGO_HORA: hora ? `${FECHA_OBSERVACION}T${hora}:00` : null,
    DESCRIPCION,
    ACCION_CORRECTIVA: ACCION_CORRECTIVA || null,
    PLAZO_LEVANTAMIENTO: PLAZO_LEVANTAMIENTO || null,
    TIPO_CONSULTA: tipoConsultaDesdeDivision(catalogos.divisiones, ID_DIVISION) || 'Campo',
  })

  const subirFotos = async (inspeccionId: number) => {
    if (!archivos.length) return
    const data = new FormData()
    archivos.forEach((archivo) => data.append('archivos', archivo))
    await api.post(`/inspecciones/${inspeccionId}/fotos`, data)
  }

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setGuardado(false)
    setEnviando(true)
    try {
      if (esNueva) {
        const creada = await api.post<Inspeccion>('/inspecciones', cuerpo())
        // Ya existe: pase lo que pase con las fotos, se continúa en modo edición para no duplicar.
        let errorFotos: string | undefined
        try {
          await subirFotos(creada.ID)
        } catch (err) {
          errorFotos = `La inspección se guardó, pero las fotos no se subieron: ${err instanceof Error ? err.message : 'error desconocido'}`
        }
        navigate(`/inspecciones/${creada.ID}`, { replace: true, state: { guardado: !errorFotos, errorFotos } })
      } else {
        await api.put(`/inspecciones/${id}`, cuerpo())
        await subirFotos(Number(id))
        setArchivos([])
        setFotos(await api.get<Foto[]>(`/inspecciones/${id}/fotos`))
        setGuardado(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar')
    } finally {
      setEnviando(false)
    }
  }

  const quitarFoto = async (fotoId: number) => {
    if (!window.confirm('¿Quitar esta foto de la inspección?')) return
    try {
      await api.delete(`/fotos/${fotoId}`)
      setFotos((prev) => prev.filter((foto) => foto.ID !== fotoId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo quitar la foto')
    }
  }

  if (noDisponible) {
    return (
      <Page angosto titulo="Registro no disponible" volver={{ to: '/inspecciones', texto: 'Inspecciones' }}>
        <RegistroNoDisponible volverA="/inspecciones" texto="Volver a inspecciones" />
      </Page>
    )
  }

  return (
    <Page
      angosto
      titulo={esNueva ? 'Nueva inspección' : `Inspección #${id}`}
      descripcion={esNueva ? 'Complete ubicación, hallazgo y, si aplica, fotos de evidencia.' : undefined}
      volver={{ to: '/inspecciones', texto: 'Inspecciones' }}
    >
      <form onSubmit={(e) => void enviar(e)} className="space-y-4">
        {guardado ? <Notice tono="success">Cambios guardados.</Notice> : null}
        {error ? <Alert mensaje={error} /> : null}
        {catalogos.error ? <Alert mensaje={catalogos.error} /> : null}

        <div className="space-y-4">
          <Card
            titulo="Ubicación"
            descripcion="Fundo y Área se habilitan al elegir Empresa y División."
          >
            <LocationFields
              value={{ ID_EMPRESA, ID_FUNDO, ID_DIVISION, ID_AREA }}
              onChange={(next) => {
                setEmpresa(next.ID_EMPRESA)
                setFundo(next.ID_FUNDO)
                setDivision(next.ID_DIVISION)
                setArea(next.ID_AREA)
              }}
              empresas={catalogos.empresas}
              fundos={catalogos.fundos}
              divisiones={catalogos.divisiones}
              areas={catalogos.areas}
            />
          </Card>

          <Card titulo="Clasificación y hallazgo">
            <div className="space-y-4">
              <CategoriaFields
                idCategoria={ID_CATEGORIA}
                idSubcategoria={ID_SUBCATEGORIA}
                categorias={catalogos.categorias}
                subcategorias={catalogos.subcategorias}
                onChange={(cat, sub) => {
                  setCategoria(cat)
                  setSubcategoria(sub)
                }}
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Fecha de observación">
                  <Input
                    type="date"
                    required
                    max={hoyIso()}
                    value={FECHA_OBSERVACION}
                    onChange={(e) => setFecha(e.target.value)}
                  />
                </Field>
                <Field label="Hora (opcional)">
                  <Input type="time" value={hora} onChange={(e) => setHora(e.target.value)} />
                </Field>
              </div>
              <Field label="Descripción">
                <Textarea
                  required
                  maxLength={8000}
                  placeholder="Qué se observó, dónde y en qué condiciones."
                  value={DESCRIPCION}
                  onChange={(e) => setDescripcion(e.target.value)}
                />
              </Field>
            </div>
          </Card>

          <Card titulo="Seguimiento" descripcion="Opcional al registrar; puede completarse después.">
            <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_14rem]">
              <Field label="Acción correctiva">
                <Textarea
                  maxLength={8000}
                  className="min-h-20"
                  value={ACCION_CORRECTIVA}
                  onChange={(e) => setAccion(e.target.value)}
                />
              </Field>
              <Field label="Plazo de levantamiento" hint="Ej.: 17/09/2026 o “7 días”">
                <Input maxLength={500} value={PLAZO_LEVANTAMIENTO} onChange={(e) => setPlazo(e.target.value)} />
              </Field>
            </div>
          </Card>
        </div>

        <Card
          titulo="Fotos de evidencia"
          accion={
            <span className="text-[13px] font-semibold text-muted">
              {fotos.length} guardada{fotos.length === 1 ? '' : 's'}
              {archivos.length ? ` · ${archivos.length} por subir` : ''}
            </span>
          }
        >
          <PhotoUploader
            existentes={fotos}
            pendientes={archivos}
            onPendientes={setArchivos}
            onQuitarExistente={(fotoId) => void quitarFoto(fotoId)}
          />
        </Card>

        <FormFooter>
          <Link to="/inspecciones">
            <Button variant="secondary">Cancelar</Button>
          </Link>
          <Button type="submit" loading={enviando}>
            {enviando ? 'Guardando…' : esNueva ? 'Guardar inspección' : 'Guardar cambios'}
          </Button>
        </FormFooter>
      </form>
    </Page>
  )
}
