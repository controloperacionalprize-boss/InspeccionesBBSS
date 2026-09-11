import { useEffect, useMemo, useRef, useState, type DragEvent } from 'react'
import { Camera, Loader2, X } from 'lucide-react'
import type { Foto } from '../types/api'
import { optimizarFoto } from '../lib/imagenes'

const TIPOS = ['image/jpeg', 'image/png', 'image/webp']
const MAX_BYTES = 8 * 1024 * 1024
export const MAX_POR_SUBIDA = 10

export function PhotoUploader({
  existentes,
  pendientes,
  onPendientes,
  onQuitarExistente,
}: {
  existentes: Foto[]
  pendientes: File[]
  onPendientes: (archivos: File[]) => void
  onQuitarExistente: (id: number) => void
}) {
  const input = useRef<HTMLInputElement>(null)
  const [arrastrando, setArrastrando] = useState(false)
  const [procesando, setProcesando] = useState(false)
  const [rechazos, setRechazos] = useState<string[]>([])

  const previas = useMemo(() => pendientes.map((archivo) => URL.createObjectURL(archivo)), [pendientes])
  useEffect(() => () => previas.forEach((url) => URL.revokeObjectURL(url)), [previas])

  const agregar = async (lista: FileList | null) => {
    if (!lista?.length) return
    const motivos: string[] = []
    const candidatos = Array.from(lista).filter((archivo) => {
      if (TIPOS.includes(archivo.type)) return true
      motivos.push(`${archivo.name}: solo JPG, PNG o WEBP`)
      return false
    })
    const espacio = MAX_POR_SUBIDA - pendientes.length
    if (candidatos.length > espacio) motivos.push(`Máximo ${MAX_POR_SUBIDA} fotos por guardado`)

    setProcesando(true)
    const optimizados = await Promise.all(candidatos.slice(0, Math.max(espacio, 0)).map(optimizarFoto))
    setProcesando(false)

    const aceptados = optimizados.filter((archivo) => {
      if (archivo.size <= MAX_BYTES) return true
      motivos.push(`${archivo.name}: supera 8 MB`)
      return false
    })
    setRechazos(motivos)
    onPendientes([...pendientes, ...aceptados])
  }

  const soltar = (evento: DragEvent) => {
    evento.preventDefault()
    setArrastrando(false)
    void agregar(evento.dataTransfer.files)
  }

  const quitarPendiente = (indice: number) => onPendientes(pendientes.filter((_, i) => i !== indice))

  const miniatura = 'relative aspect-square overflow-hidden rounded-lg border border-line bg-sand'
  const botonQuitar =
    'absolute right-1.5 top-1.5 flex size-7 items-center justify-center rounded-full bg-slate-900/60 text-white transition-colors hover:bg-red-600'

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-5">
        {existentes.map((foto) => (
          <figure key={foto.ID} className={miniatura}>
            <a href={foto.URL} target="_blank" rel="noreferrer" title="Abrir en tamaño completo">
              <img
                src={foto.URL}
                alt="Evidencia"
                className="size-full object-cover"
                loading="lazy"
                decoding="async"
              />
            </a>
            <button
              type="button"
              className={botonQuitar}
              onClick={() => onQuitarExistente(foto.ID)}
              aria-label="Quitar foto"
              title="Quitar foto"
            >
              <X className="size-3.5" />
            </button>
          </figure>
        ))}
        {previas.map((url, indice) => (
          <figure key={url} className={`${miniatura} ring-2 ring-brand-300 ring-offset-1`}>
            <img src={url} alt={pendientes[indice]?.name ?? ''} className="size-full object-cover" />
            <span className="absolute inset-x-0 bottom-0 bg-brand-900/70 px-2 py-1 text-center text-[11px] font-semibold text-white">
              Por subir
            </span>
            <button
              type="button"
              className={botonQuitar}
              onClick={() => quitarPendiente(indice)}
              aria-label="Descartar foto"
              title="Descartar"
            >
              <X className="size-3.5" />
            </button>
          </figure>
        ))}
        {pendientes.length < MAX_POR_SUBIDA ? (
          <button
            type="button"
            disabled={procesando}
            onClick={() => input.current?.click()}
            onDragOver={(e) => {
              e.preventDefault()
              setArrastrando(true)
            }}
            onDragLeave={() => setArrastrando(false)}
            onDrop={soltar}
            className={`col-span-3 flex min-h-28 flex-col items-center justify-center gap-1.5 rounded-lg border-2 border-dashed px-3 text-center transition-colors disabled:cursor-wait sm:col-span-2 ${
              arrastrando ? 'border-brand-500 bg-brand-100' : 'border-brand-200 bg-brand-50 hover:border-brand-400'
            }`}
          >
            {procesando ? (
              <Loader2 className="size-5 animate-spin text-brand-700" />
            ) : (
              <Camera className="size-5 text-brand-700" />
            )}
            <span className="text-[13px] font-semibold text-brand-700">
              {procesando ? 'Optimizando fotos…' : 'Arrastre o elija fotos'}
            </span>
            <span className="text-[11.5px] text-muted">JPG, PNG o WEBP · se optimizan antes de subir</span>
          </button>
        ) : null}
      </div>
      <input
        ref={input}
        type="file"
        accept={TIPOS.join(',')}
        multiple
        hidden
        onChange={(e) => {
          void agregar(e.target.files)
          e.target.value = ''
        }}
      />
      {rechazos.length ? (
        <ul className="space-y-0.5 text-xs text-amber-700">
          {rechazos.map((motivo) => (
            <li key={motivo}>{motivo}</li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
