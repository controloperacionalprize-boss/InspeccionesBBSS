import { useLayoutEffect, useRef } from 'react'
import { dibujarFirma, tieneFirma } from '../lib/firma'

const ANCHO = 400
const ALTO = 200

export function FirmaCanvas({ valor }: { valor: string | null | undefined }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const hayFirma = tieneFirma(valor)

  useLayoutEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !hayFirma) return
    dibujarFirma(canvas, valor)
  }, [valor, hayFirma])

  return (
    <div className="space-y-1.5 sm:col-span-2">
      <span className="text-[13px] font-semibold text-ink-soft">Firma</span>
      {hayFirma ? (
        <canvas
          ref={canvasRef}
          width={ANCHO}
          height={ALTO}
          className="h-auto w-full max-w-[400px] rounded-lg border border-line bg-white"
          aria-label="Firma del trabajador"
        />
      ) : (
        <div
          className="flex aspect-[2/1] w-full max-w-[400px] items-center justify-center rounded-lg border border-dashed border-line bg-sand text-sm text-muted"
          role="status"
        >
          Sin firma
        </div>
      )}
    </div>
  )
}
