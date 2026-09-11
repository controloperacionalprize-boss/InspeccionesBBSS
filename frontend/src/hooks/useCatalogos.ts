import { useCallback, useEffect, useMemo, useState } from 'react'
import { cacheado, invalidar, leerCache } from '../lib/cache'
import { api } from '../services/apiClient'
import type { Area, CatalogoItem, Fundo, Subcategoria } from '../types/api'

interface Catalogos {
  empresas: CatalogoItem[]
  fundos: Fundo[]
  divisiones: CatalogoItem[]
  areas: Area[]
  categorias: CatalogoItem[]
  subcategorias: Subcategoria[]
}

const CLAVE = 'catalogos'
// Cambian muy poco; toda escritura en catálogos invalida la caché (ver apiClient).
const TTL = 10 * 60 * 1000

const cargarCatalogos = () => cacheado(CLAVE, TTL, () => api.get<Catalogos>('/catalogos'))

const vacios: Catalogos = { empresas: [], fundos: [], divisiones: [], areas: [], categorias: [], subcategorias: [] }

export function useCatalogos() {
  const [datos, setDatos] = useState<Catalogos | undefined>(() => leerCache<Catalogos>(CLAVE))
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let vigente = true
    cargarCatalogos()
      .then((respuesta) => vigente && setDatos(respuesta))
      .catch((err: Error) => vigente && setError(err.message || 'No se pudieron cargar los catálogos'))
    return () => {
      vigente = false
    }
  }, [])

  const recargar = useCallback(async () => {
    invalidar(CLAVE)
    setError(null)
    try {
      setDatos(await cargarCatalogos())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los catálogos')
    }
  }, [])

  const actual = datos ?? vacios
  const nombre = useMemo(() => {
    const mapa = (items: CatalogoItem[]) =>
      Object.fromEntries(items.map((item) => [item.ID, item.NOMBRE])) as Record<number, string>
    return {
      empresa: mapa(actual.empresas),
      fundo: mapa(actual.fundos),
      division: mapa(actual.divisiones),
      area: mapa(actual.areas),
      categoria: mapa(actual.categorias),
      subcategoria: mapa(actual.subcategorias),
    }
  }, [actual])

  return { ...actual, nombre, cargando: !datos && !error, error, recargar }
}
