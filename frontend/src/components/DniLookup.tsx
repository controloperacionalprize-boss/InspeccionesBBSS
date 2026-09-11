import { useState } from 'react'
import { AlertCircle, CheckCircle2, Info, Loader2, Search } from 'lucide-react'
import { cacheado } from '../lib/cache'
import { api, ApiError } from '../services/apiClient'
import type { Trabajador } from '../types/api'
import { Field, Input } from './Field'

type Aviso = { tono: 'ok' | 'alerta' | 'info'; texto: string }

const estiloAviso = {
  ok: { clase: 'text-emerald-700', Icono: CheckCircle2 },
  alerta: { clase: 'text-amber-700', Icono: AlertCircle },
  info: { clase: 'text-muted', Icono: Info },
}

export function DniLookup({
  dni,
  nombres,
  onDni,
  onNombres,
}: {
  dni: string
  nombres: string
  onDni: (value: string) => void
  onNombres: (value: string) => void
}) {
  const [aviso, setAviso] = useState<Aviso | null>(null)
  const [buscando, setBuscando] = useState(false)

  const buscar = async (valor: string) => {
    setAviso(null)
    if (!/^\d{8}$/.test(valor)) {
      setAviso({ tono: 'alerta', texto: 'El DNI debe tener 8 dígitos' })
      return
    }
    setBuscando(true)
    try {
      // Cada búsqueda consulta la base de RR.HH.: se reutiliza el resultado del mismo DNI por 10 min.
      const trabajador = await cacheado(`trabajador:${valor}`, 10 * 60_000, () =>
        api.get<Trabajador>(`/trabajadores/${valor}`),
      )
      onNombres(trabajador.APELLIDOS_NOMBRES)
      setAviso(
        trabajador.VIGENTE === false
          ? { tono: 'alerta', texto: 'Encontrado en RR.HH., pero figura como no vigente' }
          : { tono: 'ok', texto: `Encontrado en RR.HH.${trabajador.CARGO ? ` · ${trabajador.CARGO}` : ''}` },
      )
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setAviso({ tono: 'info', texto: 'Búsqueda de RR.HH. no disponible. Escriba el nombre a mano.' })
      } else if (err instanceof ApiError && err.status === 404) {
        setAviso({ tono: 'alerta', texto: 'No figura en RR.HH. Puede escribir el nombre a mano.' })
      } else {
        setAviso({ tono: 'alerta', texto: err instanceof Error ? err.message : 'No se pudo buscar el DNI' })
      }
    } finally {
      setBuscando(false)
    }
  }

  const cambiarDni = (texto: string) => {
    const limpio = texto.replace(/\D/g, '').slice(0, 8)
    onDni(limpio)
    setAviso(null)
    if (limpio.length === 8 && limpio !== dni) void buscar(limpio)
  }

  const Estilo = aviso ? estiloAviso[aviso.tono] : null

  return (
    <div className="grid gap-4 sm:grid-cols-[minmax(0,14rem)_1fr]">
      <Field
        label="DNI del trabajador"
        hint={
          aviso && Estilo ? (
            <span className={`flex items-center gap-1.5 ${Estilo.clase}`}>
              <Estilo.Icono className="size-3.5 shrink-0" />
              {aviso.texto}
            </span>
          ) : (
            'Se busca en RR.HH. al completar los 8 dígitos'
          )
        }
      >
        <div className="flex gap-2">
          <Input
            required
            inputMode="numeric"
            pattern="\d{8}"
            title="8 dígitos"
            maxLength={8}
            placeholder="00000000"
            value={dni}
            onChange={(e) => cambiarDni(e.target.value)}
          />
          <button
            type="button"
            onClick={() => void buscar(dni)}
            disabled={buscando}
            aria-label="Buscar DNI en RR.HH."
            title="Buscar en RR.HH."
            className="inline-flex size-10 shrink-0 items-center justify-center rounded-lg border border-line text-muted transition-colors hover:border-brand-300 hover:text-brand-700 disabled:opacity-50"
          >
            {buscando ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
          </button>
        </div>
      </Field>
      <Field label="Apellidos y nombres">
        <Input required maxLength={150} value={nombres} onChange={(e) => onNombres(e.target.value)} />
      </Field>
    </div>
  )
}
