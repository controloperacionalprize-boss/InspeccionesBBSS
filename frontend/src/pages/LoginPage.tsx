import { useState, type FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { ArrowRight, Check, Eye, EyeOff, Lock, Sprout, User } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { ApiError } from '../services/apiClient'
import { Button } from '../components/Button'
import { Field, Input } from '../components/Field'
import { Alert } from '../components/Feedback'

const puntos = [
  'Inspecciones de Campo y Packing con evidencia fotográfica',
  'Consultas de trabajadores con respuesta en el momento',
  'Trazabilidad de entrega de indumentaria',
]

export function LoginPage() {
  const { usuario, listo, login } = useAuth()
  const location = useLocation()
  const [nombreUsuario, setNombreUsuario] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [verContrasena, setVerContrasena] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (listo && usuario) {
    const destino = (location.state as { from?: string } | null)?.from ?? '/'
    return <Navigate to={destino} replace />
  }

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await login(nombreUsuario.trim(), contrasena)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo iniciar sesión')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[minmax(0,560px)_1fr]">
      <section className="relative hidden overflow-hidden bg-gradient-to-br from-brand-900 via-[#123166] to-brand-700 p-14 text-white lg:flex lg:flex-col lg:justify-between">
        <svg
          aria-hidden="true"
          className="pointer-events-none absolute -right-32 -top-24 opacity-60"
          width="480"
          height="480"
          viewBox="0 0 480 480"
          fill="none"
        >
          <circle cx="240" cy="240" r="239" stroke="#3B82F6" strokeOpacity="0.35" />
          <circle cx="240" cy="240" r="180" stroke="#3B82F6" strokeOpacity="0.25" />
          <circle cx="240" cy="240" r="120" stroke="#3B82F6" strokeOpacity="0.18" />
        </svg>

        <div className="relative flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-lg bg-white/10 ring-1 ring-white/15">
            <Sprout className="size-5 text-brand-200" />
          </div>
          <p className="font-display text-lg font-extrabold tracking-tight">Consultar Campo</p>
        </div>

        <div className="relative max-w-md space-y-6">
          <h1 className="font-display text-[38px] font-extrabold leading-[1.15] tracking-tight">
            Control operacional de Campo y Packing en un solo lugar.
          </h1>
          <p className="text-[15px] leading-relaxed text-brand-100/90">
            Inspecciones, consultas de personal e indumentaria, con trazabilidad por fundo y área.
          </p>
          <ul className="space-y-3.5">
            {puntos.map((texto) => (
              <li key={texto} className="flex items-center gap-3 text-sm text-slate-200">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-white/10">
                  <Check className="size-4" />
                </span>
                {texto}
              </li>
            ))}
          </ul>
        </div>

        <p className="relative text-[13px] text-brand-200/70">Uso interno · AQUANQA</p>
      </section>

      <section className="flex items-center justify-center bg-sand px-6 py-12">
        <form onSubmit={(e) => void enviar(e)} className="w-full max-w-[380px] animate-fade-up space-y-5">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <div className="flex size-10 items-center justify-center rounded-lg bg-brand-900">
              <Sprout className="size-5 text-brand-200" />
            </div>
            <p className="font-display text-lg font-extrabold tracking-tight text-ink">Consultar Campo</p>
          </div>
          <div>
            <h2 className="font-display text-[26px] font-extrabold tracking-tight text-ink">Iniciar sesión</h2>
            <p className="mt-1 text-sm text-muted">Ingrese con su usuario y contraseña del sistema.</p>
          </div>
          {error ? <Alert mensaje={error} /> : null}
          <Field label="Usuario">
            <div className="relative">
              <User className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />
              <Input
                autoComplete="username"
                required
                autoFocus
                className="h-11 pl-10"
                value={nombreUsuario}
                onChange={(e) => setNombreUsuario(e.target.value)}
              />
            </div>
          </Field>
          <Field label="Contraseña">
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />
              <Input
                type={verContrasena ? 'text' : 'password'}
                autoComplete="current-password"
                required
                className="h-11 px-10"
                value={contrasena}
                onChange={(e) => setContrasena(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setVerContrasena((v) => !v)}
                aria-label={verContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                className="absolute right-2 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-md text-muted hover:text-ink"
              >
                {verContrasena ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              </button>
            </div>
          </Field>
          <Button type="submit" className="h-11 w-full" loading={enviando}>
            {enviando ? 'Ingresando…' : 'Iniciar sesión'}
            {enviando ? null : <ArrowRight className="size-4" />}
          </Button>
          <p className="text-center text-[13px] text-muted">
            ¿Olvidó su contraseña? Solicítela a su administrador.
          </p>
        </form>
      </section>
    </div>
  )
}
