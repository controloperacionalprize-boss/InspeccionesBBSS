import type { HealthResponse } from '../types/api'

/**
 * Calls the backend health endpoint at /health.
 * VITE_API_URL points to /api; the server base URL is derived from it.
 */
export function getHealth(): Promise<HealthResponse> {
  const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
  const baseUrl = apiUrl.replace(/\/api\/?$/, '')

  return fetch(`${baseUrl}/health`).then(async (response) => {
    if (!response.ok) {
      throw new Error(`Request error: ${response.status}`)
    }
    return response.json() as Promise<HealthResponse>
  })
}
