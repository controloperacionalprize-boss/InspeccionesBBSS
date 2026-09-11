import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Lock } from 'lucide-react'
import { Page } from '../../components/AppShell'
import { Button } from '../../components/Button'
import { DniLookup } from '../../components/DniLookup'
import { Alert, Notice, RegistroNoDisponible } from '../../components/Feedback'
import { Field, Input, Textarea } from '../../components/Field'
import { LocationFields, TipoConsultaField } from '../../components/LocationFields'
import { Card, FormFooter } from '../../components/Surface'
import { useCatalogos } from '../../hooks/useCatalogos'
import { hoyIso } from '../../lib/fechas'
import { api, ApiError } from '../../services/apiClient'
import type { Consulta, TipoConsulta } from '../../types/api'

export function ConsultaFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const catalogos = useCatalogos()
  const esNueva = !id

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
  const [TIPO_CONSULTA, setTipo] = useState<TipoConsulta | ''>('')
  const [noDisponible, setNoDisponible] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [guardado, setGuardado] = useState(Boolean((location.state as { guardado?: boolean } | null)?.guardado))
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
        setTipo(item.TIPO_CONSULTA ?? '')
        setNoDisponible(item.ELIMINADO)
      })
      .catch((err: Error) => (err instanceof ApiError && err.status === 404 ? setNoDisponible(true) : setError(err.message)))
  }, [id])

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
        TIPO_CONSULTA: TIPO_CONSULTA || null,
      }
      if (esNueva) {
        const creada = await api.post<Consulta>('/consultas', {
          ...base,
          RESPUESTA_INMEDIATA: RESPUESTA_INMEDIATA || null,
        })
        navigate(`/consultas/${creada.ID}`, { replace: true, state: { guardado: true } })
      } else {
        await api.put(`/consultas/${id}`, { ...base, RESPUESTA_POSTERIOR: RESPUESTA_POSTERIOR || null })
        setGuardado(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar')
    } finally {
      setEnviando(false)
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
      descripcion={esNueva ? 'La respuesta inmediata se registra ahora y queda fija.' : undefined}
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
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Fecha de la consulta">
                  <Input
                    type="date"
                    required
                    max={hoyIso()}
                    value={FECHA_CONSULTA}
                    onChange={(e) => setFecha(e.target.value)}
                  />
                </Field>
                <TipoConsultaField value={TIPO_CONSULTA} onChange={setTipo} />
              </div>
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
