# Consultar Campo – Packing

Proyecto base del sistema **Consultar Campo – Packing**.

Stack:

- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + Python
- **Base de datos:** PostgreSQL
- **Arquitectura:** hexagonal ligera

Esta etapa incluye únicamente la estructura ejecutable, sin lógica de negocio ni datos de prueba.

## Estructura

```text
├── backend/          # API FastAPI
├── frontend/         # App React
├── database/         # Soporte de migraciones / esquema
├── docker-compose.yml
└── README.md
```

## Requisitos

- Python 3.12+
- Node.js 20+
- Docker y Docker Compose (opcional, recomendado)

## Variables de entorno

### Backend (`backend/.env`)

```env
APP_ENV=development
DATABASE_URL=postgresql://usuario:password@localhost:5432/consultar_campo
CORS_ORIGINS=http://localhost:5173

JWT_SECRET_KEY=cambiar-esta-clave-en-produccion
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

## Arranque con Docker

Con **Neon** (u otra Postgres remota): `backend/.env` debe tener `DATABASE_URL` apuntando a ese host. No hace falta Postgres en compose.

```bash
docker compose up --build
```

Postgres **local** opcional (perfil `local-db`), si `DATABASE_URL` usa el host `postgres`:

```bash
docker compose --profile local-db up --build
```

1. Si usas el perfil `local-db`, copiar `.env.example` (raíz) a `.env` y definir `POSTGRES_USER`/`POSTGRES_PASSWORD`.
2. Asegurarse de que `backend/.env` exista (JWT, `DATABASE_URL`, CORS). No se sobreescriben en `docker-compose.yml`.

Servicios:

| Servicio   | URL                    |
|------------|------------------------|
| Frontend   | http://localhost:3000  |
| Backend    | http://localhost:8000  |
| PostgreSQL | localhost:5432 (solo con `--profile local-db`) |
| Health     | http://localhost:8000/health |

## Arranque local (desarrollo)

### 1. Base de datos

```bash
docker compose --profile local-db up postgres -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements-dev.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend en: http://localhost:5173

## Tests

```bash
cd backend
.venv\Scripts\pytest -v      # Windows
# source .venv/bin/activate && pytest -v   # Linux/macOS
```

The tests cubren login, hashing, validaciones de inspecciones y permisos HTTP (inspector vs admin) con SQLite en memoria, sin usar la base remota.

## Fotos

`URL_FOTO` en inspecciones es texto (URL o ruta). No hay bucket de Neon ni almacenamiento de objetos en esta etapa.

## Salud

- `GET /health` — proceso vivo
- `GET /health/ready` — además verifica la base de datos

## Seguridad: JWT_SECRET_KEY obligatorio

La app **no arranca** si `JWT_SECRET_KEY` no está configurado, tiene menos de 32 caracteres, o es igual al valor de ejemplo de `.env.example`. Generar uno propio:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Alembic

Las migraciones viven en `backend/alembic/versions/`.

Las migraciones viven en `backend/alembic/versions/`. En una base **ya existente** (como el entorno de prueba) basta:

```bash
cd backend
alembic upgrade head
```

En una Postgres **vacía**, `0001` crea las tablas base y el resto aplica índices, roles y DNI. Luego `alembic upgrade head` deja el esquema al día.

Todavía no hay seeds de catálogos ni inspecciones.

## Endpoint de salud

```http
GET /health
```

Respuesta:

```json
{
  "status": "ok"
}
```

## Autenticación

Login simple con usuario + contraseña (hash bcrypt) y token JWT.

```http
POST /api/auth/login
Content-Type: application/json

{
  "usuario": "demo",
  "contrasena": "demo1234"
}
```

Respuesta:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "usuario": { "id": 1, "nombre": "...", "apellido": "...", "usuario": "demo", "rol": "inspector" }
}
```

Usar el token en el header `Authorization: Bearer <token>` para el resto de endpoints protegidos (`/api/auth/me`, catálogos, etc.).

## Roles

Tabla `Roles` con dos valores fijos, **sin empresa**: `admin` e `inspector`.

| Rol | Catálogos (GET) | Catálogos (POST/PUT/DELETE) | Inspecciones (GET/POST/PUT) | Inspecciones (DELETE) |
|-----|-----------------|-----------------------------|-----------------------------|------------------------|
| inspector | Sí | No | Sí | No |
| admin | Sí | Sí | Sí | Sí |

`GET /api/roles` lista los roles. Alta de usuarios: `POST /api/usuarios` (solo admin).

## Endpoints de catálogos

CRUD básico (GET, POST, PUT, DELETE), todos protegidos con JWT:

- `/api/empresas`
- `/api/divisiones`
- `/api/categorias`
- `/api/fundos` (requiere `ID_EMPRESA`)
- `/api/areas` (requiere `ID_DIVISION`)
- `/api/subcategorias` (requiere `ID_CATEGORIA`)

## Endpoint de Inspecciones (Campo / Packing)

CRUD protegido con JWT, con filtros de consulta y validación de reglas de negocio:

```http
GET /api/inspecciones?id_empresa=1&id_fundo=2&fecha_desde=2026-01-01&fecha_hasta=2026-12-31&skip=0&limit=100
GET /api/inspecciones/{id}
POST /api/inspecciones
PUT /api/inspecciones/{id}
DELETE /api/inspecciones/{id}
```

Al crear/actualizar se valida que:

- Empresa, Fundo, División, Área, Categoría y Subcategoría existan.
- El Fundo pertenezca a la Empresa indicada.
- El Área pertenezca a la División indicada.
- La Subcategoría pertenezca a la Categoría indicada.

Si alguna referencia no es válida, responde `400 Bad Request` con el detalle.

## Esquema de base de datos

La base ya contaba con tablas creadas manualmente (`Empresas`, `Division`, `Fundo`, `Area`, `Categoria`, `Subcategoria`, `Usuarios`, `Inspecciones`). Se aplicó la migración `0001_fix_schema_constraints` para:

- Renombrar `Usuarios.CONTRASEÑA` → `Usuarios.PASSWORD_HASH` (evita problemas de encoding y refleja que se guarda un hash, no texto plano).
- Forzar `NOT NULL` en columnas obligatorias de negocio.
- Agregar `UNIQUE` sobre `Usuarios.USUARIO`.

Los `ID` de todas las tablas ya eran columnas `IDENTITY` (autoincrementales), no requirieron cambios.

## Capas del backend

| Capa              | Responsabilidad                         |
|-------------------|-----------------------------------------|
| `domain`          | Entidades y reglas de negocio           |
| `application`     | Casos de uso                            |
| `infrastructure`  | BD, config, adaptadores externos        |
| `presentation`    | API HTTP (FastAPI)                      |

Convención de nombres: código técnico en inglés (`health`, `router`, `session`); textos de UI en español.

## Notas

En esta base **no** se incluyen:

- datos ficticios / seeds de catálogos o inspecciones
- reportes o dashboards
- almacenamiento de fotos (solo el campo `URL_FOTO`)
