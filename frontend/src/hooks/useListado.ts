import { useCallback, useEffect, useState } from 'react'
import { api, esCancelacion } from '../services/apiClient'
import type { TipoConsulta } from '../types/api'

export interface Filtros {
  id_empresa: number | ''
  id_fundo: number | ''
  tipo_consulta: TipoConsulta | ''
  fecha_desde: string
  fecha_hasta: string
  dni_trabajador: string
}

export const filtrosVacios: Filtros = {
  id_empresa: '',
  id_fundo: '',
  tipo_consulta: '',
  fecha_desde: '',
  fecha_hasta: '',
  dni_trabajador: '',
}

export const TAMANOS_PAGINA = [10, 25, 50, 100] as const

export function contarFiltrosActivos(filtros: Filtros) {
  return (Object.keys(filtros) as (keyof Filtros)[]).filter((clave) => filtros[clave] !== filtrosVacios[clave]).length
}

function paramsFiltros(filtros: Filtros) {
  const params = new URLSearchParams()
  if (filtros.id_empresa !== '') params.set('id_empresa', String(filtros.id_empresa))
  if (filtros.id_fundo !== '') params.set('id_fundo', String(filtros.id_fundo))
  if (filtros.tipo_consulta) params.set('tipo_consulta', filtros.tipo_consulta)
  if (filtros.fecha_desde) params.set('fecha_desde', filtros.fecha_desde)
  if (filtros.fecha_hasta) params.set('fecha_hasta', filtros.fecha_hasta)
  // El backend filtra por DNI exacto: se aplica solo con los 8 dígitos completos.
  if (/^\d{8}$/.test(filtros.dni_trabajador)) params.set('dni_trabajador', filtros.dni_trabajador)
  return params
}

function aQuery(filtros: Filtros, skip: number, limit: number) {
  const params = paramsFiltros(filtros)
  params.set('skip', String(skip))
  params.set('limit', String(limit))
  return params.toString()
}

/** Mismos filtros del listado, sin paginación: para exportar todo lo filtrado. */
export function aQueryExportar(filtros: Filtros) {
  return paramsFiltros(filtros).toString()
}

function leerTamano(ruta: string) {
  try {
    const guardado = Number(localStorage.getItem(`filas_por_pagina:${ruta}`))
    return (TAMANOS_PAGINA as readonly number[]).includes(guardado) ? guardado : 10
  } catch {
    return 10
  }
}

function useRetrasado<T>(valor: T, ms: number) {
  const [retrasado, setRetrasado] = useState(valor)
  useEffect(() => {
    const id = setTimeout(() => setRetrasado(valor), ms)
    return () => clearTimeout(id)
  }, [valor, ms])
  return retrasado
}

export function useListado<T>(ruta: string, filtros: Filtros) {
  const [filas, setFilas] = useState<T[]>([])
  const [total, setTotal] = useState(0)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recargas, setRecargas] = useState(0)
  const [tamano, setTamanoEstado] = useState(() => leerTamano(ruta))

  // Cambiar un filtro vuelve a la página 1 sin una carga extra: la página va atada a los filtros.
  const claveFiltros = JSON.stringify(filtros)
  const [estadoPagina, setEstadoPagina] = useState({ claveFiltros, pagina: 0 })
  const pagina = estadoPagina.claveFiltros === claveFiltros ? estadoPagina.pagina : 0
  const setPagina = (nueva: number) => setEstadoPagina({ claveFiltros, pagina: nueva })

  const setTamano = (nuevo: number) => {
    setTamanoEstado(nuevo)
    setEstadoPagina({ claveFiltros, pagina: 0 })
    try {
      localStorage.setItem(`filas_por_pagina:${ruta}`, String(nuevo))
    } catch {
      /* almacenamiento no disponible: se usa solo en esta sesión */
    }
  }

  // Varios cambios seguidos (p. ej. empresa y luego fundo) se agrupan en una sola petición.
  const url = useRetrasado(`${ruta}?${aQuery(JSON.parse(claveFiltros) as Filtros, pagina * tamano, tamano)}`, 250)

  useEffect(() => {
    // Si llega una nueva consulta antes de que responda la anterior, la anterior se cancela:
    // no se gasta ancho de banda en ella ni puede pisar resultados más recientes.
    const control = new AbortController()
    setCargando(true)
    setError(null)
    api
      .getPaginado<T>(url, control.signal)
      .then(({ datos, total: cantidad }) => {
        setFilas(datos)
        setTotal(cantidad)
      })
      .catch((err: unknown) => {
        if (!esCancelacion(err)) setError(err instanceof Error ? err.message : 'No se pudieron cargar los registros')
      })
      .finally(() => {
        if (!control.signal.aborted) setCargando(false)
      })
    return () => control.abort()
  }, [url, recargas])

  // Si se borró el último registro de la última página, se retrocede a la anterior.
  const paginas = Math.max(1, Math.ceil(total / tamano))
  useEffect(() => {
    if (!cargando && pagina > 0 && pagina >= paginas) setEstadoPagina({ claveFiltros, pagina: paginas - 1 })
  }, [cargando, pagina, paginas, claveFiltros])

  const recargar = useCallback(() => setRecargas((n) => n + 1), [])

  return { filas, total, pagina, paginas, setPagina, tamano, setTamano, cargando, error, recargar }
}
