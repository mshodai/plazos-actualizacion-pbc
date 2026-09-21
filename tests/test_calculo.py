"""Reglas de docs/especificacion-calculo.md que los ejemplos del §9 no cubren."""

from datetime import date

import pytest

from actualizacion.calculo import calcular, sumar_dias, sumar_meses
from ayudas import clasificacion, entrada, evento, revision, version

D = date.fromisoformat


@pytest.mark.parametrize(
    "desde, meses, vence",
    [
        ("2027-08-31", 6, "2028-02-29"),
        ("2024-02-29", 12, "2025-02-28"),
        ("2020-03-02", 36, "2023-03-02"),
        ("2024-01-31", 1, "2024-02-29"),
        ("2023-12-15", 1, "2024-01-15"),
    ],
)
def test_sumar_meses(desde, meses, vence):
    # D-1.
    assert sumar_meses(D(desde), meses) == D(vence)


def test_sumar_dias():
    # D-3.
    assert sumar_dias(D("2028-04-01"), 30) == D("2028-05-01")


def test_el_dia_de_vencimiento_esta_en_plazo():
    # D-2.
    def en(referencia):
        return calcular(
            entrada(referencia, "2020-03-02", [clasificacion("2020-03-02")], [revision("R1", "inicial", "2020-03-02")])
        )["ley_rd"].estado

    assert en("2023-03-02") == "en_plazo"
    assert en("2023-03-03") == "vencida"


def test_relacion_terminada():
    # D-22: sin próxima revisión, con aviso de la revisión vencida ese día.
    r = calcular(
        entrada(
            "2026-01-01",
            "2019-01-10",
            [clasificacion("2019-01-10")],
            [revision("R1", "inicial", "2019-01-10")],
            terminacion="2025-06-01",
        )
    )
    assert set(r.estados.values()) == {"relacion_terminada"}
    assert r["ley_rd"].fechas_proxima_revision == (None,)
    assert any("vencida desde 2022-01-10" in a for a in r["ley_rd"].avisos)


def test_sin_periodicidad_en_el_manual():
    # D-16 con el RD; con el AMLR, el límite legal (PM-2 usa L).
    r = calcular(
        entrada("2026-01-01", "2020-01-10", [clasificacion("2020-01-10", "bajo")], [revision("R1", "inicial", "2020-01-10")])
    )
    assert r["ley_rd"].estado == "sin_plazo"
    assert r["ley_rd"].fechas_proxima_revision == (None,)
    assert r["amlr"].fechas_proxima_revision == (D("2025-01-10"),)


def test_riesgo_superior_sin_periodicidad_en_el_manual():
    # D-14: se aplica el mínimo anual del RD.
    r = calcular(
        entrada(
            "2020-06-01",
            "2020-01-10",
            [clasificacion("2020-01-10", "alto", True, True, True)],
            [revision("R1", "inicial", "2020-01-10")],
        )
    )
    assert r["ley_rd"].fechas_proxima_revision == (D("2021-01-10"),)


def test_superior_al_promedio_sin_calificar():
    # D-15: SP-1 y SP-2.
    r = calcular(
        entrada(
            "2021-06-01",
            "2020-01-10",
            [clasificacion("2020-01-10", "medio", None)],
            [revision("R1", "inicial", "2020-01-10")],
        )
    )
    assert r["ley_rd"].estado == "indeterminado"
    assert [a.dimension for a in r["ley_rd"].atribuciones] == ["SP (2020-01-10)"]


def test_revision_no_completada_no_cuenta():
    # D-8.
    r = calcular(
        entrada(
            "2024-01-01",
            "2020-01-10",
            [clasificacion("2020-01-10")],
            [revision("R1", "inicial", "2020-01-10"), revision("R2", "periodica", "2023-01-05", "no_completada")],
        )
    )
    assert r["ley_rd"].estado == "vencida"
    assert r["ley_rd"].fechas_proxima_revision == (D("2023-01-10"),)


def test_ip_2_no_existe_sin_revision_inicial_que_cuente():
    # D-11: con AC-2, la revisión inicial sin cambios no cuenta y la combinación
    # IP-2 × AC-2 no existe.
    r = calcular(
        entrada(
            "2028-09-01",
            "2027-08-01",
            [clasificacion("2027-08-15", "alto", True, True, True)],
            [revision("R1", "inicial", "2027-09-01", "sin_cambios")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )
    hojas = [dict(h.lecturas) for h in r["amlr"].lecturas]
    assert {"AC": "AC-2", "IP": "IP-2"} not in [{k: h.get(k) for k in ("AC", "IP")} for h in hojas]
    assert any(h.get("AC") == "AC-2" for h in hojas)
    assert any("D-11" in a for a in r["amlr"].avisos)


def test_evento_no_relevante():
    # D-18.
    r = calcular(
        entrada(
            "2028-05-20",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01")],
            [evento("E", "cambio_titularidad_real_o_control", "2028-04-01", "2028-05-10", relevante=False)],
            versiones=[version(plazo=30)],
        )
    )
    assert set(r.estados.values()) == {"en_plazo"}


def test_revision_no_completada_no_atiende_el_evento():
    # D-19.
    r = calcular(
        entrada(
            "2028-06-20",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01"), revision("R2", "por_evento", "2028-05-01", "no_completada", ["E"])],
            [evento("E", "informacion_de_riesgo", "2028-04-01", "2028-04-10")],
            versiones=[version(plazo=30)],
        )
    )
    assert r["amlr"].estado == "vencida"
    assert r["amlr"].fechas_proxima_revision == (D("2028-05-10"),)


def test_obligacion_de_contacto_vence_el_31_de_diciembre():
    # D-20: letra b), sin plazo en el manual.
    r = calcular(
        entrada(
            "2029-01-02",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01")],
            [evento("E", "obligacion_contacto_dac", "2028-03-01", "2028-03-01", anio_natural=2028)],
        )
    )
    assert r["amlr"].estado == "vencida"
    assert r["amlr"].fechas_proxima_revision == (D("2028-12-31"),)
    # La Ley 7.2 no recoge la Directiva 2011/16/UE.
    assert r["ley_rd"].estado == "en_plazo"


def test_obligacion_de_contacto_con_plazo_del_manual_mas_corto():
    r = calcular(
        entrada(
            "2028-12-01",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01")],
            [evento("E", "obligacion_contacto_dac", "2028-03-01", "2028-03-01", anio_natural=2028)],
            versiones=[version(plazo=30)],
        )
    )
    assert r["amlr"].fechas_proxima_revision == (D("2028-03-31"),)


def test_evento_anterior_a_a_en_la_transicion():
    # D-25: un cambio de titularidad de 2026 que el RD no cubre (cliente posterior a
    # 2010, L72-1) no se convierte en revisión exigible con el AMLR desde A.
    r = calcular(
        entrada(
            "2028-01-10",
            "2020-01-10",
            [clasificacion("2020-01-10")],
            [revision("R1", "inicial", "2020-01-10"), revision("R2", "periodica", "2025-06-01")],
            [evento("E", "cambio_titularidad_real_o_control", "2026-05-01", "2026-05-02")],
            versiones=[version(plazo=30)],
        )
    )
    assert r["amlr"].estado == "vencida"  # el AMLR aplicado solo, a toda la historia
    for t in ("T-1", "T-2", "T-3"):
        assert r[t].estado == "indeterminado"
        assert [a.dimension for a in r[t].atribuciones] == ["L72"]
    # T-4 aplica las dos normas: con el AMLR, vencido desde 2026.
    assert r["T-4"].estado == "vencida"


def test_fecha_de_aplicacion_para_agentes_de_futbol():
    # §1.1: A = 2029-07-10; antes, los T-n son `ley_rd`.
    datos = dict(
        inicio="2020-03-02",
        clasificaciones=[clasificacion("2020-03-02", "bajo")],
        revisiones=[revision("R1", "inicial", "2020-03-02")],
        versiones=[version(periodicidades={"bajo": 120})],
    )
    otra = calcular(entrada("2028-01-01", **datos))
    futbol = calcular(entrada("2028-01-01", actividad="agente_de_futbol", **datos))
    assert otra["T-2"].estado == "vencida"
    assert futbol["T-2"].estado == "en_plazo"
    assert any("2029-07-10" in a for a in futbol["amlr"].avisos)


def test_t1_pasa_al_amlr_con_la_primera_revision_posterior_a_a():
    # D-27: desde esa revisión, AMLR con ella de ancla.
    r = calcular(
        entrada(
            "2031-01-01",
            "2012-02-01",
            [clasificacion("2012-02-01", "bajo")],
            [revision("R1", "inicial", "2012-02-01"), revision("R2", "periodica", "2028-01-15")],
            versiones=[version(periodicidades={"bajo": 120})],
        )
    )
    assert r["T-1"].fechas_proxima_revision == (D("2033-01-15"),)
    assert r["ley_rd"].fechas_proxima_revision == (D("2038-01-15"),)


def test_regimenes_en_orden():
    r = calcular(
        entrada("2024-06-01", "2020-03-02", [clasificacion("2020-03-02")], [revision("R1", "inicial", "2020-03-02")])
    )
    assert [x.regimen for x in r.regimenes] == ["ley_rd", "amlr", "T-1", "T-2", "T-3", "T-4"]
