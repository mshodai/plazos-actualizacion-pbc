"""Validaciones del §9 de docs/modelo-datos.md, una a una.

Cada test parte de una entrada mínima válida (un cliente con una clasificación,
una revisión inicial y un evento atendido) y cambia solo lo necesario para
provocar el error.
"""

import json
from datetime import date

import pytest

from actualizacion.carga import cargar, cargar_fichero
from actualizacion.modelo import ERRORES, TIPOS_EVENTO


def base():
    return {
        "version_modelo": 1,
        "fecha_referencia": "2030-01-01",
        "sujeto": {"actividad": "otra"},
        "manual": {"versiones": [version("M1", "2019-01-01")]},
        "cliente": {
            "id": "C",
            "fecha_inicio_relacion": "2020-01-10",
            "fecha_terminacion_relacion": None,
            "clasificaciones": [clasificacion("2020-01-10")],
            "revisiones": [revision("R1", "inicial", "2020-01-10"), revision("R2", "por_evento", "2029-06-15", ["E1"])],
            "eventos": [evento("E1")],
        },
    }


def version(id_, vigente_desde, periodicidades=None, plazo=None, reinicia=None):
    return {
        "id": id_,
        "vigente_desde": vigente_desde,
        "periodicidades": periodicidades if periodicidades is not None else [{"nivel_entidad": "medio", "meses": 36}],
        "plazo_revision_por_evento_dias": plazo,
        "revision_anticipada_reinicia_plazo": reinicia,
    }


def clasificacion(fecha, nivel="medio", superior=False, elevado=None, seccion_4=None):
    return {
        "fecha": fecha,
        "nivel_entidad": nivel,
        "superior_al_promedio": superior,
        "riesgo_elevado_amlr": elevado,
        "medidas_seccion_4_amlr": seccion_4,
    }


def revision(id_, tipo, fecha, eventos=(), resultado="actualizada"):
    return {"id": id_, "tipo": tipo, "fecha": fecha, "resultado": resultado, "eventos": list(eventos)}


def evento(id_, tipo="cambio_actividad", hecho="2029-05-02", conocimiento="2029-05-20", **campos):
    return {
        "id": id_,
        "tipo": tipo,
        "fecha_hecho": hecho,
        "fecha_conocimiento": conocimiento,
        "relevante_segun_entidad": True,
        **campos,
    }


def validar(datos):
    return cargar(json.dumps(datos))


def codigos(datos):
    return [e.codigo for e in validar(datos).errores]


def rutas(datos, codigo):
    return [e.ruta for e in validar(datos).errores if e.codigo == codigo]


# --- Entrada válida ----------------------------------------------------------


def test_la_base_es_valida():
    resultado = validar(base())
    assert resultado.valida, resultado.errores
    cliente = resultado.entrada.cliente
    assert cliente.revisiones[1].eventos == ("E1",)
    assert type(cliente.fecha_inicio_relacion) is date


def test_todos_los_codigos_estan_documentados():
    assert list(ERRORES) == [f"ERR-{n:02d}" for n in range(1, 9)]


def test_con_errores_no_hay_entrada():
    datos = base()
    datos["cliente"]["clasificaciones"] = []
    resultado = validar(datos)
    assert resultado.entrada is None
    assert not resultado.valida


def test_cargar_fichero(tmp_path):
    fichero = tmp_path / "entrada.json"
    fichero.write_text(json.dumps(base()), encoding="utf-8")
    assert cargar_fichero(fichero).valida


# --- ERR-01: estructura y tipos ----------------------------------------------


def test_json_mal_formado():
    # Modelo, V-15.
    assert [e.codigo for e in cargar("{").errores] == ["ERR-01"]


@pytest.mark.parametrize("constante", ["NaN", "Infinity", "-Infinity"])
def test_constantes_no_json(constante):
    # Modelo, V-15.
    texto = json.dumps(base()).replace('"version_modelo": 1', f'"version_modelo": {constante}')
    assert "ERR-01" in [e.codigo for e in cargar(texto).errores]


def test_clave_repetida():
    # Modelo, V-15.
    texto = json.dumps(base()).replace('"version_modelo": 1', '"version_modelo": 1, "version_modelo": 1')
    errores = cargar(texto).errores
    assert [e.codigo for e in errores] == ["ERR-01"]
    assert "repetida" in errores[0].mensaje


def test_raiz_no_es_objeto():
    assert codigos([]) == ["ERR-01"]


def test_regimen_es_error():
    datos = base()
    datos["regimen"] = "amlr"
    assert rutas(datos, "ERR-01") == ["regimen"]


@pytest.mark.parametrize(
    "ruta",
    [
        ("otro_campo",),
        ("sujeto", "naturaleza"),
        ("manual", "extra"),
        ("cliente", "regimen"),
    ],
)
def test_campo_desconocido(ruta):
    # Modelo, V-1.
    datos = base()
    objeto = datos
    for clave in ruta[:-1]:
        objeto = objeto[clave]
    objeto[ruta[-1]] = "x"
    assert rutas(datos, "ERR-01") == [".".join(ruta)]


def test_campo_desconocido_en_elemento_de_lista():
    datos = base()
    datos["cliente"]["revisiones"][0]["alcance"] = "completa"
    assert rutas(datos, "ERR-01") == ["cliente.revisiones[0].alcance"]


@pytest.mark.parametrize(
    "objeto, clave",
    [
        ("version", "plazo_revision_por_evento_dias"),
        ("version", "revision_anticipada_reinicia_plazo"),
        ("clasificacion", "riesgo_elevado_amlr"),
        ("cliente", "fecha_terminacion_relacion"),
    ],
)
def test_campo_que_admite_null_no_se_puede_omitir(objeto, clave):
    # Modelo, V-2.
    datos = base()
    destino = {
        "version": datos["manual"]["versiones"][0],
        "clasificacion": datos["cliente"]["clasificaciones"][0],
        "cliente": datos["cliente"],
    }[objeto]
    del destino[clave]
    assert codigos(datos) == ["ERR-01"]


@pytest.mark.parametrize("version_modelo", [2, 0, "1", True, 1.0])
def test_version_modelo(version_modelo):
    # Modelo, V-3 y V-17.
    datos = base()
    datos["version_modelo"] = version_modelo
    assert rutas(datos, "ERR-01") == ["version_modelo"]


@pytest.mark.parametrize("fecha", ["20300101", "2030-1-1", "2030-02-30", "2030-W01-1", "", None, 20300101])
def test_fecha_mal_formada(fecha):
    # Modelo, V-16.
    datos = base()
    datos["fecha_referencia"] = fecha
    assert rutas(datos, "ERR-01") == ["fecha_referencia"]


@pytest.mark.parametrize("meses", [0, -12, 12.0, True, "12", None])
def test_meses_no_valido(meses):
    # Modelo, V-17.
    datos = base()
    datos["manual"]["versiones"][0]["periodicidades"][0]["meses"] = meses
    assert rutas(datos, "ERR-01") == ["manual.versiones[0].periodicidades[0].meses"]


@pytest.mark.parametrize("plazo", [0, -1, 30.5, False])
def test_plazo_por_evento_no_valido(plazo):
    datos = base()
    datos["manual"]["versiones"][0]["plazo_revision_por_evento_dias"] = plazo
    assert rutas(datos, "ERR-01") == ["manual.versiones[0].plazo_revision_por_evento_dias"]


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("superior_al_promedio", "sí"),
        ("riesgo_elevado_amlr", 1),
        ("medidas_seccion_4_amlr", "true"),
    ],
)
def test_calificacion_no_booleana(campo, valor):
    datos = base()
    datos["cliente"]["clasificaciones"][0][campo] = valor
    assert rutas(datos, "ERR-01") == [f"cliente.clasificaciones[0].{campo}"]


@pytest.mark.parametrize(
    "ruta, valor",
    [
        (("sujeto", "actividad"), "banco"),
        (("cliente", "revisiones", 0, "tipo"), "anticipada"),
        (("cliente", "revisiones", 0, "resultado"), "parcial"),
        (("cliente", "eventos", 0, "tipo"), "sospecha"),
    ],
)
def test_enumerado_no_valido(ruta, valor):
    datos = base()
    objeto = datos
    for clave in ruta[:-1]:
        objeto = objeto[clave]
    objeto[ruta[-1]] = valor
    esperada = ".".join(str(c) for c in ruta).replace(".0.", "[0].")
    assert rutas(datos, "ERR-01") == [esperada]


def test_relevante_no_admite_null():
    datos = base()
    datos["cliente"]["eventos"][0]["relevante_segun_entidad"] = None
    assert rutas(datos, "ERR-01") == ["cliente.eventos[0].relevante_segun_entidad"]


@pytest.mark.parametrize("lista", [("manual", "versiones"), ("cliente", "revisiones"), ("cliente", "eventos")])
def test_lista_que_no_es_lista(lista):
    datos = base()
    datos[lista[0]][lista[1]] = {}
    assert f"{lista[0]}.{lista[1]}" in rutas(datos, "ERR-01")


# --- Eventos: campos según el tipo --------------------------------------------


@pytest.mark.parametrize("tipo", ["obligacion_contacto_titularidad_real", "obligacion_contacto_dac"])
def test_contacto_exige_anio_natural(tipo):
    datos = base()
    datos["cliente"]["eventos"][0]["tipo"] = tipo
    assert rutas(datos, "ERR-01") == ["cliente.eventos[0].anio_natural"]
    datos["cliente"]["eventos"][0]["anio_natural"] = 2029
    resultado = validar(datos)
    assert resultado.valida
    assert resultado.entrada.cliente.eventos[0].anio_natural == 2029


@pytest.mark.parametrize("anio", [0, 10000, 2029.0, "2029", None])
def test_anio_natural_no_valido(anio):
    # Modelo, V-17.
    datos = base()
    datos["cliente"]["eventos"][0].update(tipo="obligacion_contacto_dac", anio_natural=anio)
    assert rutas(datos, "ERR-01") == ["cliente.eventos[0].anio_natural"]


def test_anio_natural_fuera_de_un_tipo_de_contacto():
    # Modelo, V-1.
    datos = base()
    datos["cliente"]["eventos"][0]["anio_natural"] = 2029
    assert rutas(datos, "ERR-01") == ["cliente.eventos[0].anio_natural"]


def test_anio_natural_no_se_compara_con_la_fecha_del_hecho():
    # Modelo, V-22: ni con la fecha de referencia (V-11).
    datos = base()
    datos["cliente"]["eventos"][0].update(tipo="obligacion_contacto_titularidad_real", anio_natural=2035)
    assert validar(datos).valida


def test_otro_exige_descripcion():
    # Modelo, V-18.
    datos = base()
    datos["cliente"]["eventos"][0]["tipo"] = "otro"
    assert rutas(datos, "ERR-01") == ["cliente.eventos[0].descripcion"]
    datos["cliente"]["eventos"][0]["descripcion"] = None
    assert rutas(datos, "ERR-01") == ["cliente.eventos[0].descripcion"]
    datos["cliente"]["eventos"][0]["descripcion"] = ""
    assert validar(datos).valida


def test_descripcion_opcional_admite_null():
    # Modelo, V-18.
    datos = base()
    datos["cliente"]["eventos"][0]["descripcion"] = None
    resultado = validar(datos)
    assert resultado.valida
    assert resultado.entrada.cliente.eventos[0].descripcion is None


@pytest.mark.parametrize("tipo", [t for t in TIPOS_EVENTO if not t.startswith("obligacion") and t != "otro"])
def test_todos_los_tipos_sin_campos_propios(tipo):
    datos = base()
    datos["cliente"]["eventos"][0]["tipo"] = tipo
    assert validar(datos).valida


# --- Admitidos ----------------------------------------------------------------


def test_textos_vacios():
    # Modelo, V-18.
    datos = base()
    datos["cliente"]["id"] = ""
    datos["cliente"]["clasificaciones"][0]["nivel_entidad"] = ""
    datos["manual"]["versiones"][0]["periodicidades"][0]["nivel_entidad"] = ""
    assert validar(datos).valida


def test_manual_y_periodicidades_vacios():
    # Modelo, V-19.
    datos = base()
    datos["manual"]["versiones"] = []
    assert validar(datos).valida
    datos["manual"]["versiones"] = [version("M1", "2019-01-01", periodicidades=[])]
    assert validar(datos).valida


def test_nivel_sin_periodicidad_en_el_manual():
    # Modelo, V-6 y V-21: «Medio» no es «medio».
    datos = base()
    datos["cliente"]["clasificaciones"][0]["nivel_entidad"] = "Medio"
    resultado = validar(datos)
    assert resultado.valida
    assert resultado.entrada.manual.versiones[0].periodicidad("Medio") is None


def test_todas_las_combinaciones_de_calificacion():
    # Modelo, V-13.
    valores = (True, False, None)
    for superior in valores:
        for elevado in valores:
            for seccion_4 in valores:
                datos = base()
                datos["cliente"]["clasificaciones"] = [clasificacion("2020-01-10", "medio", superior, elevado, seccion_4)]
                assert validar(datos).valida, (superior, elevado, seccion_4)


def test_revisiones_y_eventos_vacios():
    datos = base()
    datos["cliente"]["revisiones"] = []
    datos["cliente"]["eventos"] = []
    assert validar(datos).valida


def test_orden_libre_de_fechas():
    # Modelo, V-12 y V-22: revisión anterior al inicio, revisión que atiende un evento
    # posterior, y hechos posteriores a la terminación.
    datos = base()
    datos["cliente"]["revisiones"][0]["fecha"] = "2019-12-20"
    datos["cliente"]["revisiones"][1]["fecha"] = "2029-01-01"
    datos["cliente"]["fecha_terminacion_relacion"] = "2029-03-01"
    assert validar(datos).valida


def test_un_evento_en_varias_revisiones():
    # Modelo, V-20.
    datos = base()
    datos["cliente"]["revisiones"].append(revision("R3", "por_evento", "2029-07-01", ["E1"]))
    assert validar(datos).valida


def test_fechas_iguales_a_la_de_referencia():
    datos = base()
    datos["fecha_referencia"] = "2029-06-15"
    assert validar(datos).valida


# --- ERR-02: identificadores y fechas repetidos --------------------------------


def test_id_de_version_repetido():
    # Modelo, V-4.
    datos = base()
    datos["manual"]["versiones"].append(version("M1", "2027-07-10"))
    assert rutas(datos, "ERR-02") == ["manual.versiones[1].id"]


def test_vigente_desde_repetida():
    datos = base()
    datos["manual"]["versiones"].append(version("M2", "2019-01-01"))
    assert rutas(datos, "ERR-02") == ["manual.versiones[1].vigente_desde"]


def test_fecha_de_clasificacion_repetida():
    datos = base()
    datos["cliente"]["clasificaciones"].append(clasificacion("2020-01-10", "alto"))
    assert rutas(datos, "ERR-02") == ["cliente.clasificaciones[1].fecha"]


def test_id_de_revision_repetido():
    datos = base()
    datos["cliente"]["revisiones"][1]["id"] = "R1"
    assert rutas(datos, "ERR-02") == ["cliente.revisiones[1].id"]


def test_id_de_evento_repetido():
    datos = base()
    datos["cliente"]["eventos"].append(evento("E1", "nuevo_producto"))
    assert rutas(datos, "ERR-02") == ["cliente.eventos[1].id"]


def test_evento_citado_dos_veces_en_una_revision():
    # Modelo, V-20.
    datos = base()
    datos["cliente"]["revisiones"][1]["eventos"] = ["E1", "E1"]
    assert codigos(datos) == ["ERR-02"]
    assert rutas(datos, "ERR-02") == ["cliente.revisiones[1].eventos[1]"]


# --- ERR-03 a ERR-07 -----------------------------------------------------------


def test_nivel_repetido_en_una_version():
    # Modelo, V-5.
    datos = base()
    datos["manual"]["versiones"][0]["periodicidades"].append({"nivel_entidad": "medio", "meses": 12})
    assert codigos(datos) == ["ERR-03"]
    assert rutas(datos, "ERR-03") == ["manual.versiones[0].periodicidades[1].nivel_entidad"]


def test_mismo_nivel_en_versiones_distintas():
    datos = base()
    datos["manual"]["versiones"].append(version("M2", "2027-07-10"))
    assert validar(datos).valida


def test_clasificaciones_vacia():
    # Modelo, V-7.
    datos = base()
    datos["cliente"]["clasificaciones"] = []
    assert codigos(datos) == ["ERR-04"]


def test_evento_citado_que_no_existe():
    # Modelo, V-8.
    datos = base()
    datos["cliente"]["revisiones"][1]["eventos"] = ["E1", "E9"]
    assert codigos(datos) == ["ERR-05"]
    assert rutas(datos, "ERR-05") == ["cliente.revisiones[1].eventos[1]"]


def test_conocimiento_anterior_al_hecho():
    # Modelo, V-9.
    datos = base()
    datos["cliente"]["eventos"][0]["fecha_conocimiento"] = "2029-05-01"
    assert codigos(datos) == ["ERR-06"]


def test_conocimiento_igual_al_hecho():
    datos = base()
    datos["cliente"]["eventos"][0]["fecha_conocimiento"] = "2029-05-02"
    assert validar(datos).valida


def test_terminacion_anterior_al_inicio():
    # Modelo, V-10.
    datos = base()
    datos["cliente"]["fecha_terminacion_relacion"] = "2020-01-09"
    assert codigos(datos) == ["ERR-07"]


# --- ERR-08: hechos posteriores a la fecha de referencia -----------------------


@pytest.mark.parametrize(
    "ruta",
    [
        "manual.versiones[0].vigente_desde",
        "cliente.fecha_inicio_relacion",
        "cliente.fecha_terminacion_relacion",
        "cliente.clasificaciones[0].fecha",
        "cliente.revisiones[1].fecha",
        "cliente.eventos[0].fecha_hecho",
        "cliente.eventos[0].fecha_conocimiento",
    ],
)
def test_hecho_posterior(ruta):
    # Modelo, V-11.
    datos = base()
    datos["fecha_referencia"] = "2031-01-01"
    objeto = datos
    partes = ruta.replace("[", ".").replace("]", "").split(".")
    for parte in partes[:-1]:
        objeto = objeto[int(parte)] if parte.isdigit() else objeto[parte]
    objeto[partes[-1]] = "2031-01-02"
    if partes[-1] == "fecha_hecho":
        objeto["fecha_conocimiento"] = "2031-01-02"
    assert ruta in rutas(datos, "ERR-08")


def test_un_error_por_cada_hecho_posterior():
    datos = base()
    datos["fecha_referencia"] = "2029-01-01"
    assert rutas(datos, "ERR-08") == [
        "cliente.revisiones[1].fecha",
        "cliente.eventos[0].fecha_hecho",
        "cliente.eventos[0].fecha_conocimiento",
    ]


# --- Varios errores y errores derivados ----------------------------------------


def test_se_recogen_todos_los_errores():
    datos = base()
    datos["version_modelo"] = 2
    datos["cliente"]["clasificaciones"] = []
    datos["cliente"]["eventos"][0]["fecha_conocimiento"] = "2029-05-01"
    datos["cliente"]["fecha_terminacion_relacion"] = "2019-01-01"
    assert codigos(datos) == ["ERR-01", "ERR-04", "ERR-06", "ERR-07"]


def test_fecha_mal_formada_no_da_errores_derivados():
    # Modelo, V-23: sin fecha_hecho válida no se compara con el conocimiento, y sin
    # fecha de referencia válida no hay ERR-08.
    datos = base()
    datos["cliente"]["eventos"][0]["fecha_hecho"] = "2029-13-01"
    datos["fecha_referencia"] = "hoy"
    assert codigos(datos) == ["ERR-01", "ERR-01"]


def test_id_de_evento_mal_formado_no_da_err_05():
    # Modelo, V-23.
    datos = base()
    datos["cliente"]["eventos"][0]["id"] = 1
    assert codigos(datos) == ["ERR-01"]


def test_lista_de_eventos_mal_formada_no_da_err_05():
    # Modelo, V-23.
    datos = base()
    datos["cliente"]["eventos"] = "E1"
    assert codigos(datos) == ["ERR-01"]


def test_evento_que_no_es_objeto_no_da_err_05():
    datos = base()
    datos["cliente"]["eventos"].append("E2")
    assert codigos(datos) == ["ERR-01"]


def test_ids_mal_formados_no_cuentan_como_repetidos():
    datos = base()
    datos["cliente"]["revisiones"][0]["id"] = None
    datos["cliente"]["revisiones"][1]["id"] = None
    assert codigos(datos) == ["ERR-01", "ERR-01"]
