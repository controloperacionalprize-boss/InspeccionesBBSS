const dos = (n: number) => String(n).padStart(2, '0')

function aIso(fecha: Date) {
  return `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}`
}

// Fecha local: toISOString() usa UTC y en Perú (UTC-5) adelanta el día desde las 19:00.
export function hoyIso() {
  return aIso(new Date())
}

export function inicioMesIso() {
  const hoy = new Date()
  return aIso(new Date(hoy.getFullYear(), hoy.getMonth(), 1))
}

const formato = new Intl.DateTimeFormat('es-PE', { day: 'numeric', month: 'short', year: 'numeric' })

// Una fecha pura ("2026-09-10") se arma en hora local: pasada directo a Date sería medianoche UTC
// y en Perú mostraría el día anterior. Un timestamp con hora sí trae zona y se convierte a local.
export function formatFecha(iso: string | null | undefined) {
  if (!iso) return '—'
  if (iso.length > 10) {
    const instante = new Date(iso)
    return Number.isNaN(instante.getTime()) ? iso : formato.format(instante).replace('.', '')
  }
  const [anio, mes, dia] = iso.split('-').map(Number)
  if (!anio || !mes || !dia) return iso
  return formato.format(new Date(anio, mes - 1, dia)).replace('.', '')
}
