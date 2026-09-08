import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'
import './MainLayout.css'

interface MainLayoutProps {
  children: ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="layout">
      <header className="layout__header">
        <div className="layout__header-content">
          <Link to="/" className="layout__brand">
            Consultar Campo – Packing
          </Link>
          <nav className="layout__nav" aria-label="Navegación principal">
            <Link to="/">Inicio</Link>
          </nav>
        </div>
      </header>

      <main className="layout__content">{children}</main>

      <footer className="layout__footer">
        <p>Consultar Campo – Packing · Base del proyecto</p>
      </footer>
    </div>
  )
}
