from app.infrastructure.security.password_hasher import hash_password

# bcrypt siempre, también si el usuario no existe (evita enumerar cuentas por tiempo).
HASH_TIMING_DUMMY = hash_password("timing-dummy-no-es-una-clave-real")
