"""La salida del §10 de docs/especificacion-calculo.md: contenido, decisiones
para salir del indeterminado (D-36), componentes (D-37) y formatos."""

import json
import random

import pytest

from actualizacion.calculo import REGIMENES
from actualizacion.carga import cargar
from actualizacion.modelo import ResultadoCarga
from actualizacion.salida import como_dict, como_json, descripcion, informe, pregunta, texto
from ayudas import clasificacion, entrada, evento, revision, version
from test_atribucion import CASOS, _entrada_al_azar


def informe_de(e):
    return informe(ResultadoCarga(e, ()))


def ejemplo_6():
    return informe_de(
        entrada(
            "2028-10-10",
            "2027-10-01",
            [clasificacion("2027-09-20", "alto", True, True, True)],
            [revision("R1", "inicial", "2027-11-25")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )


def ejemplo_1(referencia):
    return informe_de(
        entrada(referencia, "2020-03-02", [clasificacion("2020-03-02")], [revision("R1", "inicial", "2020-03-02")])
    )


# --- D-36: salir del indeterminado ------------------------------------------------


def test_decisiones_del_ejemplo_6():
    inf = ejemplo_6()
    decisiones = {d.dimension: d for d in inf["ley_rd"].decisiones}
    assert set(decisiones) == {"RA", "IP"}

    ra = decisiones["RA"]
    assert ra.pregunta == "¿Una revisión hecha antes de tiempo reinicia el plazo de la siguiente?"
    assert ra.referencia == "S-3, §2.2"
    respuestas = {x.lectura: x for x in ra.respuestas}
    # Con RA-1 el estado queda resuelto; con RA-2 aún depende de IP.
    assert respuestas["RA-1"].estados == ("en_plazo",)
    assert respuestas["RA-1"].depende_de == ()
    assert respuestas["RA-2"].depende_de == ("IP",)
    assert set(respuestas["RA-2"].estados) == {"en_plazo", "vencida"}

    ip = {x.lectura: x for x in decisiones["IP"].respuestas}
    # IP-2 resuelve: con ella RA no cambia nada (hoja sin RA).
    assert (ip["IP-2"].estados, ip["IP-2"].depende_de) == (("en_plazo",), ())
    assert ip["IP-1"].depende_de == ("RA",)
    assert "cliente.fecha_inicio_relacion" in decisiones["IP"].datos


def test_pregunta_de_un_dato_que_falta():
    inf = informe_de(
        entrada("2021-06-01", "2020-01-10", [clasificacion("2020-01-10", "medio", None)], [revision("R1", "inicial", "2020-01-10")])
    )
    (d,) = inf["ley_rd"].decisiones
    assert d.pregunta == "La clasificación del 2020-01-10 no dice si el riesgo es superior al promedio: ¿lo es?"
    assert [(x.lectura, x.descripcion, x.estados) for x in d.respuestas] == [
        ("SP-1", "sí", ("vencida",)),
        ("SP-2", "no", ("en_plazo",)),
    ]


@pytest.mark.parametrize("semilla", range(0, CASOS, 4))
def test_toda_dimension_tiene_pregunta_y_toda_lectura_descripcion(semilla):
    inf = informe_de(_entrada_al_azar(random.Random(semilla)))
    for r in inf.regimenes:
        for d in r.decisiones:
            assert d.pregunta and "{}" not in d.pregunta
            for x in d.respuestas:
                assert x.descripcion != x.lectura, x.lectura
                # D-36: si no resuelve, dice de qué depende.
                assert (len(x.estados) == 1) == (not x.depende_de)
    texto(inf)
    json.loads(como_json(inf))


def test_pregunta_con_parametro():
    assert pregunta("EV (operacion_significativa)")[0] == (
        "¿A qué letra del art. 26.3 del AMLR corresponde un evento «operacion_significativa»?"
    )
    assert descripcion("RA-3 (reinician hasta R2)") == "lo decide el manual"


# --- Comparación (D-40) y componentes (D-37) --------------------------------------


def test_mismo_estado_con_fechas_distintas():
    # Ejemplo 8 antes del vencimiento: los seis en plazo, con fechas distintas.
    inf = informe_de(
        entrada(
            "2027-10-01",
            "2015-06-01",
            [clasificacion("2015-06-01", "alto", True, None, None)],
            [revision("R1", "inicial", "2015-06-01"), revision("R2", "periodica", "2026-11-15")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )
    assert not inf.estados_distintos
    assert inf.fechas_distintas
    assert inf.normas_difieren  # D-40: mismo estado, fechas distintas
    assert "Mismo estado en los seis (en_plazo), con fechas distintas." in texto(inf)


def test_componentes_con_empate_y_eventos():
    inf = informe_de(
        entrada(
            "2028-06-01",
            "2028-03-01",
            [clasificacion("2028-03-01", "alto", True, True, True)],
            [revision("R1", "inicial", "2028-03-01")],
            [evento("E", "informacion_de_riesgo", "2028-05-01", "2028-05-10")],
            versiones=[version(periodicidades={"alto": 12}, plazo=30)],
        )
    )
    t4 = inf["T-4"]
    assert [c.componente.norma for c in t4.periodicos] == ["RD", "AMLR"]  # D-34
    assert all(c.combinaciones == len(t4.resultado.lecturas) for c in t4.periodicos)
    salida = texto(inf)
    assert "RD: desde el 2028-03-01, 12 meses → vence el 2029-03-01 (en_plazo)" in salida
    assert "E · AMLR 26.3.c · activado el 2028-05-10 · vence el 2028-06-09 (en_plazo)" in salida
    evento_json = como_dict(inf)["regimenes"]["amlr"]["componentes"]["eventos"][0]
    assert evento_json["bases"] == ["AMLR 26.3.c"]
    assert evento_json["fecha_limite"] == "2028-06-09"


# --- Texto --------------------------------------------------------------------------


def test_texto_del_ejemplo_6():
    salida = texto(ejemplo_6())
    assert salida.startswith("Cliente C\nFecha de referencia: 2028-10-10 · AMLR aplicable desde el 2027-07-10\n")
    assert "no una determinación jurídica" in salida
    assert "  ley_rd  2028-09-20 o 2028-10-01 o 2028-11-25  indeterminado" in salida
    assert "Qué hay que decidir para salir del indeterminado" in salida
    assert "    RA — ¿Una revisión hecha antes de tiempo reinicia el plazo de la siguiente? (S-3, §2.2)" in salida
    assert "      RA-2 (nunca: solo las revisiones periódicas marcan el calendario): " in salida
    assert "; aún depende de IP" in salida
    # D-35: los regímenes iguales se remiten.
    assert "  amlr: lo mismo que ley_rd" in salida


def test_texto_sin_diferencias():
    salida = texto(ejemplo_1("2028-01-15"))
    assert "Qué hay que decidir" not in salida
    assert "ley_rd y amlr no coinciden" in salida  # vencida en los dos, fechas distintas
    assert "Mismo estado en los seis (vencida), con fechas distintas." in salida


def test_texto_resume_muchas_fechas():
    # D-39.
    carga = cargar(_ejemplo_del_modelo())
    salida = texto(informe(carga))
    assert "entre el 2019-11-10 y el 2030-02-14 (10 fechas posibles)" in salida
    datos = como_dict(informe(carga))
    assert len(datos["regimenes"]["amlr"]["fechas_proxima_revision"]) == 10


def _ejemplo_del_modelo():
    from test_ejemplo_modelo import EJEMPLO

    return EJEMPLO


def test_texto_de_entrada_no_valida():
    inf = informe(cargar('{"version_modelo": 2}'))
    salida = texto(inf)
    assert salida.startswith("La entrada no es válida (8 errores):\n")
    assert "  ERR-01  version_modelo: «version_modelo» debe ser 1" in salida


# --- JSON ---------------------------------------------------------------------------


def test_json_del_ejemplo_6():
    datos = json.loads(como_json(ejemplo_6()))
    assert datos["valida"] is True
    assert datos["cliente"] == "C"
    assert datos["fecha_referencia"] == "2028-10-10"
    assert datos["comparacion"]["hay_indeterminado"] is True
    assert list(datos["regimenes"]) == list(REGIMENES)
    ley = datos["regimenes"]["ley_rd"]
    assert ley["estado"] == "indeterminado"
    assert ley["fechas_proxima_revision"] == ["2028-09-20", "2028-10-01", "2028-11-25"]
    ra = next(d for d in ley["decisiones"] if d["dimension"] == "RA")
    ra1 = next(x for x in ra["respuestas"] if x["lectura"] == "RA-1")
    assert (ra1["resuelve"], ra1["estados"], ra1["depende_de"]) == (True, ["en_plazo"], [])
    # Las lecturas completas, con sus combinaciones.
    assert {"lecturas", "estado", "fecha_proxima_revision", "periodicos", "eventos", "avisos"} == set(ley["lecturas"][0])
    assert ley["componentes"]["combinaciones"] == len(ley["lecturas"])


def test_json_de_entrada_no_valida():
    datos = json.loads(como_json(informe(cargar("{"))))
    assert datos["valida"] is False
    assert datos["errores"][0]["codigo"] == "ERR-01"
    assert datos["comparacion"] is None
    assert datos["regimenes"] == {}


def test_texto_de_relacion_terminada():
    inf = informe_de(
        entrada(
            "2026-01-01",
            "2019-01-10",
            [clasificacion("2019-01-10")],
            [revision("R1", "inicial", "2019-01-10")],
            terminacion="2025-06-01",
        )
    )
    salida = texto(inf)
    assert "  ley_rd  sin fecha  relacion_terminada" in salida
    assert "    Periódico: ninguno." in salida
    assert "La relación terminó el 2025-06-01" in salida
