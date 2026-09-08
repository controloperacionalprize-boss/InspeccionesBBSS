import type { ReactNode } from 'react'
import './Card.css'

interface CardProps {
  title: string
  children: ReactNode
}

export function Card({ title, children }: CardProps) {
  return (
    <section className="card">
      <h2 className="card__title">{title}</h2>
      <div className="card__content">{children}</div>
    </section>
  )
}
