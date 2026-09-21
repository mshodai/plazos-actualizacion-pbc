"""Construcción de entradas para los tests del cálculo.

Las entradas se escriben como en el JSON y pasan por la carga, así que cada
test usa una entrada válida según el modelo.
"""

import json

from actualizacion.carga import cargar


def version(id_="M", desde="2000-01-01", periodicidades=None, plazo=None, reinicia=None):
    periodicidades = periodicidades if periodicidades is not None else {"medio": 36}
    return {
        "id": id_,
        "vigente_desde": desde,
        "periodicidades": [{"nivel_entidad": n, "meses": m} for n, m in periodicidades.items()],
        "plazo_revision_por_evento_dias": plazo,
        "revision_anticipada_reinicia_plazo": reinicia,
    }


def clasificacion(fecha, nivel="medio", superior=False, elevado=False, seccion_4=False):
    return {
        "fecha": fecha,
        "nivel_entidad": nivel,
        "superior_al_promedio": superior,
        "riesgo_elevado_amlr": elevado,
        "medidas_seccion_4_amlr": seccion_4,
    }


def revision(id_, tipo, fecha, resultado="actualizada", eventos=()):
    return {"id": id_, "tipo": tipo, "fecha": fecha, "resultado": resultado, "eventos": list(eventos)}


def evento(id_, tipo, hecho, conocimiento, relevante=True, **campos):
    datos = {
        "id": id_,
        "tipo": tipo,
        "fecha_hecho": hecho,
        "fecha_conocimiento": conocimiento,
        "relevante_segun_entidad": relevante,
        **campos,
    }
    if tipo == "otro":
        datos.setdefault("descripcion", "")
    return datos


def entrada(
    referencia,
    inicio,
    clasificaciones,
    revisiones=(),
    eventos=(),
    versiones=None,
    actividad="otra",
    terminacion=None,
):
    datos = {
        "version_modelo": 1,
        "fecha_referencia": referencia,
        "sujeto": {"actividad": actividad},
        "manual": {"versiones": versiones if versiones is not None else [version()]},
        "cliente": {
            "id": "C",
            "fecha_inicio_relacion": inicio,
            "fecha_terminacion_relacion": terminacion,
            "clasificaciones": list(clasificaciones),
            "revisiones": list(revisiones),
            "eventos": list(eventos),
        },
    }
    resultado = cargar(json.dumps(datos))
    assert resultado.valida, resultado.errores
    return resultado.entrada
