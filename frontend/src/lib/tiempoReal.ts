import { invalidar } from './cache'
import { TOKEN_KEY } from '../services/apiClient'

const EVENTO = 'consultar-campo:tiempo-real'
const PING_MS = 25_000
const BACKEND_WS_DEV = 'ws://127.0.0.1:8001/api/ws'

export function onTiempoReal(alAviso: (recurso: string) => void) {
  const escuchar = (evento: Event) => {
    const recurso = (evento as CustomEvent<{ recurso?: string }>).detail?.recurso
    if (recurso) alAviso(recurso)
  }
  window.addEventListener(EVENTO, escuchar)
  return () => window.removeEventListener(EVENTO, escuchar)
}

function urlWebSocket() {
  const api = import.meta.env.VITE_API_URL ?? '/api'
  if (api.startsWith('http://') || api.startsWith('https://')) {
    return `${api.replace(/^http/, 'ws')}/ws`
  }
  // En Vite el proxy WS de /api se cae con 1006 antes de enviar el JWT.
  if (import.meta.env.DEV) return BACKEND_WS_DEV
  const protocolo = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocolo}//${window.location.host}${api}/ws`
}

/** Conecta el canal; se cierra al hacer logout o desmontar. Reintenta si se cae. */
export function conectarTiempoReal(token: string) {
  let cerrado = false
  let socket: WebSocket | null = null
  let ping: number | undefined
  let reintento: number | undefined
  let espera = 1000

  const emitir = (recurso: string) => {
    if (recurso === 'catalogos') invalidar('catalogos')
    if (recurso === 'inspecciones' || recurso === 'consultas' || recurso === 'indumentaria') {
      invalidar('resumen')
    }
    window.dispatchEvent(new CustomEvent(EVENTO, { detail: { recurso } }))
  }

  const detenerPing = () => {
    if (ping) window.clearInterval(ping)
    ping = undefined
  }

  const abrir = () => {
    if (cerrado || localStorage.getItem(TOKEN_KEY) !== token) return
    socket = new WebSocket(urlWebSocket())

    socket.onopen = () => {
      if (cerrado) {
        socket?.close(1000)
        return
      }
      socket?.send(token)
      espera = 1000
      detenerPing()
      ping = window.setInterval(() => {
        if (socket?.readyState === WebSocket.OPEN) socket.send('ping')
      }, PING_MS)
    }

    socket.onmessage = (evento) => {
      try {
        const cuerpo = JSON.parse(evento.data) as { recurso?: string }
        if (cuerpo.recurso) emitir(cuerpo.recurso)
      } catch {
        /* mensaje no JSON */
      }
    }

    socket.onclose = (evento) => {
      detenerPing()
      socket = null
      if (cerrado || evento.code === 4401) return
      reintento = window.setTimeout(abrir, espera)
      espera = Math.min(espera * 2, 15_000)
    }
  }

  abrir()

  return () => {
    cerrado = true
    detenerPing()
    if (reintento) window.clearTimeout(reintento)
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      socket.close(1000)
    }
  }
}
