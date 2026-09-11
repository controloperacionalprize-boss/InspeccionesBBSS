export type Rol = 'admin' | 'inspector'
export type TipoConsulta = 'Campo' | 'Packing'

export interface Usuario {
  id: number
  nombre: string
  apellido: string
  usuario: string
  rol: Rol
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: Usuario
}

export interface CatalogoItem {
  ID: number
  NOMBRE: string
}

export interface Fundo extends CatalogoItem {
  ID_EMPRESA: number
}

export interface Area extends CatalogoItem {
  ID_DIVISION: number
}

export interface Subcategoria extends CatalogoItem {
  ID_CATEGORIA: number
}

export interface Inspeccion {
  ID: number
  ID_EMPRESA: number
  ID_FUNDO: number
  ID_DIVISION: number
  ID_AREA: number
  FECHA_OBSERVACION: string
  RANGO_HORA: string | null
  ID_CATEGORIA: number
  ID_SUBCATEGORIA: number
  DESCRIPCION: string
  ACCION_CORRECTIVA: string | null
  PLAZO_LEVANTAMIENTO: string | null
  TIPO_CONSULTA: TipoConsulta | null
  ELIMINADO: boolean
  FECHA_ELIMINACION: string | null
}

export interface Consulta {
  ID: number
  ID_EMPRESA: number
  ID_FUNDO: number
  ID_DIVISION: number
  ID_AREA: number
  FECHA_CONSULTA: string
  DNI_TRABAJADOR: string
  APELLIDOS_NOMBRES: string
  DESCRIPCION: string
  AREA_RESPONSABLE: string
  RESPUESTA_INMEDIATA: string | null
  RESPUESTA_POSTERIOR: string | null
  TIPO_CONSULTA: TipoConsulta | null
  ELIMINADO: boolean
  FECHA_ELIMINACION: string | null
}

export interface Indumentaria {
  ID: number
  ID_EMPRESA: number
  ID_FUNDO: number
  ID_DIVISION: number
  ID_AREA: number
  DNI_TRABAJADOR: string
  APELLIDOS_NOMBRES: string
  FECHA_ENTREGA: string
  CANTIDAD: number
  TIPO: string
  FIRMA: string | null
  RESPONSABLE_REGISTRO: string
  TIPO_CONSULTA: TipoConsulta | null
  ELIMINADO: boolean
  FECHA_ELIMINACION: string | null
}

export interface Foto {
  ID: number
  URL: string
  ORDEN: number
  FECHA_SUBIDA: string
}

export interface Trabajador {
  DNI: string
  APELLIDOS_NOMBRES: string
  EMPRESA: string | null
  CARGO: string | null
  VIGENTE: boolean | null
}

export interface UsuarioAdmin {
  id: number
  nombre: string
  apellido: string
  usuario: string
  rol: Rol
  dni: string | null
}

export interface Resumen {
  inspecciones: number
  inspecciones_por_tipo: { campo: number; packing: number; sin_tipo: number }
  inspecciones_sin_accion: number
  consultas_por_responder: number
  entregas: number
  unidades_entregadas: number
}
