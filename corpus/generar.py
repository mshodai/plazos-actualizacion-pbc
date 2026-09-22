"""Genera el corpus de corpus/: clientes sintéticos con su resultado esperado.

Uso, desde cualquier directorio: python corpus/generar.py

Cada caso es una entrada según docs/modelo-datos.md y un resultado esperado,
escrito a mano aquí a partir de docs/especificacion-calculo.md, no copiado
del cálculo. Antes de escribir nada, el script calcula cada caso con el
código de src/ y lo compara con lo esperado. Si alguno no coincide, termina
con error y no escribe ningún fichero.

Los datos son sintéticos y deterministas: cada ejecución produce exactamente
los mismos ficheros. Los identificadores dicen «FICTICIO» y las descripciones
«ficticio»; no hay nombres, NIF ni ningún dato que recuerde a una entidad o
persona real.

Por cada caso se escriben NN-nombre.json (la entrada) y
NN-nombre.esperado.json (qué demuestra y el resultado), y un README.md con la
lista. A = 2027-07-10 en todos los casos (sujeto con `actividad = "otra"`).
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent
# Usa siempre el código de src/, no una versión instalada del paquete.
sys.path.insert(0, str(DIRECTORIO.parent / "src"))

from actualizacion.calculo import REGIMENES  # noqa: E402
from actualizacion.carga import cargar  # noqa: E402
from actualizacion.cli import codigo_de_salida  # noqa: E402
from actualizacion.salida import como_dict, informe  # noqa: E402

# Estados, con nombres cortos para que las expectativas se lean de un vistazo.
EN_PLAZO = "en_plazo"
VENCIDA = "vencida"
INDET = "indeterminado"
TERMINADA = "relacion_terminada"

LEY, AMLR, T1, T2, T3, T4 = REGIMENES

# Preguntas de la salida (especificación, §10.2), tal como las da el informe.
P_AC = "¿Una revisión sin cambios cuenta como actualización para el AMLR?"
P_PB = "¿El plazo de un año del AMLR (art. 26.2.a) exige riesgo elevado y medidas de la sección 4, o basta uno?"
P_PM = "Si el manual fija un plazo más corto que el máximo del AMLR, ¿cuál es el de la revisión obligatoria?"
P_RA = "¿Una revisión hecha antes de tiempo reinicia el plazo de la siguiente?"
P_L72 = "¿El art. 7.2 de la Ley se aplica a cualquier cliente o solo a los que ya lo eran cuando entró en vigor?"
P_LC_RIESGO = "¿Un evento «informacion_de_riesgo» es un cambio de las circunstancias del cliente (Ley 7.2)?"
P_TD = "Un evento que las dos normas activan en su propio periodo: ¿cuál rige?"
P_TR = "¿Qué norma decide si una revisión posterior a A cierra el periodo del RD?"

LC_RIESGO = "LC (informacion_de_riesgo)"


# --- Construcción de las entradas --------------------------------------------------


def cliente(numero, referencia, inicio, clasificaciones, revisiones, periodicidades, eventos=(), plazo=None,
            terminacion=None):
    """Entrada de un cliente ficticio, con un manual de una sola versión."""
    return {
        "version_modelo": 1,
        "fecha_referencia": referencia,
        "sujeto": {"actividad": "otra"},
        "manual": {
            "versiones": [
                {
                    "id": "MANUAL-FICTICIO",
                    "vigente_desde": "2000-01-01",
                    "periodicidades": [{"nivel_entidad": n, "meses": m} for n, m in periodicidades.items()],
                    "plazo_revision_por_evento_dias": plazo,
                    "revision_anticipada_reinicia_plazo": None,
                }
            ]
        },
        "cliente": {
            "id": f"CLI-FICTICIO-{numero:02d}",
            "fecha_inicio_relacion": inicio,
            "fecha_terminacion_relacion": terminacion,
            "clasificaciones": list(clasificaciones),
            "revisiones": list(revisiones),
            "eventos": list(eventos),
        },
    }


def clasificacion(fecha, nivel, superior, elevado, seccion_4):
    return {
        "fecha": fecha,
        "nivel_entidad": nivel,
        "superior_al_promedio": superior,
        "riesgo_elevado_amlr": elevado,
        "medidas_seccion_4_amlr": seccion_4,
    }


def revision(n, tipo, fecha, resultado="actualizada", eventos=()):
    return {"id": f"REV-FICTICIO-{n}", "tipo": tipo, "fecha": fecha, "resultado": resultado, "eventos": list(eventos)}


def evento(n, tipo, hecho, conocimiento, descripcion):
    return {
        "id": f"EV-FICTICIO-{n}",
        "tipo": tipo,
        "descripcion": f"Hecho ficticio: {descripcion}",
        "fecha_hecho": hecho,
        "fecha_conocimiento": conocimiento,
        "relevante_segun_entidad": True,
    }


# --- Resultado esperado ------------------------------------------------------------


def resp(estados, fechas, depende=()):
    """Una respuesta de una decisión (D-36): estados, fechas y de qué depende aún."""
    return {"estados": sorted(estados), "fechas": list(fechas), "depende_de": sorted(depende)}


def dec(pregunta, respuestas):
    return {"pregunta": pregunta, "respuestas": respuestas}


def reg(estado, fechas, decisiones=None, eventos=(), avisos=()):
    """Un régimen: estado, fechas, decisiones por dimensión, eventos pendientes
    distintos y los códigos D-n de sus avisos."""
    return {
        "estado": estado,
        "fechas": list(fechas),
        "decisiones": decisiones or {},
        "eventos": sorted(eventos),
        "avisos": sorted(avisos),
    }


def resultado(codigo, regimenes):
    return {"codigo_salida": codigo, "regimenes": dict(zip(REGIMENES, regimenes))}


def resumen(inf):
    """Lo que se compara de cada caso, sacado de la salida en JSON (§10)."""
    datos = como_dict(inf)
    regimenes = {}
    for r in REGIMENES:
        d = datos["regimenes"][r]
        eventos = {
            (e["id"], tuple(e["bases"]), e["fecha_activacion"], e["fecha_limite"], e["estado"])
            for e in d["componentes"]["eventos"]
        }
        # \b: «TD-1» es una lectura, no la decisión D-1.
        avisos = {c for a in d["avisos"] for c in re.findall(r"\bD-\d+", a)}
        regimenes[r] = reg(
            d["estado"],
            d["fechas_proxima_revision"],
            {
                x["dimension"]: dec(
                    x["pregunta"],
                    {
                        y["lectura"]: resp(y["estados"], y["fechas_proxima_revision"], y["depende_de"])
                        for y in x["respuestas"]
                    },
                )
                for x in d["decisiones"]
            },
            [[i, list(b), act, lim, est] for i, b, act, lim, est in eventos],
            avisos,
        )
    return {"codigo_salida": codigo_de_salida(inf), "regimenes": regimenes}


# --- Los casos -----------------------------------------------------------------------


@dataclass(frozen=True)
class Caso:
    nombre: str
    demuestra: str
    entrada: dict
    esperado: dict


def _caso_01():
    # Cliente nuevo (inicio ≥ A), riesgo alto con los tres booleanos a true y manual de 12 meses.
    # RD: el menor de 12 y 12 (D-14). AMLR: L = 12 (26.2.a), manual igual: sin PM.
    # Ancla: la revisión inicial, que coincide con IP-1 a IP-3. Vence el 2029-02-01.
    # T-1 a T-3: el AMLR (cliente nuevo). T-4: empate RD y AMLR (D-34).
    todos = reg(EN_PLAZO, ["2029-02-01"])
    return Caso(
        "01-mismo-resultado-en-los-seis",
        "Cliente nuevo de riesgo alto, con los tres criterios de riesgo a true y un manual de 12 meses, revisado "
        "al darse de alta el 2028-02-01. Con el RD, el manual (12 meses, que es el mínimo anual del art. 11.2); con "
        "el AMLR, el año del art. 26.2.a. Los seis regímenes dan en_plazo con la misma fecha, el 2029-02-01, y no "
        "hay ninguna lectura que decidir: código 0.",
        cliente(1, "2028-09-01", "2028-02-01",
                [clasificacion("2028-02-01", "alto", True, True, True)],
                [revision(1, "inicial", "2028-02-01")],
                {"alto": 12}),
        resultado(0, [todos] * 6),
    )


def _caso_02():
    # Ejemplo 3 de la especificación. RD: la revisión sin cambios cuenta (§2.3): 2028-08-20 + 12.
    # AMLR: AC-1 igual; AC-2 no la cuenta, el ancla es la inicial: 2027-09-01 + 12 = 2028-09-01.
    ac = dec(P_AC, {
        "AC-1": resp([EN_PLAZO], ["2029-08-20"]),
        "AC-2": resp([VENCIDA], ["2028-09-01"]),
    })
    amlr = reg(INDET, ["2028-09-01", "2029-08-20"], {"AC": ac})
    return Caso(
        "02-revision-sin-cambios-vencida-con-ac-2",
        "Cliente de riesgo alto dado de alta el 2027-09-01, revisado a tiempo el 2028-08-20 sin encontrar cambios, "
        "a fecha 2029-01-10. Con el RD la revisión cuenta y vence el 2029-08-20: en_plazo. Con el AMLR depende de "
        "AC: si una revisión sin cambios es una «actualización» (AC-1), en_plazo; si no (AC-2), el periodo cuenta "
        "desde la inicial y está vencido desde el 2028-09-02, aunque la entidad revisó a tiempo (S-6, §2.3).",
        cliente(2, "2029-01-10", "2027-09-01",
                [clasificacion("2027-09-01", "alto", True, True, True)],
                [revision(1, "inicial", "2027-09-01"), revision(2, "periodica", "2028-08-20", "sin_cambios")],
                {"alto": 12}),
        resultado(1, [reg(EN_PLAZO, ["2029-08-20"]), amlr, amlr, amlr, amlr, amlr]),
    )


def _caso_03():
    # Ejemplo 9 de la especificación. Manual bajo = 120 meses (simplificadas, RD 17.1.b).
    # RD: 2024-01-15 + 120 = 2034-01-15. AMLR: 60 como máximo (D-17): 2029-01-15.
    # T-1: el periodo en curso el día A sigue con el RD. T-2: AMLR desde la última revisión.
    # T-3: el menor de 2034-01-15 y A + 60 = 2032-07-10. T-4: el más temprano, 2029-01-15.
    return Caso(
        "03-cliente-existente-transicion-diverge",
        "Cliente de riesgo bajo desde el 2012-02-01, con un manual de 120 meses por medidas simplificadas y la "
        "última revisión el 2024-01-15, calificado con el AMLR el 2027-07-10; a fecha 2030-01-01. Con el RD vence "
        "el 2034-01-15; con el AMLR, el 2029-01-15, porque el manual no puede superar cinco años (D-17). Las "
        "cuatro lecturas de la transición se separan: T-1 mantiene el RD (en_plazo), T-2 y T-4 aplican el AMLR "
        "(vencida) y T-3 cuenta cinco años desde el 2027-07-10 (en_plazo hasta el 2032-07-10).",
        cliente(3, "2030-01-01", "2012-02-01",
                [clasificacion("2012-02-01", "bajo", False, None, None),
                 clasificacion("2027-07-10", "bajo", False, False, False)],
                [revision(1, "inicial", "2012-02-01"), revision(2, "periodica", "2024-01-15")],
                {"bajo": 120}),
        resultado(1, [
            reg(EN_PLAZO, ["2034-01-15"]),
            reg(VENCIDA, ["2029-01-15"], avisos=["D-17"]),
            reg(EN_PLAZO, ["2034-01-15"]),
            reg(VENCIDA, ["2029-01-15"], avisos=["D-17"]),
            reg(EN_PLAZO, ["2032-07-10"], avisos=["D-17"]),
            reg(VENCIDA, ["2029-01-15"], avisos=["D-17"]),
        ]),
    )


def _caso_04():
    # Ejemplo 2 de la especificación. RD: superior al promedio, el menor de 36 y 12 (D-14, aviso).
    # AMLR: E = false, S4 = true. PB-1: 60, y PM entre 60 y 36; PB-2: 12, con el manual por encima (D-17).
    pb = dec(P_PB, {
        "PB-1": resp([EN_PLAZO], ["2031-03-01", "2033-03-01"]),
        "PB-2": resp([VENCIDA], ["2029-03-01"]),
    })
    amlr = reg(INDET, ["2029-03-01", "2031-03-01", "2033-03-01"], {"PB": pb}, avisos=["D-17"])
    return Caso(
        "04-persona-del-medio-politico",
        "Persona del medio político, cliente desde el 2028-03-01: la entidad la considera de riesgo superior al "
        "promedio con el RD, le aplica medidas de la sección 4 del AMLR (art. 42), pero no la considera de riesgo "
        "elevado. A fecha 2029-06-01, con el RD rige el plazo anual y está vencida desde el 2029-03-02. Con el "
        "AMLR depende de si el art. 26.2.a exige los dos elementos (PB-1: cinco años, en_plazo) o basta uno (PB-2: "
        "un año, vencida) (S-4). T-4, que aplica también el RD, da vencida.",
        cliente(4, "2029-06-01", "2028-03-01",
                [clasificacion("2028-03-01", "medio", True, False, True)],
                [revision(1, "inicial", "2028-03-01")],
                {"medio": 36}),
        resultado(1, [
            reg(VENCIDA, ["2029-03-01"], avisos=["D-14"]),
            amlr, amlr, amlr, amlr,
            reg(VENCIDA, ["2029-03-01"], avisos=["D-14", "D-17"]),
        ]),
    )


def _caso_05():
    # Ejemplo 4 de la especificación con un manual de 60 meses, igual al máximo del AMLR: sin PM,
    # y los seis regímenes dan lo mismo. RA-1: desde la revisión por evento, 2029-06-15 + 60.
    # RA-2: solo las periódicas; no hay: IP (todas 2028-01-10) + 60 = 2033-01-10.
    # RA-3 con el manual a null (D-10): hasta qué revisión reinician; la inicial es el propio ancla.
    ra = dec(P_RA, {
        "RA-1": resp([EN_PLAZO], ["2034-06-15"]),
        "RA-2": resp([VENCIDA], ["2033-01-10"]),
        "RA-3 (las revisiones con el manual a null no reinician)": resp([VENCIDA], ["2033-01-10"]),
        "RA-3 (reinician hasta REV-FICTICIO-1)": resp([VENCIDA], ["2033-01-10"]),
        "RA-3 (reinician hasta REV-FICTICIO-2)": resp([EN_PLAZO], ["2034-06-15"]),
    })
    todos = reg(INDET, ["2033-01-10", "2034-06-15"], {"RA": ra})
    return Caso(
        "05-revision-anticipada-puede-reiniciar",
        "Cliente de riesgo medio desde el 2028-01-10, con un manual de 60 meses que no dice si una revisión "
        "anticipada reinicia el plazo. Un cambio de titularidad provoca una revisión el 2029-06-15. A fecha "
        "2033-03-01, el «can reset» del borrador de la AMLA decide el estado en los seis regímenes: si la revisión "
        "reinicia el plazo (RA-1), vence el 2034-06-15; si no (RA-2), venció el 2033-01-10; si lo decide el manual "
        "(RA-3), como el manual calla, las dos cosas (S-3, D-10).",
        cliente(5, "2033-03-01", "2028-01-10",
                [clasificacion("2028-01-10", "medio", False, False, False)],
                [revision(1, "inicial", "2028-01-10"),
                 revision(2, "por_evento", "2029-06-15", eventos=["EV-FICTICIO-1"])],
                {"medio": 60},
                eventos=[evento(1, "cambio_titularidad_real_o_control", "2029-05-02", "2029-05-20",
                                "entrada de un socio inventado")]),
        resultado(1, [todos] * 6),
    )


def _caso_06():
    # Información de riesgo con el hecho el 2027-06-01 (antes de A) y el conocimiento el 2027-08-01.
    # Manual: 36 meses y 30 días para los eventos. Última revisión periódica el 2025-06-01.
    # RD: solo por la Ley 7.2 (L72-2) si es un cambio de circunstancias (LC-2): hecho + 30 = 2027-07-01.
    # AMLR: letra c), conocimiento + 30 = 2027-08-31. T-1 a T-3: con L72-2 y LC-2, las dos normas lo
    # activan en su periodo: TD (D-32). T-4: las dos, la más temprana.
    ley_evento = ["EV-FICTICIO-1", ["Ley 7.2"], "2027-06-01", "2027-07-01", VENCIDA]
    amlr_evento = ["EV-FICTICIO-1", ["AMLR 26.3.c"], "2027-08-01", "2027-08-31", EN_PLAZO]
    ambas = ["2027-07-01", "2027-08-31"]
    transicion = reg(INDET, ambas, {
        "L72": dec(P_L72, {
            "L72-1": resp([EN_PLAZO], ["2027-08-31"]),
            "L72-2": resp([EN_PLAZO, VENCIDA], ambas, [LC_RIESGO, "TD"]),
        }),
        LC_RIESGO: dec(P_LC_RIESGO, {
            "LC-1": resp([EN_PLAZO], ["2027-08-31"]),
            "LC-2": resp([EN_PLAZO, VENCIDA], ambas, ["L72", "TD"]),
        }),
        "TD": dec(P_TD, {
            "TD-1": resp([EN_PLAZO, VENCIDA], ambas, ["L72", LC_RIESGO]),
            "TD-2": resp([EN_PLAZO], ["2027-08-31"]),
        }),
    }, [ley_evento, amlr_evento], ["D-32"])
    return Caso(
        "06-evento-conocido-despues-del-10-de-julio-de-2027",
        "Cliente de riesgo medio desde el 2020-01-10. Una información de riesgo ocurre el 2027-06-01 y la entidad "
        "la conoce el 2027-08-01: el hecho y el conocimiento caen a distinto lado del 2027-07-10. El manual da 30 "
        "días para revisar tras un evento. A fecha 2027-08-20, con el AMLR (letra c, desde el conocimiento) la "
        "revisión vence el 2027-08-31: en_plazo. Con la Ley 7.2, si se aplica a este cliente (L72-2) y la "
        "información es un cambio de circunstancias (LC-2), cuenta desde el hecho y venció el 2027-07-01. En T-1 "
        "a T-3 las dos normas lo activan en su propio periodo, y además hay que decidir cuál rige (TD, D-32).",
        cliente(6, "2027-08-20", "2020-01-10",
                [clasificacion("2020-01-10", "medio", False, False, False)],
                [revision(1, "inicial", "2020-01-10"), revision(2, "periodica", "2025-06-01")],
                {"medio": 36},
                eventos=[evento(1, "informacion_de_riesgo", "2027-06-01", "2027-08-01",
                                "noticia adversa inventada sobre el cliente")],
                plazo=30),
        resultado(1, [
            reg(INDET, ["2027-07-01", "2028-06-01"], {
                "L72": dec(P_L72, {
                    "L72-1": resp([EN_PLAZO], ["2028-06-01"]),
                    "L72-2": resp([EN_PLAZO, VENCIDA], ["2027-07-01", "2028-06-01"], [LC_RIESGO]),
                }),
                LC_RIESGO: dec(P_LC_RIESGO, {
                    "LC-1": resp([EN_PLAZO], ["2028-06-01"]),
                    "LC-2": resp([EN_PLAZO, VENCIDA], ["2027-07-01", "2028-06-01"], ["L72"]),
                }),
            }, [ley_evento]),
            reg(EN_PLAZO, ["2027-08-31"], eventos=[amlr_evento]),
            transicion, transicion, transicion,
            reg(INDET, ambas, {
                "L72": dec(P_L72, {
                    "L72-1": resp([EN_PLAZO], ["2027-08-31"]),
                    "L72-2": resp([EN_PLAZO, VENCIDA], ambas, [LC_RIESGO]),
                }),
                LC_RIESGO: dec(P_LC_RIESGO, {
                    "LC-1": resp([EN_PLAZO], ["2027-08-31"]),
                    "LC-2": resp([EN_PLAZO, VENCIDA], ambas, ["L72"]),
                }),
            }, [ley_evento, amlr_evento]),
        ]),
    )


def _caso_07():
    # Cliente de 2020, manual de 36 meses, revisión periódica el 2025-01-15 y otra sin cambios el 2027-12-01.
    # RD: la cuenta: 2027-12-01 + 36 = 2030-12-01.
    # AMLR: AC-1: desde 2027-12-01, 60 (PM-1) o 36 (PM-2). AC-2: desde 2025-01-15, 60 o 36.
    # T-1 y T-3 (D-33): con AC-2, TR-1 (la juzga el AMLR) deja el periodo del RD de 2025: 2028-01-15;
    # TR-2 (la juzga el RD) pasa al AMLR desde 2027-12-01.
    # T-4: el más temprano del RD y el AMLR.
    amlr = reg(INDET, ["2028-01-15", "2030-01-15", "2030-12-01", "2032-12-01"], {
        "AC": dec(P_AC, {
            "AC-1": resp([EN_PLAZO], ["2030-12-01", "2032-12-01"]),
            "AC-2": resp([EN_PLAZO, VENCIDA], ["2028-01-15", "2030-01-15"], ["PM"]),
        }),
        "PM": dec(P_PM, {
            "PM-1": resp([EN_PLAZO], ["2030-01-15", "2032-12-01"]),
            "PM-2": resp([EN_PLAZO, VENCIDA], ["2028-01-15", "2030-12-01"], ["AC"]),
        }),
    })
    t1 = reg(INDET, ["2028-01-15", "2030-12-01", "2032-12-01"], {
        "AC": dec(P_AC, {
            "AC-1": resp([EN_PLAZO], ["2030-12-01", "2032-12-01"]),
            "AC-2": resp([EN_PLAZO, VENCIDA], ["2028-01-15", "2030-12-01", "2032-12-01"], ["TR"]),
        }),
        "TR": dec(P_TR, {
            "TR-1": resp([EN_PLAZO, VENCIDA], ["2028-01-15", "2030-12-01", "2032-12-01"], ["AC"]),
            "TR-2": resp([EN_PLAZO], ["2030-12-01", "2032-12-01"]),
        }),
    }, avisos=["D-33"])
    return Caso(
        "07-revision-de-2027-que-ninguna-norma-cuenta",
        "Cliente de riesgo medio desde el 2020-01-10, manual de 36 meses, revisado el 2025-01-15 y otra vez el "
        "2027-12-01 sin encontrar cambios; a fecha 2028-03-01. Con el RD la revisión de 2027 cuenta y vence el "
        "2030-12-01. En T-1 y T-3, si una revisión sin cambios no es una actualización (AC-2) y la juzga el AMLR "
        "por ser posterior al 2027-07-10 (TR-1), no cuenta para ninguna norma: el cliente sigue en el periodo del "
        "RD de 2025, que venció el 2028-01-15. Si la juzga el RD (TR-2), cierra ese periodo y está en plazo (D-33).",
        cliente(7, "2028-03-01", "2020-01-10",
                [clasificacion("2020-01-10", "medio", False, False, False)],
                [revision(1, "inicial", "2020-01-10"), revision(2, "periodica", "2025-01-15"),
                 revision(3, "periodica", "2027-12-01", "sin_cambios")],
                {"medio": 36}),
        resultado(1, [
            reg(EN_PLAZO, ["2030-12-01"]),
            amlr, t1, amlr, t1,
            reg(INDET, ["2028-01-15", "2030-01-15", "2030-12-01"], {
                "AC": dec(P_AC, {
                    "AC-1": resp([EN_PLAZO], ["2030-12-01"]),
                    "AC-2": resp([EN_PLAZO, VENCIDA], ["2028-01-15", "2030-01-15"], ["PM"]),
                }),
                "PM": dec(P_PM, {
                    "PM-1": resp([EN_PLAZO], ["2030-01-15", "2030-12-01"]),
                    "PM-2": resp([EN_PLAZO, VENCIDA], ["2028-01-15", "2030-12-01"], ["AC"]),
                }),
            }),
        ]),
    )


def _caso_08():
    # `superior_al_promedio` a null (D-15). RD: SP-1: el menor de 36 y 12 = 12, 2021-01-10;
    # SP-2: 36, 2023-01-10. AMLR: E y S4 a false: 60, PM con el manual (36): los dos en plazo.
    # Antes de A: T-1 a T-4 son el RD, y el AMLR lleva el aviso D-24.
    sp = dec("La clasificación del 2020-01-10 no dice si el riesgo es superior al promedio: ¿lo es?", {
        "SP-1": resp([VENCIDA], ["2021-01-10"]),
        "SP-2": resp([EN_PLAZO], ["2023-01-10"]),
    })
    # Con SP-1, el manual (36) supera el mínimo anual del RD: se recorta a 12, con aviso (D-14).
    ley = reg(INDET, ["2021-01-10", "2023-01-10"], {"SP (2020-01-10)": sp}, avisos=["D-14"])
    return Caso(
        "08-falta-un-dato-de-clasificacion",
        "Cliente desde el 2020-01-10 cuya clasificación no dice si su riesgo es superior al promedio "
        "(`superior_al_promedio = null`); a fecha 2021-06-01. Con el RD, si lo es, rige el plazo anual y está "
        "vencido; si no, los 36 meses del manual. La salida no plantea una lectura de la norma sino un dato que "
        "falta: «¿lo es?». Se sale del indeterminado completando la entrada (D-15, D-36). Con SP-1, además, el "
        "manual de 36 meses supera el mínimo anual y se recorta a 12, con aviso (D-14). El AMLR no usa ese dato.",
        cliente(8, "2021-06-01", "2020-01-10",
                [clasificacion("2020-01-10", "medio", None, False, False)],
                [revision(1, "inicial", "2020-01-10")],
                {"medio": 36}),
        resultado(1, [ley, reg(EN_PLAZO, ["2023-01-10", "2025-01-10"], avisos=["D-24"]), ley, ley, ley, ley]),
    )


def _caso_09():
    # Relación terminada el 2025-06-01 (D-22). Ese día la revisión ya estaba vencida en todos los
    # regímenes: RD 2022-01-10; AMLR 2024-01-10 (PM-1) o 2022-01-10 (PM-2). Aviso con D-2 y D-22.
    todos = reg(TERMINADA, [None], avisos=["D-2", "D-22"])
    return Caso(
        "09-relacion-terminada",
        "Cliente de riesgo medio con la relación terminada el 2025-06-01, a fecha 2026-01-01. No hay próxima "
        "revisión en ningún régimen: relacion_terminada, sin fecha (D-22). El aviso recuerda que el día de la "
        "terminación la revisión ya estaba vencida. Los seis coinciden: código 0.",
        cliente(9, "2026-01-01", "2019-01-10",
                [clasificacion("2019-01-10", "medio", False, False, False)],
                [revision(1, "inicial", "2019-01-10")],
                {"medio": 36},
                terminacion="2025-06-01"),
        resultado(0, [todos] * 6),
    )


def _caso_10():
    # Ejemplo 1 de la especificación con R = 2028-01-15. Cliente existente de riesgo medio desde el
    # 2020-03-02, revisado solo al darse de alta, manual de 36 meses.
    # RD: 2020-03-02 + 36 = 2023-03-02. AMLR: PM-1, 60 meses: 2025-03-02; PM-2, 36: 2023-03-02.
    # PM no cambia el estado: vencida con las dos, sin decisión.
    # T-1: el periodo en curso el día A es el del RD, ya vencido: 2023-03-02. T-2: amlr.
    # T-3: el primero entre el RD (2023-03-02) y A + P (2032 o 2030): 2023-03-02 (D-26).
    # T-4: la más temprana entre ley_rd y amlr: 2023-03-02.
    # D-41: vencida en los seis, los regímenes coinciden en el estado y hay que revisar: código 1.
    rd = reg(VENCIDA, ["2023-03-02"])
    amlr = reg(VENCIDA, ["2023-03-02", "2025-03-02"])
    return Caso(
        "10-vencida-en-los-seis",
        "Cliente de riesgo medio desde el 2020-03-02, con un manual de 36 meses y revisado solo al darse de alta; "
        "a fecha 2028-01-15. Con el RD venció el 2023-03-02; con el AMLR, el 2025-03-02 (PM-1) o el 2023-03-02 "
        "(PM-2). Los seis regímenes dan vencida: coinciden en el estado, pero hay que revisar al cliente. Código 1, "
        "porque alguna lectura exige actuar (D-41); con el criterio anterior, retirado (D-38), daba 0.",
        cliente(10, "2028-01-15", "2020-03-02",
                [clasificacion("2020-03-02", "medio", False, False, False)],
                [revision(1, "inicial", "2020-03-02")],
                {"medio": 36}),
        resultado(1, [rd, amlr, rd, amlr, rd, rd]),
    )


CASOS = [
    _caso_01(), _caso_02(), _caso_03(), _caso_04(), _caso_05(), _caso_06(), _caso_07(), _caso_08(), _caso_09(),
    _caso_10(),
]


# --- Autoverificación y escritura ------------------------------------------------------


def comprobar(caso):
    """Calcula el caso y devuelve las diferencias con lo esperado (vacío si coincide)."""
    carga = cargar(json.dumps(caso.entrada, ensure_ascii=False))
    if carga.errores:
        return [f"la entrada no es válida: {[e.codigo for e in carga.errores]}"]
    obtenido = resumen(informe(carga))
    diferencias = []
    if obtenido["codigo_salida"] != caso.esperado["codigo_salida"]:
        diferencias.append(
            f"codigo_salida: se esperaba {caso.esperado['codigo_salida']!r} y se obtuvo {obtenido['codigo_salida']!r}"
        )
    for regimen in REGIMENES:
        for parte in ("estado", "fechas", "decisiones", "eventos", "avisos"):
            esperado = caso.esperado["regimenes"][regimen][parte]
            calculado = obtenido["regimenes"][regimen][parte]
            if calculado != esperado:
                diferencias.append(f"{regimen}.{parte}: se esperaba {esperado!r} y se obtuvo {calculado!r}")
    return diferencias


def ficheros(caso):
    """Los dos ficheros de un caso: nombre → contenido."""
    esperado = {"caso": caso.nombre, "demuestra": caso.demuestra, "resultado": caso.esperado}
    return {f"{caso.nombre}.json": _json(caso.entrada), f"{caso.nombre}.esperado.json": _json(esperado)}


def readme():
    lineas = [
        "# Corpus",
        "",
        "Clientes sintéticos con su resultado esperado. Lo genera `corpus/generar.py`, que comprueba cada caso "
        "con el código de `src/` antes de escribirlo. No se edita a mano.",
        "",
        "```",
        "python corpus/generar.py",
        "```",
        "",
        "Cada caso tiene la entrada (`NN-nombre.json`, según `docs/modelo-datos.md`) y el resultado esperado "
        "(`NN-nombre.esperado.json`): en cada uno de los seis regímenes, el estado y las fechas de la próxima "
        "revisión en la fecha de referencia, las decisiones que hay que tomar para salir de cada `indeterminado` "
        "(con el estado y las fechas de cada respuesta y de qué depende aún), los eventos pendientes con sus "
        "bases y los códigos D-n de los avisos. Los resultados esperados están escritos a mano en `generar.py` a "
        "partir de `docs/especificacion-calculo.md`. El código de salida es el de `plazos-actualizacion` (§10.3): "
        "1 si alguna lectura de algún régimen exige actuar (`vencida`, `revision_pendiente_sin_plazo` o `sin_plazo`); "
        "0 si ninguna lo exige, aunque los regímenes discrepen (D-41).",
        "",
        "| Caso | Referencia | " + " | ".join(REGIMENES) + " | Código |",
        "|---|---|" + "---|" * len(REGIMENES) + "---|",
    ]
    for caso in CASOS:
        r = caso.esperado
        fila = [caso.nombre, caso.entrada["fecha_referencia"],
                *(r["regimenes"][g]["estado"] for g in REGIMENES), str(r["codigo_salida"])]
        lineas.append("| " + " | ".join(fila) + " |")
    lineas += ["", "## Qué demuestra cada caso", ""]
    for caso in CASOS:
        lineas += [f"**{caso.nombre}.** {caso.demuestra}", ""]
    return "\n".join(lineas).rstrip("\n") + "\n"


def _json(datos):
    return json.dumps(datos, ensure_ascii=False, indent=2) + "\n"


def main():
    fallos = [(caso.nombre, diferencias) for caso in CASOS if (diferencias := comprobar(caso))]
    if fallos:
        for nombre, diferencias in fallos:
            print(f"{nombre}:", *diferencias, sep="\n  ", file=sys.stderr)
        sys.exit(f"{len(fallos)} caso(s) no dan el resultado esperado: no se escribe nada")
    for caso in CASOS:
        for nombre, contenido in ficheros(caso).items():
            (DIRECTORIO / nombre).write_text(contenido, encoding="utf-8", newline="\n")
        print(f"Escrito corpus/{caso.nombre}.json y .esperado.json")
    (DIRECTORIO / "README.md").write_text(readme(), encoding="utf-8", newline="\n")
    print("Escrito corpus/README.md")


if __name__ == "__main__":
    main()
