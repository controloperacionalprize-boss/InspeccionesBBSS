const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`)

  if (!response.ok) {
    throw new Error(`Request error: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export { API_URL }
