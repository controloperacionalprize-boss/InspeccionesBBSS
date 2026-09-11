import { useState, type ReactNode } from 'react'
import { Link, NavLink, Navigate, Outlet, useLocation } from 'react-router-dom'
import {
  ChevronLeft,
  ClipboardList,
  LayoutDashboard,
  Layers,
  LogOut,
  Menu,
  MessageSquareText,
  Shirt,
  Sprout,
  Users,
  X,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

const operacion = [
  { to: '/', label: 'Inicio', icon: LayoutDashboard, fin: true },
  { to: '/inspecciones', label: 'Inspecciones', icon: ClipboardList },
  { to: '/consultas', label: 'Consultas', icon: MessageSquareText },
  { to: '/indumentaria', label: 'Indumentaria', icon: Shirt },
]

const administracion = [
  { to: '/catalogos', label: 'Catálogos', icon: Layers },
  { to: '/usuarios', label: 'Usuarios', icon: Users },
]

function Marca() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="flex size-9 items-center justify-center rounded-lg bg-white/10 ring-1 ring-white/15">
        <Sprout className="size-5 text-brand-200" />
      </div>
      <div className="leading-tight">
        <p className="font-display text-[15px] font-extrabold tracking-tight text-white">Consultar Campo</p>
        <p className="text-xs text-brand-200/80">Campo · Packing</p>
      </div>
    </div>
  )
}

function Navegacion({ esAdmin }: { esAdmin: boolean }) {
  const enlace = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
      isActive ? 'bg-white/10 font-semibold text-white' : 'font-medium text-brand-100/75 hover:bg-white/5 hover:text-white'
    }`

  return (
    <nav className="flex-1 space-y-1 overflow-y-auto px-3" aria-label="Principal">
      {operacion.map((item) => (
        <NavLink key={item.to} to={item.to} end={'fin' in item} className={enlace}>
          <item.icon className="size-[18px]" />
          {item.label}
        </NavLink>
      ))}
      {esAdmin ? (
        <>
          <p className="px-3 pb-1.5 pt-5 text-[11px] font-bold uppercase tracking-[0.08em] text-brand-300/60">
            Administración
          </p>
          {administracion.map((item) => (
            <NavLink key={item.to} to={item.to} className={enlace}>
              <item.icon className="size-[18px]" />
              {item.label}
            </NavLink>
          ))}
        </>
      ) : null}
    </nav>
  )
}

function iniciales(nombre: string, apellido: string) {
  return `${nombre.charAt(0)}${apellido.charAt(0)}`.toUpperCase()
}

function PanelLateral({ onCerrar }: { onCerrar?: () => void }) {
  const { usuario, esAdmin, logout } = useAuth()
  if (!usuario) return null
  return (
    <div className="flex h-full flex-col bg-gradient-to-b from-brand-900 to-brand-950 py-5">
      <div className="flex items-center justify-between px-5 pb-7">
        <Marca />
        {onCerrar ? (
          <button
            type="button"
            onClick={onCerrar}
            aria-label="Cerrar menú"
            className="rounded-lg p-1.5 text-brand-100 hover:bg-white/10"
          >
            <X className="size-5" />
          </button>
        ) : null}
      </div>
      <Navegacion esAdmin={esAdmin} />
      <div className="mx-3 mt-4 flex items-center gap-3 rounded-xl bg-white/[0.06] p-3">
        <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-brand-500 font-display text-[13px] font-bold text-white">
          {iniciales(usuario.nombre, usuario.apellido)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold text-white">
            {usuario.nombre} {usuario.apellido}
          </p>
          <p className="text-xs capitalize text-brand-200/80">
            {usuario.rol === 'admin' ? 'Administrador' : 'Inspector'}
          </p>
        </div>
        <button
          type="button"
          onClick={logout}
          aria-label="Cerrar sesión"
          title="Cerrar sesión"
          className="rounded-lg p-2 text-brand-200 transition-colors hover:bg-white/10 hover:text-white"
        >
          <LogOut className="size-4" />
        </button>
      </div>
    </div>
  )
}

export function ProtectedLayout() {
  const { usuario, listo } = useAuth()
  const location = useLocation()
  // El menú recuerda en qué ruta se abrió: al navegar a otra, queda cerrado sin un efecto.
  const [menuAbiertoEn, setMenuAbiertoEn] = useState<string | null>(null)
  const menuAbierto = menuAbiertoEn === location.pathname
  const setMenuAbierto = (abierto: boolean) => setMenuAbiertoEn(abierto ? location.pathname : null)

  if (!listo) {
    return (
      <div className="grid min-h-screen place-items-center text-muted">
        <div className="flex items-center gap-2 text-sm font-medium">
          <span className="size-2 animate-ping rounded-full bg-brand-500" />
          Cargando sesión…
        </div>
      </div>
    )
  }
  if (!usuario) return <Navigate to="/login" replace state={{ from: location.pathname }} />

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 lg:block">
        <PanelLateral />
      </aside>

      <div className="sticky top-0 z-30 flex h-14 items-center gap-3 bg-brand-900 px-4 lg:hidden">
        <button
          type="button"
          onClick={() => setMenuAbierto(true)}
          aria-label="Abrir menú"
          className="rounded-lg p-1.5 text-white hover:bg-white/10"
        >
          <Menu className="size-5" />
        </button>
        <Marca />
      </div>

      {menuAbierto ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Cerrar menú"
            className="absolute inset-0 bg-slate-950/40"
            onClick={() => setMenuAbierto(false)}
          />
          <div className="absolute inset-y-0 left-0 w-72 max-w-[85%] shadow-lift">
            <PanelLateral onCerrar={() => setMenuAbierto(false)} />
          </div>
        </div>
      ) : null}

      <main className="lg:pl-64">
        <Outlet />
      </main>
    </div>
  )
}

export function Page({
  titulo,
  descripcion,
  accion,
  volver,
  angosto = false,
  children,
}: {
  titulo: string
  descripcion?: string
  accion?: ReactNode
  volver?: { to: string; texto: string }
  angosto?: boolean
  children: ReactNode
}) {
  const ancho = angosto ? 'max-w-3xl' : 'max-w-6xl'
  return (
    <>
      <header className="z-20 border-b border-line bg-white/90 backdrop-blur lg:sticky lg:top-0">
        <div
          className={`mx-auto flex min-h-[72px] ${ancho} flex-wrap items-center justify-between gap-x-6 gap-y-3 px-4 py-3 sm:px-6 lg:px-8`}
        >
          <div className="min-w-0">
            {volver ? (
              <Link
                to={volver.to}
                className="mb-0.5 inline-flex items-center gap-1 text-[13px] font-medium text-muted hover:text-brand-700"
              >
                <ChevronLeft className="size-3.5" />
                {volver.texto}
              </Link>
            ) : null}
            <h1 className="font-display text-xl font-bold tracking-tight text-ink">{titulo}</h1>
            {descripcion ? <p className="text-[13px] text-muted">{descripcion}</p> : null}
          </div>
          {accion ? <div className="flex flex-wrap items-center gap-2">{accion}</div> : null}
        </div>
      </header>
      <div className={`mx-auto ${ancho} animate-fade-up px-4 py-6 sm:px-6 lg:px-8`}>{children}</div>
    </>
  )
}
