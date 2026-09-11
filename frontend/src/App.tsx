import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { ProtectedLayout } from './components/AppShell'
import { CatalogosPage } from './pages/catalogos/CatalogosPage'
import { ConsultaFormPage } from './pages/consultas/ConsultaFormPage'
import { ConsultasPage } from './pages/consultas/ConsultasPage'
import { HomePage } from './pages/HomePage'
import { IndumentariaFormPage } from './pages/indumentaria/IndumentariaFormPage'
import { IndumentariaPage } from './pages/indumentaria/IndumentariaPage'
import { InspeccionFormPage } from './pages/inspecciones/InspeccionFormPage'
import { InspeccionesPage } from './pages/inspecciones/InspeccionesPage'
import { LoginPage } from './pages/LoginPage'
import { UsuariosPage } from './pages/usuarios/UsuariosPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/inspecciones" element={<InspeccionesPage />} />
            <Route path="/inspecciones/nueva" element={<InspeccionFormPage />} />
            <Route path="/inspecciones/:id" element={<InspeccionFormPage />} />
            <Route path="/consultas" element={<ConsultasPage />} />
            <Route path="/consultas/nueva" element={<ConsultaFormPage />} />
            <Route path="/consultas/:id" element={<ConsultaFormPage />} />
            <Route path="/indumentaria" element={<IndumentariaPage />} />
            <Route path="/indumentaria/nueva" element={<IndumentariaFormPage />} />
            <Route path="/indumentaria/:id" element={<IndumentariaFormPage />} />
            <Route path="/catalogos" element={<CatalogosPage />} />
            <Route path="/usuarios" element={<UsuariosPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
