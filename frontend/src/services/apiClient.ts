import { invalidar } from '../lib/cache'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export const TOKEN_KEY = 'consultar_campo_token'
export const USER_KEY = 'consultar_campo_usuario'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export function esCancelacion(err: unknown) {
  return err instanceof DOMException && err.name === 'AbortError'
}

let onUnauthorized: (() => void) | null = null

export function setOnUnauthorized(handler: (() => void) | null) {
  onUnauthorized = handler
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string }
    if (body.detail) return body.detail
  } catch {
    /* respuesta no JSON */
  }
  if (response.status === 401) return 'Sesión vencida o credenciales inválidas'
  if (response.status === 403) return 'No tiene permiso para esta operación'
  if (response.status === 404) return 'No encontrado'
  if (response.status === 429) return 'Demasiadas solicitudes seguidas. Espere un momento e intente de nuevo.'
  return `Error ${response.status}`
}

// Tras escribir, se descartan las lecturas cacheadas que esa escritura deja desactualizadas.
const CATALOGOS = /^\/(empresas|fundos|divisiones|areas|categorias|subcategorias)(\/|$)/
const REGISTROS = /^\/(inspecciones|consultas|indumentaria|fotos)(\/|$)/

function invalidarTrasEscritura(path: string) {
  if (CATALOGOS.test(path)) invalidar('catalogos')
  if (REGISTROS.test(path)) invalidar('resumen')
}

async function ejecutar(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body !== undefined && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${API_URL}${path}`, { ...init, headers })

  if (response.status === 401 && !path.startsWith('/auth/login')) {
    onUnauthorized?.()
  }
  if (!response.ok) {
    throw new ApiError(response.status, await parseError(response))
  }
  if (init.method && init.method !== 'GET') invalidarTrasEscritura(path)
  return response
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await ejecutar(path, init)
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export const api = {
  get: <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),
  /** Listado paginado: el backend informa el total filtrado en la cabecera X-Total-Count. */
  getPaginado: async <T>(path: string, signal?: AbortSignal) => {
    const response = await ejecutar(path, { signal })
    const datos = (await response.json()) as T[]
    const total = Number(response.headers.get('X-Total-Count'))
    return { datos, total: Number.isFinite(total) ? total : datos.length }
  },
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    }),
  put: <T>(path: string, body: unknown) => request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (path: string) => request<void>(path, { method: 'DELETE' }),
  /** Descarga un archivo (p. ej. exportación a Excel) y dispara la descarga en el navegador. */
  descargar: async (path: string, nombreSugerido: string) => {
    const response = await ejecutar(path)
    const blob = await response.blob()
    const disposicion = response.headers.get('Content-Disposition')
    const coincidencia = disposicion?.match(/filename="?([^";]+)"?/)
    const nombre = coincidencia?.[1] ?? nombreSugerido

    const url = URL.createObjectURL(blob)
    const enlace = document.createElement('a')
    enlace.href = url
    enlace.download = nombre
    document.body.appendChild(enlace)
    enlace.click()
    enlace.remove()
    URL.revokeObjectURL(url)
  },
}

export { API_URL }
