export type PuntoFirma = { x: number; y: number }

/** Trazo = puntos unidos; `|` separa trazos, `,` puntos, `_` las coordenadas x/y (con decimales). */
export function parsearFirma(firmaString: string | null | undefined): PuntoFirma[][] {
  const valor = firmaString?.trim()
  if (!valor) return []
  return valor.split('|').map((trazo) =>
    trazo
      .split(',')
      .map((punto) => {
        const partes = punto.split('_')
        return { x: Number.parseFloat(partes[0]), y: Number.parseFloat(partes[1]) }
      })
      .filter((punto) => !Number.isNaN(punto.x) && !Number.isNaN(punto.y)),
  )
}

export function tieneFirma(firmaString: string | null | undefined): boolean {
  return Boolean(firmaString?.trim())
}

export function dibujarFirma(canvas: HTMLCanvasElement, firmaString: string | null | undefined) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  if (!firmaString?.trim()) return

  const trazos = parsearFirma(firmaString)
  let minX = Infinity
  let minY = Infinity
  let maxX = 0
  let maxY = 0
  for (const trazo of trazos) {
    for (const punto of trazo) {
      if (punto.x < minX) minX = punto.x
      if (punto.y < minY) minY = punto.y
      if (punto.x > maxX) maxX = punto.x
      if (punto.y > maxY) maxY = punto.y
    }
  }
  if (!Number.isFinite(minX) || !Number.isFinite(minY)) return

  const anchoFirma = maxX - minX || 1
  const altoFirma = maxY - minY || 1
  const margen = 15
  const escalaX = (canvas.width - margen * 2) / anchoFirma
  const escalaY = (canvas.height - margen * 2) / altoFirma
  const escala = Math.min(escalaX, escalaY)
  const offsetX = (canvas.width - anchoFirma * escala) / 2
  const offsetY = (canvas.height - altoFirma * escala) / 2

  ctx.strokeStyle = '#000'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'

  for (const trazo of trazos) {
    if (trazo.length < 2) continue
    ctx.beginPath()
    ctx.moveTo((trazo[0].x - minX) * escala + offsetX, (trazo[0].y - minY) * escala + offsetY)
    for (let i = 1; i < trazo.length; i++) {
      ctx.lineTo((trazo[i].x - minX) * escala + offsetX, (trazo[i].y - minY) * escala + offsetY)
    }
    ctx.stroke()
  }
}
