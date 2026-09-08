import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { useHealthApi } from '../hooks/useHealthApi'
import './HomePage.css'

export function HomePage() {
  const { loading, status, error } = useHealthApi()

  return (
    <div className="home">
      <section className="home__hero">
        <p className="home__label">Sistema operativo</p>
        <h1>Consultar Campo – Packing</h1>
        <p className="home__description">
          Base del proyecto lista para incorporar los módulos de Campo y Packing.
          Esta etapa incluye únicamente la estructura inicial.
        </p>
      </section>

      <div className="home__grid">
        <Card title="Campo">
          <p>Espacio preparado para consultas y operaciones de campo.</p>
        </Card>

        <Card title="Packing">
          <p>Espacio preparado para consultas y operaciones de packing.</p>
        </Card>

        <Card title="Estado del API">
          {loading && <p>Verificando conexión…</p>}
          {!loading && status && (
            <p className="home__status home__status--ok">
              API disponible · estado: {status}
            </p>
          )}
          {!loading && error && (
            <p className="home__status home__status--error">
              API no disponible todavía. Levanta el backend para verificar la conexión.
            </p>
          )}
        </Card>
      </div>

      <div className="home__actions">
        <Button variant="primary" disabled>
          Módulos próximamente
        </Button>
        <Button variant="secondary" disabled>
          Sin lógica de negocio aún
        </Button>
      </div>
    </div>
  )
}
