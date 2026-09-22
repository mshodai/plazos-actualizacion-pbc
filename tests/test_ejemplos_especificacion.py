"""Los ejemplos del §9 de docs/especificacion-calculo.md, con sus fechas.

Cada test reproduce un ejemplo tal como está escrito y comprueba los estados
y las fechas de los seis regímenes, y a qué lecturas se atribuye cada
`indeterminado` (D-30).
"""

from datetime import date

import pytest

from actualizacion.calculo import calcular
from ayudas import clasificacion, entrada, evento, revision, version

D = date.fromisoformat


def estados(resultado):
    return resultado.estados


def fechas(resultado, regimen):
    return [str(f) for f in resultado[regimen].fechas_proxima_revision]


def atribuidas(resultado, regimen):
    return [a.dimension for a in resultado[regimen].atribuciones]


def lecturas_de(resultado, regimen, dimension):
    """{lectura: estados} de una dimensión atribuida."""
    (atribucion,) = [a for a in resultado[regimen].atribuciones if a.dimension == dimension]
    return {lectura: set(e) for lectura, e in atribucion.lecturas}


# --- Ejemplo 1 --------------------------------------------------------------------


def ejemplo_1(referencia):
    return calcular(
        entrada(referencia, "2020-03-02", [clasificacion("2020-03-02")], [revision("R1", "inicial", "2020-03-02")])
    )


def test_ejemplo_1_antes_de_a():
    r = ejemplo_1("2024-06-01")
    assert estados(r) == {
        "ley_rd": "vencida",
        "amlr": "indeterminado",
        "T-1": "vencida",
        "T-2": "vencida",
        "T-3": "vencida",
        "T-4": "vencida",
    }
    assert fechas(r, "ley_rd") == ["2023-03-02"]
    assert fechas(r, "amlr") == ["2023-03-02", "2025-03-02"]
    assert atribuidas(r, "amlr") == ["PM"]
    assert lecturas_de(r, "amlr", "PM") == {"PM-1": {"en_plazo"}, "PM-2": {"vencida"}}
    assert any("D-24" in a for a in r["amlr"].avisos)
    assert r.coincide_transicion and not r.coinciden_normas


def test_ejemplo_1_despues_de_a():
    r = ejemplo_1("2028-01-15")
    assert set(estados(r).values()) == {"vencida"}
    assert not any("D-24" in a for a in r["amlr"].avisos)


# --- Ejemplo 2 --------------------------------------------------------------------


def test_ejemplo_2_poblaciones():
    r = calcular(
        entrada(
            "2029-06-01",
            "2028-03-01",
            [clasificacion("2028-03-01", "medio", superior=True, elevado=False, seccion_4=True)],
            [revision("R1", "inicial", "2028-03-01")],
        )
    )
    assert estados(r) == {
        "ley_rd": "vencida",
        "amlr": "indeterminado",
        "T-1": "indeterminado",
        "T-2": "indeterminado",
        "T-3": "indeterminado",
        "T-4": "vencida",
    }
    assert fechas(r, "ley_rd") == ["2029-03-01"]
    assert any("D-14" in a for a in r["ley_rd"].avisos)
    assert fechas(r, "amlr") == ["2029-03-01", "2031-03-01", "2033-03-01"]
    assert atribuidas(r, "amlr") == ["PB"]
    assert lecturas_de(r, "amlr", "PB") == {"PB-1": {"en_plazo"}, "PB-2": {"vencida"}}
    assert fechas(r, "T-4") == ["2029-03-01"]


# --- Ejemplo 3 --------------------------------------------------------------------


def test_ejemplo_3_revision_sin_cambios():
    r = calcular(
        entrada(
            "2029-01-10",
            "2027-09-01",
            [clasificacion("2027-09-01", "alto", True, True, True)],
            [revision("R1", "inicial", "2027-09-01"), revision("R2", "periodica", "2028-08-20", "sin_cambios")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )
    assert estados(r)["ley_rd"] == "en_plazo"
    assert fechas(r, "ley_rd") == ["2029-08-20"]
    for regimen in ("amlr", "T-1", "T-2", "T-3", "T-4"):
        assert estados(r)[regimen] == "indeterminado"
        assert atribuidas(r, regimen) == ["AC"]
    assert lecturas_de(r, "amlr", "AC") == {"AC-1": {"en_plazo"}, "AC-2": {"vencida"}}
    assert fechas(r, "amlr") == ["2028-09-01", "2029-08-20"]
    assert atribuciones_datos(r, "amlr", "AC") == ("cliente.revisiones[1] (R2)",)


def atribuciones_datos(resultado, regimen, dimension):
    (a,) = [a for a in resultado[regimen].atribuciones if a.dimension == dimension]
    return a.datos


# --- Ejemplo 4 --------------------------------------------------------------------


def ejemplo_4(reinicia=None):
    return calcular(
        entrada(
            "2031-03-01",
            "2028-01-10",
            [clasificacion("2028-01-10")],
            [revision("R1", "inicial", "2028-01-10"), revision("R2", "por_evento", "2029-06-15", eventos=["EV-1"])],
            [evento("EV-1", "cambio_titularidad_real_o_control", "2029-05-02", "2029-05-20")],
            versiones=[version(reinicia=reinicia)],
        )
    )


def test_ejemplo_4_revision_anticipada():
    r = ejemplo_4()
    assert set(estados(r).values()) == {"indeterminado"}
    assert fechas(r, "ley_rd") == ["2031-01-10", "2032-06-15"]
    assert atribuidas(r, "ley_rd") == ["RA"]
    ra = lecturas_de(r, "ley_rd", "RA")
    assert ra["RA-1"] == {"en_plazo"} and ra["RA-2"] == {"vencida"}
    # D-30: los datos de RA son las revisiones no periódicas.
    assert atribuciones_datos(r, "ley_rd", "RA") == ("cliente.revisiones[0] (R1)", "cliente.revisiones[1] (R2)")
    assert fechas(r, "amlr") == ["2031-01-10", "2032-06-15", "2033-01-10", "2034-06-15"]
    assert set(atribuidas(r, "amlr")) == {"RA", "PM"}
    # El evento está atendido: no queda pendiente en ninguna lectura.
    assert all(not h.eventos for h in r["ley_rd"].lecturas)


def test_ejemplo_4_con_el_manual_a_true():
    r = ejemplo_4(reinicia=True)
    assert set(estados(r).values()) == {"indeterminado"}
    ra = lecturas_de(r, "ley_rd", "RA")
    assert ra == {"RA-1": {"en_plazo"}, "RA-2": {"vencida"}, "RA-3": {"en_plazo"}}  # RA-3 como RA-1


# --- Ejemplo 5 --------------------------------------------------------------------


def ejemplo_5(tipo):
    return calcular(
        entrada(
            "2028-05-20",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01")],
            [evento("E", tipo, "2028-04-01", "2028-05-10")],
            versiones=[version("M", "2027-07-10", {"medio": 36}, plazo=30)],
        )
    )


def test_ejemplo_5a_cambio_de_titularidad():
    r = ejemplo_5("cambio_titularidad_real_o_control")
    assert estados(r)["amlr"] == "vencida"
    assert fechas(r, "amlr") == ["2028-05-01"]
    (h,) = {h.eventos for h in r["amlr"].lecturas}
    assert [(e.bases, e.fecha_activacion, e.fecha_limite) for e in h] == [(("AMLR 26.3.a",), D("2028-04-01"), D("2028-05-01"))]
    assert any("letra a)" in a for a in r["amlr"].avisos)
    assert estados(r)["ley_rd"] == "indeterminado"
    assert atribuidas(r, "ley_rd") == ["L72"]
    assert lecturas_de(r, "ley_rd", "L72") == {"L72-1": {"en_plazo"}, "L72-2": {"vencida"}}


def test_ejemplo_5b_informacion_de_riesgo():
    r = ejemplo_5("informacion_de_riesgo")
    assert estados(r)["amlr"] == "en_plazo"
    assert fechas(r, "amlr") == ["2028-06-09"]
    assert estados(r)["ley_rd"] == "indeterminado"
    assert set(atribuidas(r, "ley_rd")) == {"L72", "LC (informacion_de_riesgo)"}


def test_ejemplo_5c_operacion_significativa():
    r = ejemplo_5("operacion_significativa")
    assert estados(r)["amlr"] == "indeterminado"
    assert atribuidas(r, "amlr") == ["EV (operacion_significativa)"]
    assert lecturas_de(r, "amlr", "EV (operacion_significativa)") == {
        "EV-A": {"vencida"},
        "EV-C": {"en_plazo"},
        "EV-N": {"en_plazo"},
    }
    assert estados(r)["ley_rd"] == "indeterminado"


def test_ejemplo_5d_cambio_de_actividad():
    r = ejemplo_5("cambio_actividad")
    assert estados(r)["amlr"] == "vencida"
    assert estados(r)["ley_rd"] == "indeterminado"
    assert set(atribuidas(r, "ley_rd")) == {"FV", "L72"}
    hojas = {dict(h.lecturas).get("FV"): h for h in r["ley_rd"].lecturas if dict(h.lecturas).get("L72") == "L72-1"}
    assert (hojas["FV-1"].estado, hojas["FV-2"].estado) == ("vencida", "en_plazo")
    assert hojas["FV-2"].fecha_proxima_revision == D("2028-06-09")


def test_ejemplo_5_sin_plazo_en_el_manual():
    r = calcular(
        entrada(
            "2028-05-20",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01")],
            [evento("E", "cambio_titularidad_real_o_control", "2028-04-01", "2028-05-10")],
            versiones=[version("M", "2027-07-10", {"medio": 36})],
        )
    )
    assert estados(r)["amlr"] == "revision_pendiente_sin_plazo"
    (h,) = r["amlr"].lecturas[:1]
    assert [(e.fecha_activacion, e.fecha_limite, e.estado) for e in h.eventos] == [
        (D("2028-04-01"), None, "revision_pendiente_sin_plazo")
    ]


# --- Ejemplo 6 y D-30 -------------------------------------------------------------


def test_ejemplo_6_inicio_del_primer_periodo():
    r = calcular(
        entrada(
            "2028-10-10",
            "2027-10-01",
            [clasificacion("2027-09-20", "alto", True, True, True)],
            [revision("R1", "inicial", "2027-11-25")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )
    assert set(estados(r).values()) == {"indeterminado"}
    assert fechas(r, "ley_rd") == ["2028-09-20", "2028-10-01", "2028-11-25"]
    # D-30: IP solo cambia el estado junto con RA, y se atribuye igual.
    assert set(atribuidas(r, "ley_rd")) == {"RA", "IP"}
    por_combinacion = {
        (dict(h.lecturas).get("RA"), dict(h.lecturas).get("IP")): h.estado for h in r["ley_rd"].lecturas
    }
    assert por_combinacion[("RA-1", "IP-1")] == "en_plazo"
    assert por_combinacion[("RA-2", "IP-1")] == "vencida"
    assert por_combinacion[("RA-2", "IP-3")] == "vencida"
    assert por_combinacion[(None, "IP-2")] == "en_plazo"  # con IP-2, RA no cambia nada
    assert lecturas_de(r, "ley_rd", "IP")["IP-2"] == {"en_plazo"}


# --- Ejemplo 7 --------------------------------------------------------------------


def test_ejemplo_7_reclasificacion():
    r = calcular(
        entrada(
            "2029-06-01",
            "2027-12-01",
            [clasificacion("2027-12-01"), clasificacion("2029-03-15", "alto", True, True, True)],
            [revision("R1", "inicial", "2027-12-01")],
            versiones=[version(periodicidades={"medio": 36, "alto": 12})],
        )
    )
    assert set(estados(r).values()) == {"indeterminado"}
    assert fechas(r, "ley_rd") == ["2028-12-01", "2030-03-15", "2030-12-01"]
    assert lecturas_de(r, "ley_rd", "FR") == {"FR-1": {"en_plazo"}, "FR-2": {"vencida"}, "FR-3": {"en_plazo"}}
    assert fechas(r, "amlr") == ["2028-12-01", "2030-03-15", "2030-12-01", "2032-12-01"]
    assert atribuciones_datos(r, "ley_rd", "FR") == ("cliente.clasificaciones[1] (2029-03-15)",)


# --- Ejemplo 8 --------------------------------------------------------------------


def ejemplo_8(referencia):
    return calcular(
        entrada(
            referencia,
            "2015-06-01",
            [clasificacion("2015-06-01", "alto", True, None, None)],
            [revision("R1", "inicial", "2015-06-01"), revision("R2", "periodica", "2026-11-15")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )


def test_ejemplo_8_antes_del_vencimiento():
    r = ejemplo_8("2027-10-01")
    assert set(estados(r).values()) == {"en_plazo"}
    assert fechas(r, "amlr") == ["2027-11-15", "2031-11-15"]


def test_ejemplo_8_despues_del_vencimiento():
    r = ejemplo_8("2028-02-01")
    assert estados(r) == {
        "ley_rd": "vencida",
        "amlr": "indeterminado",
        "T-1": "vencida",
        "T-2": "indeterminado",
        "T-3": "vencida",
        "T-4": "vencida",
    }
    for regimen in ("ley_rd", "T-1", "T-3", "T-4"):
        assert fechas(r, regimen) == ["2027-11-15"]
    assert set(atribuidas(r, "T-2")) == {"NC", "PM"}
    assert not r.coincide_transicion


# --- Ejemplo 9 --------------------------------------------------------------------


def ejemplo_9(referencia):
    return calcular(
        entrada(
            referencia,
            "2012-02-01",
            [clasificacion("2012-02-01", "bajo", False, None, None), clasificacion("2027-07-10", "bajo")],
            [revision("R1", "inicial", "2012-02-01"), revision("R2", "periodica", "2024-01-15")],
            versiones=[version(periodicidades={"bajo": 120})],
        )
    )


@pytest.mark.parametrize(
    "referencia, t3",
    [("2030-01-01", "en_plazo"), ("2032-09-01", "vencida")],
)
def test_ejemplo_9_manual_mas_largo(referencia, t3):
    r = ejemplo_9(referencia)
    assert estados(r) == {
        "ley_rd": "en_plazo",
        "amlr": "vencida",
        "T-1": "en_plazo",
        "T-2": "vencida",
        "T-3": t3,
        "T-4": "vencida",
    }
    assert fechas(r, "ley_rd") == fechas(r, "T-1") == ["2034-01-15"]
    assert fechas(r, "amlr") == fechas(r, "T-2") == fechas(r, "T-4") == ["2029-01-15"]
    assert fechas(r, "T-3") == ["2032-07-10"]
    assert any("D-17" in a for a in r["amlr"].avisos)
