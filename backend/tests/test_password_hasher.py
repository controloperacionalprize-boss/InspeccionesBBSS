from app.infrastructure.security.password_hasher import hash_password, verify_password


def test_hash_no_devuelve_el_texto_plano():
    resultado = hash_password("mi-clave-segura")
    assert resultado != "mi-clave-segura"


def test_verify_password_acepta_la_contrasena_correcta():
    hash_guardado = hash_password("mi-clave-segura")
    assert verify_password("mi-clave-segura", hash_guardado) is True


def test_verify_password_rechaza_contrasena_incorrecta():
    hash_guardado = hash_password("mi-clave-segura")
    assert verify_password("otra-clave", hash_guardado) is False


def test_verify_password_con_hash_corrupto_no_lanza_excepcion():
    assert verify_password("cualquiera", "esto-no-es-un-hash-bcrypt") is False
