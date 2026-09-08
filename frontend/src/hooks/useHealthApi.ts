import { useEffect, useState } from 'react'
import { getHealth } from '../services/healthService'

interface HealthState {
  loading: boolean
  status: string | null
  error: string | null
}

export function useHealthApi(): HealthState {
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    getHealth()
      .then((data) => {
        if (active) {
          setStatus(data.status)
          setError(null)
        }
      })
      .catch((err: unknown) => {
        if (active) {
          setStatus(null)
          setError(err instanceof Error ? err.message : 'No se pudo consultar el API')
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [])

  return { loading, status, error }
}
