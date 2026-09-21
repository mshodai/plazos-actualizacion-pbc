"""D-30: ningún `indeterminado` queda sin atribuir, y la atribución es la de la definición.

Se generan clientes al azar (con semilla fija) y, para cada régimen, se
expanden las hojas a todas las combinaciones completas de lecturas. Sobre ese
espacio se aplica la definición de D-30 por fuerza bruta: una dimensión causa el
`indeterminado` si hay dos combinaciones que solo difieren en ella y dan estados
distintos. El resultado tiene que coincidir con las atribuciones del cálculo.
"""

import functools
import itertools
import json
import random
from datetime import date, timedelta

import pytest

from actualizacion.calculo import INDETERMINADO, REGIMENES, calcular
from actualizacion.carga import cargar
from actualizacion.modelo import TIPOS_EVENTO

CASOS = 400
# Límite del recorrido por fuerza bruta: combinaciones por hojas.
MAXIMO_TRABAJO = 300_000


def _fecha(rng, desde, hasta):
    return desde + timedelta(days=rng.randint(0, (hasta - desde).days))


def _entrada_al_azar(rng):
    niveles = ["bajo", "medio", "alto"]
    inicio = _fecha(rng, date(2008, 1, 1), date(2029, 1, 1))
    referencia = _fecha(rng, inicio + timedelta(days=30), date(2034, 12, 31))

    versiones = []
    for i, desde in enumerate(sorted({_fecha(rng, date(2005, 1, 1), referencia) for _ in range(rng.randint(1, 2))})):
        versiones.append(
            {
                "id": f"M{i}",
                "vigente_desde": str(desde),
                "periodicidades": [
                    {"nivel_entidad": n, "meses": rng.choice([6, 12, 24, 36, 60, 84, 120])}
                    for n in rng.sample(niveles, rng.randint(1, 3))
                ],
                "plazo_revision_por_evento_dias": rng.choice([None, 30, 90]),
                "revision_anticipada_reinicia_plazo": rng.choice([None, True, False]),
            }
        )

    booleano = lambda: rng.choice([True, False, None])  # noqa: E731
    clasificaciones = [
        {
            "fecha": str(f),
            "nivel_entidad": rng.choice(niveles),
            "superior_al_promedio": booleano(),
            "riesgo_elevado_amlr": booleano(),
            "medidas_seccion_4_amlr": booleano(),
        }
        for f in sorted({_fecha(rng, inicio - timedelta(days=30), referencia) for _ in range(rng.randint(1, 3))})
    ]

    eventos = []
    for i in range(rng.randint(0, 2)):
        tipo = rng.choice(TIPOS_EVENTO)
        hecho = _fecha(rng, inicio, referencia)
        ev = {
            "id": f"E{i}",
            "tipo": tipo,
            "fecha_hecho": str(hecho),
            "fecha_conocimiento": str(_fecha(rng, hecho, referencia)),
            "relevante_segun_entidad": rng.random() < 0.8,
        }
        if tipo.startswith("obligacion"):
            ev["anio_natural"] = hecho.year
        if tipo == "otro":
            ev["descripcion"] = ""
        eventos.append(ev)

    revisiones = []
    for i in range(rng.randint(0, 3)):
        tipo = "inicial" if i == 0 and rng.random() < 0.7 else rng.choice(["periodica", "por_evento"])
        citados = [e["id"] for e in eventos if tipo == "por_evento" and rng.random() < 0.5]
        revisiones.append(
            {
                "id": f"R{i}",
                "tipo": tipo,
                "fecha": str(_fecha(rng, inicio, referencia)),
                "resultado": rng.choice(["actualizada", "actualizada", "sin_cambios", "no_completada"]),
                "eventos": citados,
            }
        )

    terminacion = None
    if rng.random() < 0.15:
        terminacion = str(_fecha(rng, inicio, referencia))

    datos = {
        "version_modelo": 1,
        "fecha_referencia": str(referencia),
        "sujeto": {"actividad": rng.choice(["otra", "otra", "otra", "agente_de_futbol"])},
        "manual": {"versiones": versiones},
        "cliente": {
            "id": "C",
            "fecha_inicio_relacion": str(inicio),
            "fecha_terminacion_relacion": terminacion,
            "clasificaciones": clasificaciones,
            "revisiones": revisiones,
            "eventos": eventos,
        },
    }
    resultado = cargar(json.dumps(datos))
    assert resultado.valida, resultado.errores
    return resultado.entrada


def _por_fuerza_bruta(resultado_regimen):
    """Dimensiones que cumplen D-30 sobre todas las combinaciones completas, o None
    si el espacio es demasiado grande para recorrerlo."""
    hojas = resultado_regimen.lecturas
    opciones: dict[str, list[str]] = {}
    for h in hojas:
        for dimension, lectura in h.lecturas:
            lista = opciones.setdefault(dimension, [])
            if lectura not in lista:
                lista.append(lectura)
    dimensiones = list(opciones)
    total = 1
    for d in dimensiones:
        total *= len(opciones[d])
    if total * len(hojas) > MAXIMO_TRABAJO:
        return None

    estado = {}
    for combinacion in itertools.product(*(opciones[d] for d in dimensiones)):
        completa = dict(zip(dimensiones, combinacion))
        encajan = [h for h in hojas if all(completa[d] == l for d, l in h.lecturas)]
        # Cada combinación está en una hoja como mucho; en ninguna si elige una
        # lectura que no existe en ese caso (D-11).
        assert len(encajan) <= 1, completa
        if encajan:
            estado[combinacion] = encajan[0].estado

    causantes = set()
    for combinacion, e in estado.items():
        for i, d in enumerate(dimensiones):
            for otra in opciones[d]:
                vecina = combinacion[:i] + (otra,) + combinacion[i + 1 :]
                if vecina in estado and estado[vecina] != e:
                    causantes.add(d)
    return causantes


@functools.cache
def _caso(semilla):
    """(resultado, {régimen: dimensiones por fuerza bruta o None}) de una semilla."""
    resultado = calcular(_entrada_al_azar(random.Random(semilla)))
    esperadas = {r.regimen: _por_fuerza_bruta(r) for r in resultado.regimenes if r.estado == INDETERMINADO}
    return resultado, esperadas


@pytest.mark.parametrize("semilla", range(CASOS))
def test_atribucion_coincide_con_la_definicion(semilla):
    resultado, esperadas = _caso(semilla)
    for regimen in REGIMENES:
        r = resultado[regimen]
        atribuidas = {a.dimension for a in r.atribuciones}
        if r.estado == INDETERMINADO:
            # Ningún indeterminado sin atribuir.
            assert atribuidas, (regimen, r.lecturas)
            for a in r.atribuciones:
                estados = {e for _, es in a.lecturas for e in es}
                assert len(estados) > 1, a
            if esperadas[regimen] is not None:
                assert atribuidas == esperadas[regimen], regimen
        else:
            assert not atribuidas


def test_la_muestra_tiene_indeterminados_verificados():
    """Que el test anterior no pase por no encontrar indeterminados, o por no poder
    recorrerlos por fuerza bruta."""
    indeterminados = verificados = 0
    for semilla in range(CASOS):
        _, esperadas = _caso(semilla)
        indeterminados += len(esperadas)
        verificados += sum(e is not None for e in esperadas.values())
    assert indeterminados > CASOS
    assert verificados > 0.8 * indeterminados
