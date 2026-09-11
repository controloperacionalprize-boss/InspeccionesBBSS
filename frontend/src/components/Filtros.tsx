import { useState } from 'react'
import { ChevronDown, RotateCcw, Search, SlidersHorizontal } from 'lucide-react'
import type { CatalogoItem, Fundo, TipoConsulta } from '../types/api'
import { contarFiltrosActivos, filtrosVacios, type Filtros } from '../hooks/useListado'
import { Field, Input, SegmentedControl, Select } from './Field'

type TipoFiltro = TipoConsulta | 'todos'

export function BarraFiltros({
  value,
  onChange,
  empresas,
  fundos,
  conDni = false,
}: {
  value: Filtros
  onChange: (next: Filtros) => void
  empresas: CatalogoItem[]
  fundos: Fundo[]
  conDni?: boolean
}) {
  const [abierto, setAbierto] = useState(false)
  const activos = contarFiltrosActivos(value)
  const fundosFiltrados = fundos.filter((f) => value.id_empresa === '' || f.ID_EMPRESA === value.id_empresa)
  const dniIncompleto = value.dni_trabajador !== '' && value.dni_trabajador.length < 8

  return (
    <div className="rounded-xl border border-line bg-white shadow-soft">
      <button
        type="button"
        onClick={() => setAbierto((a) => !a)}
        aria-expanded={abierto}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-semibold text-ink-soft md:hidden"
      >
        <span className="flex items-center gap-2">
          <SlidersHorizontal className="size-4" />
          Filtros
          {activos ? (
            <span className="rounded-full bg-brand-700 px-2 py-0.5 text-[11px] font-bold text-white">{activos}</span>
          ) : null}
        </span>
        <ChevronDown className={`size-4 transition-transform ${abierto ? 'rotate-180' : ''}`} />
      </button>

      <div className={`${abierto ? 'block' : 'hidden'} border-t border-line p-4 md:block md:border-0 md:p-5`}>
        <div
          className={`grid gap-3 sm:grid-cols-2 ${conDni ? 'xl:grid-cols-[repeat(5,minmax(0,1fr))]' : 'xl:grid-cols-4'}`}
        >
          <Field label="Empresa">
            <Select
              value={value.id_empresa}
              onChange={(e) => onChange({ ...value, id_empresa: Number(e.target.value) || '', id_fundo: '' })}
            >
              <option value="">Todas</option>
              {empresas.map((item) => (
                <option key={item.ID} value={item.ID}>
                  {item.NOMBRE}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Fundo">
            <Select
              value={value.id_fundo}
              onChange={(e) => onChange({ ...value, id_fundo: Number(e.target.value) || '' })}
            >
              <option value="">{value.id_empresa === '' ? 'Todos' : 'Todos los de la empresa'}</option>
              {fundosFiltrados.map((item) => (
                <option key={item.ID} value={item.ID}>
                  {item.NOMBRE}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Desde">
            <Input
              type="date"
              value={value.fecha_desde}
              max={value.fecha_hasta || undefined}
              onChange={(e) => onChange({ ...value, fecha_desde: e.target.value })}
            />
          </Field>
          <Field label="Hasta">
            <Input
              type="date"
              value={value.fecha_hasta}
              min={value.fecha_desde || undefined}
              onChange={(e) => onChange({ ...value, fecha_hasta: e.target.value })}
            />
          </Field>
          {conDni ? (
            <Field label="DNI del trabajador" hint={dniIncompleto ? 'Se filtra al completar los 8 dígitos' : undefined}>
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
                <Input
                  inputMode="numeric"
                  placeholder="8 dígitos"
                  className="pl-9"
                  value={value.dni_trabajador}
                  onChange={(e) =>
                    onChange({ ...value, dni_trabajador: e.target.value.replace(/\D/g, '').slice(0, 8) })
                  }
                />
              </div>
            </Field>
          ) : null}
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
          <div className="w-full sm:w-64">
            <SegmentedControl<TipoFiltro>
              etiqueta="Tipo de consulta"
              value={value.tipo_consulta || 'todos'}
              onChange={(tipo) => onChange({ ...value, tipo_consulta: tipo === 'todos' ? '' : tipo })}
              opciones={[
                { valor: 'todos', texto: 'Todos' },
                { valor: 'Campo', texto: 'Campo' },
                { valor: 'Packing', texto: 'Packing' },
              ]}
            />
          </div>
          {activos ? (
            <button
              type="button"
              onClick={() => onChange(filtrosVacios)}
              className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-muted hover:text-brand-700"
            >
              <RotateCcw className="size-3.5" />
              Limpiar filtros
            </button>
          ) : null}
        </div>
      </div>
    </div>
  )
}
