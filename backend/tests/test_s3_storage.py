from app.infrastructure.storage import s3_storage


class _ClienteFalso:
    def __init__(self):
        self.firmas = 0

    def generate_presigned_url(self, *_args, **_kwargs):
        self.firmas += 1
        return f"https://bucket/objeto?firma={self.firmas}"

    def delete_object(self, **_kwargs):
        pass


def test_url_firmada_se_reutiliza_para_que_el_navegador_cachee(monkeypatch):
    cliente = _ClienteFalso()
    monkeypatch.setattr(s3_storage, "_cliente", lambda: cliente)
    s3_storage._urls.clear()

    primera = s3_storage.url_firmada("inspecciones/1/a.jpg")
    segunda = s3_storage.url_firmada("inspecciones/1/a.jpg")

    assert primera == segunda
    assert cliente.firmas == 1


def test_url_se_renueva_cerca_del_vencimiento_y_al_eliminar(monkeypatch):
    cliente = _ClienteFalso()
    monkeypatch.setattr(s3_storage, "_cliente", lambda: cliente)
    s3_storage._urls.clear()

    s3_storage.url_firmada("k")
    url, _ = s3_storage._urls["k"]
    s3_storage._urls["k"] = (url, 0)  # vencida
    s3_storage.url_firmada("k")
    assert cliente.firmas == 2

    s3_storage.eliminar_objeto("k")
    assert "k" not in s3_storage._urls
