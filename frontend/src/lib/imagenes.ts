const LADO_MAXIMO = 1920
const CALIDAD = 0.82
// Por debajo de este tamaño y resolución, la foto se sube tal cual.
const UMBRAL_BYTES = 600 * 1024

// Reduce fotos de cámara (4–8 MB) a ~300–600 KB antes de subirlas: menos datos móviles
// en campo, menos almacenamiento y descargas más rápidas al revisar la inspección.
export async function optimizarFoto(archivo: File): Promise<File> {
  if (typeof createImageBitmap !== 'function') return archivo
  let imagen: ImageBitmap
  try {
    imagen = await createImageBitmap(archivo, { imageOrientation: 'from-image' })
  } catch {
    return archivo
  }
  const escala = Math.min(1, LADO_MAXIMO / Math.max(imagen.width, imagen.height))
  if (escala === 1 && archivo.size <= UMBRAL_BYTES) {
    imagen.close()
    return archivo
  }

  const lienzo = document.createElement('canvas')
  lienzo.width = Math.round(imagen.width * escala)
  lienzo.height = Math.round(imagen.height * escala)
  const contexto = lienzo.getContext('2d')
  if (!contexto) {
    imagen.close()
    return archivo
  }
  contexto.drawImage(imagen, 0, 0, lienzo.width, lienzo.height)
  imagen.close()

  const blob = await new Promise<Blob | null>((resolver) => lienzo.toBlob(resolver, 'image/jpeg', CALIDAD))
  if (!blob || blob.size >= archivo.size) return archivo
  const nombre = archivo.name.replace(/\.[^.]+$/, '') + '.jpg'
  return new File([blob], nombre, { type: 'image/jpeg', lastModified: archivo.lastModified })
}
