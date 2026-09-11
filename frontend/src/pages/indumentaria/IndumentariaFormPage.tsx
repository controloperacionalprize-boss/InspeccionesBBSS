import { useEffect, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { Page } from '../../components/AppShell'
import { Button } from '../../components/Button'
import { DniLookup } from '../../components/DniLookup'
import { Alert, Notice, RegistroNoDisponible } from '../../components/Feedback'
import { Field, Input } from '../../components/Field'
import { LocationFields, TipoConsultaField } from '../../components/LocationFields'
import { Card, FormFooter } from '../../components/Surface'
import { useCatalogos } from '../../hooks/useCatalogos'
import { hoyIso } from '../../lib/fechas'
import { api, ApiError } from '../../services/apiClient'
import type { Indumentaria, TipoConsulta } from '../../types/api'

export function IndumentariaFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const { usuario } = useAuth()
  const catalogos = useCatalogos()
  const esNueva = !id

  const [ID_EMPRESA, setEmpresa] = useState<number | ''>('')
  const [ID_FUNDO, setFundo] = useState<number | ''>('')
  const [ID_DIVISION, setDivision] = useState<number | ''>('')
  const [ID_AREA, setArea] = useState<number | ''>('')
  const [DNI_TRABAJADOR, setDni] = useState('')
  const [APELLIDOS_NOMBRES, setNombres] = useState('')
  const [FECHA_ENTREGA, setFecha] = useState(hoyIso())
  const [CANTIDAD, setCantidad] = useState(1)
  const [TIPO, setTipoItem] = useState('')
  const [FIRMA, setFirma] = useState('')
  const [RESPONSABLE_REGISTRO, setResponsable] = useState(
    usuario ? `${usuario.nombre} ${usuario.apellido}` : '',
  )
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
      .get<Indumentaria>(`/indumentaria/${id}`)
      .then((item) => {
        setEmpresa(item.ID_EMPRESA)
        setFundo(item.ID_FUNDO)
        setDivision(item.ID_DIVISION)
        setArea(item.ID_AREA)
        setDni(item.DNI_TRABAJADOR)
        setNombres(item.APELLIDOS_NOMBRES)
        setFecha(item.FECHA_ENTREGA)
        setCantidad(item.CANTIDAD)
        setTipoItem(item.TIPO)
        setFirma(item.FIRMA ?? '')
        setResponsable(item.RESPONSABLE_REGISTRO)
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
      const cuerpo = {
        ID_EMPRESA,
        ID_FUNDO,
        ID_DIVISION,
        ID_AREA,
        DNI_TRABAJADOR,
        APELLIDOS_NOMBRES,
        FECHA_ENTREGA,
        CANTIDAD,
        TIPO,
        FIRMA: FIRMA || null,
        RESPONSABLE_REGISTRO,
        TIPO_CONSULTA: TIPO_CONSULTA || null,
      }
      if (esNueva) {
        const creada = await api.post<Indumentaria>('/indumentaria', cuerpo)
        navigate(`/indumentaria/${creada.ID}`, { replace: true, state: { guardado: true } })
      } else {
        await api.put(`/indumentaria/${id}`, cuerpo)
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
      <Page angosto titulo="Registro no disponible" volver={{ to: '/indumentaria', texto: 'Indumentaria' }}>
        <RegistroNoDisponible volverA="/indumentaria" texto="Volver a indumentaria" />
      </Page>
    )
  }

  return (
    <Page
      angosto
      titulo={esNueva ? 'Nueva entrega' : `Entrega #${id}`}
      descripcion={esNueva ? 'Registre el ítem entregado y el trabajador que lo recibe.' : undefined}
      volver={{ to: '/indumentaria', texto: 'Indumentaria' }}
    >
      <form onSubmit={(e) => void enviar(e)} className="space-y-4">
        {guardado ? <Notice tono="success">Cambios guardados.</Notice> : null}
        {error ? <Alert mensaje={error} /> : null}

        <div className="space-y-4">
          <Card titulo="Trabajador">
            <DniLookup dni={DNI_TRABAJADOR} nombres={APELLIDOS_NOMBRES} onDni={setDni} onNombres={setNombres} />
          </Card>

          <Card titulo="Entrega">
            <div className="grid gap-4 sm:grid-cols-[minmax(0,1fr)_8rem_12rem]">
              <Field label="Ítem entregado">
                <Input
                  required
                  maxLength={100}
                  placeholder="Ej.: Guantes de nitrilo"
                  value={TIPO}
                  onChange={(e) => setTipoItem(e.target.value)}
                />
              </Field>
              <Field label="Cantidad">
                <Input
                  type="number"
                  min={1}
                  required
                  value={CANTIDAD}
                  onChange={(e) => setCantidad(Number(e.target.value))}
                />
              </Field>
              <Field label="Fecha de entrega">
                <Input
                  type="date"
                  required
                  max={hoyIso()}
                  value={FECHA_ENTREGA}
                  onChange={(e) => setFecha(e.target.value)}
                />
              </Field>
            </div>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <TipoConsultaField value={TIPO_CONSULTA} onChange={setTipo} />
              <Field label="Responsable de registro">
                <Input
                  required
                  maxLength={150}
                  value={RESPONSABLE_REGISTRO}
                  onChange={(e) => setResponsable(e.target.value)}
                />
              </Field>
              <Field
                label="Firma"
                hint="Provisional: texto o referencia, mientras se define la captura de firma."
                className="sm:col-span-2"
              >
                <Input maxLength={8000} value={FIRMA} onChange={(e) => setFirma(e.target.value)} />
              </Field>
            </div>
          </Card>

          <Card titulo="Ubicación">
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
        </div>

        <FormFooter>
          <Link to="/indumentaria">
            <Button variant="secondary">Cancelar</Button>
          </Link>
          <Button type="submit" loading={enviando}>
            {enviando ? 'Guardando…' : esNueva ? 'Guardar entrega' : 'Guardar cambios'}
          </Button>
        </FormFooter>
      </form>
    </Page>
  )
}
