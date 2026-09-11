import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { cacheado, limpiarCache } from '../lib/cache'
import { conectarTiempoReal } from '../lib/tiempoReal'
import { api, setOnUnauthorized, TOKEN_KEY, USER_KEY } from '../services/apiClient'
import type { LoginResponse, Usuario } from '../types/api'

interface AuthContextValue {
  usuario: Usuario | null
  token: string | null
  listo: boolean
  esAdmin: boolean
  login: (usuario: string, contrasena: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

function leerUsuario(): Usuario | null {
  const crudo = localStorage.getItem(USER_KEY)
  if (!crudo) return null
  try {
    return JSON.parse(crudo) as Usuario
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [usuario, setUsuario] = useState<Usuario | null>(leerUsuario)
  const [listo, setListo] = useState(false)

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    limpiarCache()
    setToken(null)
    setUsuario(null)
  }, [])

  useEffect(() => {
    setOnUnauthorized(logout)
    return () => setOnUnauthorized(null)
  }, [logout])

  useEffect(() => {
    if (!token) return
    return conectarTiempoReal(token)
  }, [token])

  // La sesión guardada se valida una sola vez al abrir la app (el login ya trae el usuario).
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) {
      setListo(true)
      return
    }
    cacheado('auth:me', 5_000, () => api.get<Usuario>('/auth/me'))
      .then((perfil) => {
        setUsuario(perfil)
        localStorage.setItem(USER_KEY, JSON.stringify(perfil))
      })
      .catch(() => logout())
      .finally(() => setListo(true))
  }, [logout])

  const login = useCallback(async (nombreUsuario: string, contrasena: string) => {
    const respuesta = await api.post<LoginResponse>('/auth/login', {
      usuario: nombreUsuario,
      contrasena,
    })
    localStorage.setItem(TOKEN_KEY, respuesta.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(respuesta.usuario))
    setToken(respuesta.access_token)
    setUsuario(respuesta.usuario)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      usuario,
      token,
      listo,
      esAdmin: usuario?.rol === 'admin',
      login,
      logout,
    }),
    [usuario, token, listo, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return ctx
}
