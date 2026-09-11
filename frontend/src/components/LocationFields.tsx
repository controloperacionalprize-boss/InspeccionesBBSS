import { TipoBadge } from './Feedback'
import { Field, Select } from './Field'
import { tipoConsultaDesdeDivision } from '../lib/tipoConsulta'
import type { Area, CatalogoItem, Fundo, Subcategoria } from '../types/api'

interface LocationValue {
  ID_EMPRESA: number | ''
  ID_FUNDO: number | ''
  ID_DIVISION: number | ''
  ID_AREA: number | ''
}

export function LocationFields({
  value,
  onChange,
  empresas,
  fundos,
  divisiones,
  areas,
}: {
  value: LocationValue
  onChange: (next: LocationValue) => void
  empresas: CatalogoItem[]
  fundos: Fundo[]
  divisiones: CatalogoItem[]
  areas: Area[]
}) {
  const fundosFiltrados = fundos.filter((item) => item.ID_EMPRESA === value.ID_EMPRESA)
  const areasFiltradas = areas.filter((item) => item.ID_DIVISION === value.ID_DIVISION)
  const tipo = tipoConsultaDesdeDivision(divisiones, value.ID_DIVISION)

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Field label="Empresa">
        <Select
          required
          value={value.ID_EMPRESA}
          onChange={(e) =>
            onChange({ ...value, ID_EMPRESA: Number(e.target.value) || '', ID_FUNDO: '' })
          }
        >
          <option value="">Seleccione</option>
          {empresas.map((item) => (
            <option key={item.ID} value={item.ID}>
              {item.NOMBRE}
            </option>
          ))}
        </Select>
      </Field>
      <Field label="Fundo">
        <Select
          required
          disabled={value.ID_EMPRESA === ''}
          value={value.ID_FUNDO}
          onChange={(e) => onChange({ ...value, ID_FUNDO: Number(e.target.value) || '' })}
        >
          <option value="">{value.ID_EMPRESA === '' ? 'Elija una empresa primero' : 'Seleccione'}</option>
          {fundosFiltrados.map((item) => (
            <option key={item.ID} value={item.ID}>
              {item.NOMBRE}
            </option>
          ))}
        </Select>
      </Field>
      <Field label="División">
        <Select
          required
          value={value.ID_DIVISION}
          onChange={(e) =>
            onChange({ ...value, ID_DIVISION: Number(e.target.value) || '', ID_AREA: '' })
          }
        >
          <option value="">Seleccione</option>
          {divisiones.map((item) => (
            <option key={item.ID} value={item.ID}>
              {item.NOMBRE}
            </option>
          ))}
        </Select>
      </Field>
      <Field label="Área">
        <Select
          required
          disabled={value.ID_DIVISION === ''}
          value={value.ID_AREA}
          onChange={(e) => onChange({ ...value, ID_AREA: Number(e.target.value) || '' })}
        >
          <option value="">{value.ID_DIVISION === '' ? 'Elija una división primero' : 'Seleccione'}</option>
          {areasFiltradas.map((item) => (
            <option key={item.ID} value={item.ID}>
              {item.NOMBRE}
            </option>
          ))}
        </Select>
      </Field>
      {tipo ? (
        <div className="flex items-center gap-2 sm:col-span-2">
          <span className="text-[13px] font-semibold text-ink-soft">Tipo</span>
          <TipoBadge tipo={tipo} />
          <span className="text-xs text-muted">Según la división: Packing o Campo</span>
        </div>
      ) : null}
    </div>
  )
}

export function CategoriaFields({
  idCategoria,
  idSubcategoria,
  categorias,
  subcategorias,
  onChange,
}: {
  idCategoria: number | ''
  idSubcategoria: number | ''
  categorias: CatalogoItem[]
  subcategorias: Subcategoria[]
  onChange: (categoria: number | '', subcategoria: number | '') => void
}) {
  const filtradas = subcategorias.filter((item) => item.ID_CATEGORIA === idCategoria)
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <Field label="Categoría">
        <Select
          required
          value={idCategoria}
          onChange={(e) => onChange(Number(e.target.value) || '', '')}
        >
          <option value="">Seleccione</option>
          {categorias.map((item) => (
            <option key={item.ID} value={item.ID}>
              {item.NOMBRE}
            </option>
          ))}
        </Select>
      </Field>
      <Field label="Subcategoría">
        <Select
          required
          disabled={idCategoria === ''}
          value={idSubcategoria}
          onChange={(e) => onChange(idCategoria, Number(e.target.value) || '')}
        >
          <option value="">{idCategoria === '' ? 'Elija una categoría primero' : 'Seleccione'}</option>
          {filtradas.map((item) => (
            <option key={item.ID} value={item.ID}>
              {item.NOMBRE}
            </option>
          ))}
        </Select>
      </Field>
    </div>
  )
}
