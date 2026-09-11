import type { CatalogoItem, TipoConsulta } from '../types/api'

export function tipoConsultaSegunDivision(nombre: string | undefined | null): TipoConsulta {
  return (nombre ?? '').toLowerCase().includes('packing') ? 'Packing' : 'Campo'
}

export function tipoConsultaDesdeDivision(
  divisiones: CatalogoItem[],
  idDivision: number | '',
): TipoConsulta | '' {
  if (idDivision === '') return ''
  const division = divisiones.find((item) => item.ID === idDivision)
  return division ? tipoConsultaSegunDivision(division.NOMBRE) : ''
}

/** En listados: PACKING en la división manda sobre el valor guardado. */
export function tipoVisible(nombreDivision: string | undefined, guardado: TipoConsulta | null): TipoConsulta | null {
  return nombreDivision ? tipoConsultaSegunDivision(nombreDivision) : guardado
}
