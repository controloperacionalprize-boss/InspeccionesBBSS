import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Lock } from 'lucide-react'
import { Page } from '../../components/AppShell'
import { Button } from '../../components/Button'
import { DniLookup } from '../../components/DniLookup'
import { Alert, Notice, RegistroNoDisponible } from '../../components/Feedback'
import { Field, Input, Textarea } from '../../components/Field'
import { LocationFields } from '../../components/LocationFields'
import { PhotoUploader } from '../../components/PhotoUploader'
import { Card, FormFooter } from '../../components/Surface'
import { useCatalogos } from '../../hooks/useCatalogos'
import { hoyIso } from '../../lib/fechas'
import { tipoConsultaDesdeDivision } from '../../lib/tipoConsulta'
import { api, ApiError } from '../../services/apiClient'
import type { Consulta, Foto } from '../../types/api'

interface EstadoNavegacion {
  guardado?: boolean
  errorFotos?: string
}

export function ConsultaFormPage() {
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
  const [FECHA_CONSULTA, setFecha] = useState(hoyIso())
  const [DNI_TRABAJADOR, setDni] = useState('')
  const [APELLIDOS_NOMBRES, setNombres] = useState('')
  const [DESCRIPCION, setDescripcion] = useState('')
  const [AREA_RESPONSABLE, setAreaResp] = useState('')
  const [RESPUESTA_INMEDIATA, setInmediata] = useState('')
  const [RESPUESTA_POSTERIOR, setPosterior] = useState('')
  const [noDisponible, setNoDisponible] = useState(false)
  const [fotos, setFotos] = useState<Foto[]>([])
  const [archivos, setArchivos] = useState<File[]>([])
  const [error, setError] = useState<string | null>(estadoInicial.errorFotos ?? null)
  const [guardado, setGuardado] = useState(Boolean(estadoInicial.guardado))
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    if (location.state) navigate(location.pathname, { replace: true, state: null })
  }, [location.state, location.pathname, navigate])

  useEffect(() => {
    if (!id) return
    api
      .get<Consulta>(`/consultas/${id}`)
      .then((item) => {
        setEmpresa(item.ID_EMPRESA)
        setFundo(item.ID_FUNDO)
        setDivision(item.ID_DIVISION)
        setArea(item.ID_AREA)
        setFecha(item.FECHA_CONSULTA)
        setDni(item.DNI_TRABAJADOR)
        setNombres(item.APELLIDOS_NOMBRES)
        setDescripcion(item.DESCRIPCION)
        setAreaResp(item.AREA_RESPONSABLE)
        setInmediata(item.RESPUESTA_INMEDIATA ?? '')
        setPosterior(item.RESPUESTA_POSTERIOR ?? '')
        setNoDisponible(item.ELIMINADO)
      })
      .catch((err: Error) => (err instanceof ApiError && err.status === 404 ? setNoDisponible(true) : setError(err.message)))
    api
      .get<Foto[]>(`/consultas/${id}/fotos`)
      .then(setFotos)
      .catch(() => setFotos([]))
  }, [id])

  const subirFotos = async (consultaId: number) => {
    if (!archivos.length) return
    const data = new FormData()
    archivos.forEach((archivo) => data.append('archivos', archivo))
    await api.post(`/consultas/${consultaId}/fotos`, data)
  }

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setGuardado(false)
    setEnviando(true)
    try {
      const base = {
        ID_EMPRESA,
        ID_FUNDO,
        ID_DIVISION,
        ID_AREA,
        FECHA_CONSULTA,
        DNI_TRABAJADOR,
        APELLIDOS_NOMBRES,
        DESCRIPCION,
        AREA_RESPONSABLE,
        TIPO_CONSULTA: tipoConsultaDesdeDivision(catalogos.divisiones, ID_DIVISION) || 'Campo',
      }
      if (esNueva) {
        const creada = await api.post<Consulta>('/consultas', {
          ...base,
          RESPUESTA_INMEDIATA: RESPUESTA_INMEDIATA || null,
        })
        let errorFotos: string | undefined
        try {
          await subirFotos(creada.ID)
        } catch (err) {
          errorFotos = `La consulta se guardó, pero las fotos no se subieron: ${err instanceof Error ? err.message : 'error desconocido'}`
        }
        navigate(`/consultas/${creada.ID}`, { replace: true, state: { guardado: !errorFotos, errorFotos } })
      } else {
        await api.put(`/consultas/${id}`, { ...base, RESPUESTA_POSTERIOR: RESPUESTA_POSTERIOR || null })
        await subirFotos(Number(id))
        setArchivos([])
        setFotos(await api.get<Foto[]>(`/consultas/${id}/fotos`))
        setGuardado(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar')
    } finally {
      setEnviando(false)
    }
  }

  const quitarFoto = async (fotoId: number) => {
    if (!window.confirm('¿Quitar esta foto de la consulta?')) return
    try {
      await api.delete(`/fotos/${fotoId}`)
      setFotos((prev) => prev.filter((foto) => foto.ID !== fotoId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo quitar la foto')
    }
  }

  if (noDisponible) {
    return (
      <Page angosto titulo="Registro no disponible" volver={{ to: '/consultas', texto: 'Consultas' }}>
        <RegistroNoDisponible volverA="/consultas" texto="Volver a consultas" />
      </Page>
    )
  }

  return (
    <Page
      angosto
      titulo={esNueva ? 'Nueva consulta' : `Consulta #${id}`}
      descripcion={esNueva ? 'La respuesta inmediata se registra ahora y queda fija. Puede adjuntar fotos.' : undefined}
      volver={{ to: '/consultas', texto: 'Consultas' }}
    >
      <form onSubmit={(e) => void enviar(e)} className="space-y-4">
        {guardado ? <Notice tono="success">Cambios guardados.</Notice> : null}
        {error ? <Alert mensaje={error} /> : null}

        <div className="space-y-4">
          <Card titulo="Trabajador">
            <DniLookup dni={DNI_TRABAJADOR} nombres={APELLIDOS_NOMBRES} onDni={setDni} onNombres={setNombres} />
          </Card>

          <Card titulo="Ubicación">
            <div className="space-y-4">
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
              <Field label="Fecha de la consulta">
                <Input
                  type="date"
                  required
                  max={hoyIso()}
                  value={FECHA_CONSULTA}
                  onChange={(e) => setFecha(e.target.value)}
                />
              </Field>
            </div>
          </Card>

          <Card titulo="Consulta y respuesta">
            <div className="space-y-4">
              <Field label="¿Qué consultó el trabajador?">
                <Textarea required value={DESCRIPCION} onChange={(e) => setDescripcion(e.target.value)} />
              </Field>
              <Field label="Área responsable">
                <Input
                  required
                  maxLength={150}
                  placeholder="Ej.: Recursos Humanos, Planillas, Transporte"
                  value={AREA_RESPONSABLE}
                  onChange={(e) => setAreaResp(e.target.value)}
                />
              </Field>

              {esNueva ? (
                <Field label="Respuesta inmediata" hint="Queda fija una vez guardada la consulta.">
                  <Textarea value={RESPUESTA_INMEDIATA} onChange={(e) => setInmediata(e.target.value)} />
                </Field>
              ) : (
                <div className="space-y-1.5">
                  <span className="flex items-center gap-1.5 text-[13px] font-semibold text-ink-soft">
                    Respuesta inmediata
                    <Lock className="size-3.5 text-muted" aria-label="No editable" />
                  </span>
                  <p className="whitespace-pre-line rounded-lg border border-line bg-sand px-3.5 py-2.5 text-sm text-ink-soft">
                    {RESPUESTA_INMEDIATA || 'No se registró respuesta en el momento.'}
                  </p>
                </div>
              )}

              {!esNueva ? (
                <Field label="Respuesta posterior" hint="Seguimiento registrado desde la web.">
                  <Textarea
                    value={RESPUESTA_POSTERIOR}
                    placeholder="Respuesta final dada al trabajador."
                    onChange={(e) => setPosterior(e.target.value)}
                  />
                </Field>
              ) : null}
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
          <Link to="/consultas">
            <Button variant="secondary">Cancelar</Button>
          </Link>
          <Button type="submit" loading={enviando}>
            {enviando ? 'Guardando…' : esNueva ? 'Guardar consulta' : 'Guardar cambios'}
          </Button>
        </FormFooter>
      </form>
    </Page>
  )
}
