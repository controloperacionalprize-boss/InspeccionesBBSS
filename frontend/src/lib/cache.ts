// Caché en memoria para lecturas que cambian poco (catálogos, resumen, lookups de DNI).
// - Deduplica: si dos componentes (o StrictMode) piden lo mismo a la vez, sale una sola petición.
// - Expira por TTL y se invalida explícitamente tras cada escritura relacionada.
// - Vive solo en memoria: se vacía al cerrar sesión o recargar la pestaña.

interface Entrada {
  datos?: unknown
  expira: number
  enVuelo?: Promise<unknown>
}

const almacen = new Map<string, Entrada>()

export function leerCache<T>(clave: string): T | undefined {
  const entrada = almacen.get(clave)
  return entrada && 'datos' in entrada && entrada.expira > Date.now() ? (entrada.datos as T) : undefined
}

export function cacheado<T>(clave: string, ttlMs: number, cargar: () => Promise<T>): Promise<T> {
  const entrada = almacen.get(clave)
  if (entrada?.enVuelo) return entrada.enVuelo as Promise<T>
  const vigente = leerCache<T>(clave)
  if (vigente !== undefined) return Promise.resolve(vigente)

  const enVuelo = cargar().then(
    (datos) => {
      almacen.set(clave, { datos, expira: Date.now() + ttlMs })
      return datos
    },
    (error: unknown) => {
      almacen.delete(clave)
      throw error
    },
  )
  almacen.set(clave, { ...entrada, expira: entrada?.expira ?? 0, enVuelo })
  return enVuelo
}

export function invalidar(prefijo: string) {
  for (const clave of almacen.keys()) {
    if (clave.startsWith(prefijo)) almacen.delete(clave)
  }
}

export function limpiarCache() {
  almacen.clear()
}
