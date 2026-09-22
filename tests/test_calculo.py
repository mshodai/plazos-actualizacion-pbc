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
    assert any("su fecha límite era el 2022-01-10" in a for a in r["ley_rd"].avisos)


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


def test_evento_que_ninguna_norma_activa_en_su_periodo():
    # D-31: cambio de actividad con el hecho antes de A y el conocimiento después.
    # Con FV-2 y L72-1, el RD lo activa el 2027-08-01 (después de A) y el AMLR, por la
    # letra a), el 2027-06-01 (antes de A). Antes se descartaba en silencio.
    r = calcular(
        entrada(
            "2027-08-20",
            "2020-01-10",
            [clasificacion("2020-01-10")],
            [revision("R1", "inicial", "2020-01-10"), revision("R2", "periodica", "2025-06-01")],
            [evento("E", "cambio_actividad", "2027-06-01", "2027-08-01")],
            versiones=[version(plazo=30)],
        )
    )
    for t in ("T-1", "T-2", "T-3"):
        resultado = r[t]
        assert resultado.estado == "indeterminado"
        assert "TE" in [a.dimension for a in resultado.atribuciones]
        assert any("D-31" in a for a in resultado.avisos)
        te = {
            dict(h.lecturas)["TE"]: h
            for h in resultado.lecturas
            if dict(h.lecturas).get("FV") == "FV-2" and dict(h.lecturas).get("L72") == "L72-1"
        }
        assert [(e.bases, e.fecha_activacion, e.fecha_limite, e.estado) for e in te["TE-1"].eventos] == [
            (("RD 33.1.b",), D("2027-08-01"), D("2027-08-31"), "en_plazo")
        ]
        assert [(e.bases, e.fecha_activacion, e.fecha_limite, e.estado) for e in te["TE-2"].eventos] == [
            (("AMLR 26.3.a, desde A",), D("2027-07-10"), D("2027-08-09"), "vencida")
        ]
        assert te["TE-3"].eventos == ()
        assert te["TE-3"].estado == "en_plazo"
        # TE solo se consulta en esa combinación.
        assert all("TE" not in dict(h.lecturas) for h in resultado.lecturas if dict(h.lecturas).get("FV") == "FV-1")
    # Fuera de la transición no hay conflicto: ni `ley_rd`, ni `amlr`, ni T-4.
    for regimen in ("ley_rd", "amlr", "T-4"):
        assert all("TE" not in dict(h.lecturas) for h in r[regimen].lecturas)


def test_evento_que_las_dos_normas_activan_en_su_periodo():
    # D-32: información de riesgo con el hecho antes de A y el conocimiento después.
    # Con L72-2 y LC-2, la Ley 7.2 la activa el 2027-06-01 (antes de A) y la letra c)
    # del AMLR el 2027-08-01 (después). Antes ganaba el RD por comprobarse primero.
    r = calcular(
        entrada(
            "2027-08-20",
            "2020-01-10",
            [clasificacion("2020-01-10")],
            [revision("R1", "inicial", "2020-01-10"), revision("R2", "periodica", "2025-06-01")],
            [evento("E", "informacion_de_riesgo", "2027-06-01", "2027-08-01")],
            versiones=[version(plazo=30)],
        )
    )
    for t in ("T-1", "T-2", "T-3"):
        resultado = r[t]
        assert resultado.estado == "indeterminado"
        assert "TD" in [a.dimension for a in resultado.atribuciones]
        assert any("D-32" in a for a in resultado.avisos)
        td = {
            dict(h.lecturas)["TD"]: h
            for h in resultado.lecturas
            if dict(h.lecturas).get("L72") == "L72-2" and dict(h.lecturas).get("LC (informacion_de_riesgo)") == "LC-2"
        }
        assert [(e.bases, e.fecha_activacion, e.fecha_limite, e.estado) for e in td["TD-1"].eventos] == [
            (("Ley 7.2",), D("2027-06-01"), D("2027-07-01"), "vencida")
        ]
        assert [(e.bases, e.fecha_activacion, e.fecha_limite, e.estado) for e in td["TD-2"].eventos] == [
            (("AMLR 26.3.c",), D("2027-08-01"), D("2027-08-31"), "en_plazo")
        ]
        # TD solo se consulta cuando el RD activa el evento.
        assert all("TD" not in dict(h.lecturas) for h in resultado.lecturas if dict(h.lecturas).get("L72") == "L72-1")
    for regimen in ("ley_rd", "amlr", "T-4"):
        assert all("TD" not in dict(h.lecturas) for h in r[regimen].lecturas)


def test_revision_sin_cambios_posterior_a_a_en_t1_y_t3():
    # D-33: cliente de 2020, manual de 36 meses, revisión periódica del 2025-01-15 y
    # otra sin cambios del 2027-12-01. Con AC-2, el AMLR no la cuenta y el RD sí.
    r = calcular(
        entrada(
            "2028-03-01",
            "2020-01-10",
            [clasificacion("2020-01-10")],
            [
                revision("R1", "inicial", "2020-01-10"),
                revision("R2", "periodica", "2025-01-15"),
                revision("R3", "periodica", "2027-12-01", "sin_cambios"),
            ],
        )
    )
    assert r["ley_rd"].estado == "en_plazo"
    assert r["ley_rd"].fechas_proxima_revision == (D("2030-12-01"),)
    for t in ("T-1", "T-3"):
        resultado = r[t]
        assert resultado.estado == "indeterminado"
        assert {a.dimension for a in resultado.atribuciones} == {"AC", "TR"}
        assert any("D-33" in a for a in resultado.avisos)
        por_lectura = {}
        for h in resultado.lecturas:
            lecturas = dict(h.lecturas)
            por_lectura.setdefault((lecturas.get("AC"), lecturas.get("TR")), set()).add(
                tuple((p.norma, p.ancla, p.fecha_limite, h.estado) for p in h.periodicos)
            )
        assert por_lectura[("AC-2", "TR-1")] == {(("RD", D("2025-01-15"), D("2028-01-15"), "vencida"),)}
        assert por_lectura[("AC-2", "TR-2")] == {
            (("AMLR", D("2027-12-01"), D("2032-12-01"), "en_plazo"),),
            (("AMLR", D("2027-12-01"), D("2030-12-01"), "en_plazo"),),
        }
        # Con AC-1 las dos lecturas coinciden y TR no se consulta.
        assert (("AC-1", None)) in por_lectura
        assert all(k[1] is None for k in por_lectura if k[0] == "AC-1")
    # T-2 y T-4 no tienen periodo del RD que cerrar.
    for t in ("T-2", "T-4"):
        assert all("TR" not in dict(h.lecturas) for h in r[t].lecturas)


def test_empate_de_componentes_periodicos_en_t4():
    # D-34: RD y AMLR vencen el mismo día; se informan los dos.
    r = calcular(
        entrada(
            "2028-06-01",
            "2028-03-01",
            [clasificacion("2028-03-01", "alto", True, True, True)],
            [revision("R1", "inicial", "2028-03-01")],
            versiones=[version(periodicidades={"alto": 12})],
        )
    )
    (hoja,) = r["T-4"].lecturas
    assert [(p.norma, p.ancla, p.meses, p.fecha_limite) for p in hoja.periodicos] == [
        ("RD", D("2028-03-01"), 12, D("2029-03-01")),
        ("AMLR", D("2028-03-01"), 12, D("2029-03-01")),
    ]
    assert r["T-4"].fechas_proxima_revision == (D("2029-03-01"),)
    # Sin empate, un solo componente.
    (hoja,) = r["ley_rd"].lecturas
    assert [p.norma for p in hoja.periodicos] == ["RD"]


def test_empate_de_bases_de_un_evento():
    # D-34: el mismo día lo activan el RD 33.1.b (FV-1), la Ley 7.2 (L72-2) y, en T-4,
    # la letra a) del AMLR. Antes se elegía una por orden alfabético.
    r = calcular(
        entrada(
            "2028-05-20",
            "2027-10-01",
            [clasificacion("2027-10-01")],
            [revision("R1", "inicial", "2027-10-01")],
            [evento("E", "cambio_actividad", "2028-04-01", "2028-05-10")],
            versiones=[version("M", "2027-07-10", {"medio": 36}, plazo=30)],
        )
    )

    def bases(regimen, **lecturas):
        (hoja,) = [
            h for h in r[regimen].lecturas if all(dict(h.lecturas).get(k) == v for k, v in lecturas.items())
        ][:1]
        (evento_pendiente,) = hoja.eventos
        return evento_pendiente.bases, evento_pendiente.fecha_limite

    assert bases("ley_rd", FV="FV-1", L72="L72-1") == (("RD 33.1.b",), D("2028-05-01"))
    assert bases("ley_rd", FV="FV-1", L72="L72-2") == (("RD 33.1.b", "Ley 7.2"), D("2028-05-01"))
    assert bases("ley_rd", FV="FV-2", L72="L72-2") == (("Ley 7.2",), D("2028-05-01"))
    assert bases("T-4", FV="FV-1", L72="L72-2") == (("RD 33.1.b", "Ley 7.2", "AMLR 26.3.a"), D("2028-05-01"))
    assert bases("T-4", FV="FV-2", L72="L72-1") == (("AMLR 26.3.a",), D("2028-05-01"))


def test_relacion_terminada_sin_componentes():
    # D-22: sin próxima revisión no hay componente periódico: tupla vacía, no None.
    r = calcular(
        entrada(
            "2026-01-01",
            "2019-01-10",
            [clasificacion("2019-01-10")],
            [revision("R1", "inicial", "2019-01-10")],
            terminacion="2025-06-01",
        )
    )
    for regimen in r.regimenes:
        for h in regimen.lecturas:
            assert h.periodicos == ()
            assert h.eventos == ()
