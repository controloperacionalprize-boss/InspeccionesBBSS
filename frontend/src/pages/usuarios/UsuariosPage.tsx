import { useEffect, useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { Pencil, ShieldCheck, UserRound } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { Page } from '../../components/AppShell'
import { Button, IconButton } from '../../components/Button'
import { Alert, EmptyState, Notice, Pill } from '../../components/Feedback'
import { Field, Input, SegmentedControl } from '../../components/Field'
import { Card, Table, Td, Th } from '../../components/Surface'
import { api } from '../../services/apiClient'
import type { Rol, UsuarioAdmin } from '../../types/api'

interface Formulario {
  nombre: string
  apellido: string
  usuario: string
  contrasena: string
  rol: Rol
  dni: string
}

const vacio: Formulario = {
  nombre: '',
  apellido: '',
  usuario: '',
  contrasena: '',
  rol: 'inspector',
  dni: '',
}

export function UsuariosPage() {
  const { esAdmin, usuario: actual } = useAuth()
  const [filas, setFilas] = useState<UsuarioAdmin[]>([])
  const [cargando, setCargando] = useState(true)
  const [form, setForm] = useState<Formulario>(vacio)
  const [editando, setEditando] = useState<UsuarioAdmin | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  const cargar = async () => {
    setFilas(await api.get<UsuarioAdmin[]>('/usuarios'))
  }

  useEffect(() => {
    if (!esAdmin) return
    cargar()
      .catch((err: Error) => setError(err.message))
      .finally(() => setCargando(false))
  }, [esAdmin])

  if (!esAdmin) return <Navigate to="/" replace />

  const cancelar = () => {
    setEditando(null)
    setForm(vacio)
  }

  const enviar = async (evento: FormEvent) => {
    evento.preventDefault()
    setError(null)
    setAviso(null)
    setEnviando(true)
    try {
      if (editando) {
        await api.put(`/usuarios/${editando.id}`, {
          nombre: form.nombre,
          apellido: form.apellido,
          rol: form.rol,
          dni: form.dni || null,
          contrasena: form.contrasena || null,
        })
        setAviso(`Se actualizó a ${form.nombre} ${form.apellido}.`)
      } else {
        await api.post('/usuarios', {
          nombre: form.nombre,
          apellido: form.apellido,
          usuario: form.usuario,
          contrasena: form.contrasena,
          rol: form.rol,
          dni: form.dni || null,
        })
        setAviso(`Se creó el usuario “${form.usuario}”.`)
      }
      cancelar()
      await cargar()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar el usuario')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Page titulo="Usuarios" descripcion="Alta y edición de inspectores y administradores.">
      <div className="space-y-4">
        {error ? <Alert mensaje={error} /> : null}
        {aviso ? <Notice tono="success">{aviso}</Notice> : null}

        <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,22rem)_minmax(0,1fr)]">
          <Card
            titulo={editando ? `Editar a ${editando.nombre}` : 'Nuevo usuario'}
            descripcion={editando ? `Usuario: ${editando.usuario}` : 'El usuario no se puede cambiar después.'}
            className="xl:sticky xl:top-24"
          >
            <form onSubmit={(e) => void enviar(e)} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Nombre">
                  <Input
                    required
                    maxLength={70}
                    value={form.nombre}
                    onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  />
                </Field>
                <Field label="Apellido">
                  <Input
                    required
                    maxLength={70}
                    value={form.apellido}
                    onChange={(e) => setForm({ ...form, apellido: e.target.value })}
                  />
                </Field>
              </div>
              {!editando ? (
                <Field label="Usuario">
                  <Input
                    required
                    autoComplete="off"
                    value={form.usuario}
                    onChange={(e) => setForm({ ...form, usuario: e.target.value })}
                  />
                </Field>
              ) : null}
              <Field
                label={editando ? 'Nueva contraseña' : 'Contraseña'}
                hint={editando ? 'Déjela vacía para mantener la actual.' : 'Mínimo 8 caracteres.'}
              >
                <Input
                  type="password"
                  autoComplete="new-password"
                  required={!editando}
                  minLength={8}
                  value={form.contrasena}
                  onChange={(e) => setForm({ ...form, contrasena: e.target.value })}
                />
              </Field>
              <Field label="DNI (opcional)">
                <Input
                  inputMode="numeric"
                  maxLength={20}
                  value={form.dni}
                  onChange={(e) => setForm({ ...form, dni: e.target.value })}
                />
              </Field>
              <div className="space-y-1.5">
                <span className="text-[13px] font-semibold text-ink-soft">Rol</span>
                <SegmentedControl<Rol>
                  etiqueta="Rol"
                  value={form.rol}
                  onChange={(rol) => setForm({ ...form, rol })}
                  opciones={[
                    { valor: 'inspector', texto: 'Inspector' },
                    { valor: 'admin', texto: 'Administrador' },
                  ]}
                />
              </div>
              <div className="flex gap-2 pt-1">
                <Button type="submit" loading={enviando} className="flex-1">
                  {editando ? 'Guardar cambios' : 'Crear usuario'}
                </Button>
                {editando ? (
                  <Button variant="secondary" onClick={cancelar}>
                    Cancelar
                  </Button>
                ) : null}
              </div>
            </form>
          </Card>

          <div className="overflow-hidden rounded-xl border border-line bg-white shadow-soft">
            {!cargando && !filas.length ? (
              <EmptyState titulo="Sin usuarios" detalle="Cree el primero con el formulario." />
            ) : (
              <Table>
                <thead>
                  <tr>
                    <Th>Persona</Th>
                    <Th className="hidden sm:table-cell">Usuario</Th>
                    <Th>Rol</Th>
                    <Th className="text-right">
                      <span className="sr-only">Acciones</span>
                    </Th>
                  </tr>
                </thead>
                <tbody>
                  {filas.map((fila) => (
                    <tr
                      key={fila.id}
                      className={`border-b border-line last:border-0 ${editando?.id === fila.id ? 'bg-brand-50' : ''}`}
                    >
                      <Td>
                        <div className="flex items-center gap-3">
                          <span className="hidden size-8 shrink-0 items-center justify-center rounded-full bg-brand-100 font-display text-xs font-bold text-brand-800 sm:flex">
                            {`${fila.nombre.charAt(0)}${fila.apellido.charAt(0)}`.toUpperCase()}
                          </span>
                          <span className="min-w-0">
                            <span className="block font-semibold text-ink">
                              {fila.nombre} {fila.apellido}
                              {actual?.id === fila.id ? (
                                <span className="ml-1.5 text-xs font-normal text-muted">(usted)</span>
                              ) : null}
                            </span>
                            <span className="block font-mono text-xs text-muted sm:hidden">{fila.usuario}</span>
                          </span>
                        </div>
                      </Td>
                      <Td className="hidden font-mono text-[13px] text-muted sm:table-cell">{fila.usuario}</Td>
                      <Td>
                        {fila.rol === 'admin' ? (
                          <Pill tono="info" icono={<ShieldCheck className="size-3.5" />}>
                            Admin<span className="hidden sm:inline">istrador</span>
                          </Pill>
                        ) : (
                          <Pill icono={<UserRound className="size-3.5" />}>Inspector</Pill>
                        )}
                      </Td>
                      <Td className="text-right">
                        <IconButton
                          label={`Editar a ${fila.nombre}`}
                          onClick={() => {
                            setEditando(fila)
                            setAviso(null)
                            setForm({
                              nombre: fila.nombre,
                              apellido: fila.apellido,
                              usuario: fila.usuario,
                              contrasena: '',
                              rol: fila.rol,
                              dni: fila.dni ?? '',
                            })
                          }}
                        >
                          <Pencil className="size-4" />
                        </IconButton>
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </div>
        </div>
      </div>
    </Page>
  )
}
