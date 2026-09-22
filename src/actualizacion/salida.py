"""La salida: la próxima revisión en los seis regímenes, dónde difieren y qué
hay que decidir para salir de cada `indeterminado`.

`informe` calcula los seis regímenes sobre una entrada ya cargada y añade lo
que el cálculo no da por sí solo:

- la **comparación** entre regímenes: qué estados y fechas dan y dónde difieren;
- para cada `indeterminado`, la **pregunta** que hay que responder en cada
  dimensión que lo causa (D-30), y qué pasa con cada respuesta: el estado y la
  fecha que da, y si con ella el estado queda resuelto o aún depende de otras
  dimensiones (D-36);
- los **componentes** distintos de cada régimen, con en cuántas combinaciones de
  lecturas aparecen (D-37).

`texto` y `como_json` lo presentan, según el §10 de la especificación. Las
decisiones se citan como «D-n»; el resto de comentarios son de formato.
"""

import json
from dataclasses import dataclass
from datetime import date

from actualizacion.calculo import (
    AMLR,
    INDETERMINADO,
    LEY_RD,
    PENDIENTE_SIN_PLAZO,
    REGIMENES,
    SIN_PLAZO,
    TRANSICION,
    VENCIDA,
    EventoPendiente,
    Lectura,
    Periodico,
    ResultadoRegimen,
    atribuir,
    calcular,
    fecha_aplicacion,
)
from actualizacion.modelo import Incidencia, ResultadoCarga

ADVERTENCIA = (
    "Resultado de un cálculo bajo las lecturas que declara la especificación "
    "(docs/especificacion-calculo.md), no una determinación jurídica. Donde la norma no fija "
    "un dato, el cálculo da todas las lecturas y no elige; las decisiones propias se citan como D-n."
)

# --- Preguntas de cada dimensión (D-36) ----------------------------------------------
#
# Clave: el nombre de la dimensión, o su prefijo si lleva un parámetro entre
# paréntesis («SP (2020-01-10)», «EV (operacion_significativa)»). `{}` se
# sustituye por ese parámetro. Las lecturas se describen por su identificador
# o, en RA-3, por su prefijo.

_PREGUNTAS = {
    "IP": ("¿Desde qué fecha cuenta el primer periodo de revisión?", "S-1, §2.1"),
    "RA": ("¿Una revisión hecha antes de tiempo reinicia el plazo de la siguiente?", "S-3, §2.2"),
    "AC": ("¿Una revisión sin cambios cuenta como actualización para el AMLR?", "S-6, §2.3"),
    "FR": (
        "Si la clasificación o el manual cambian a mitad de un periodo, ¿cuáles rigen y desde cuándo?",
        "S-5, S-13, §2.4",
    ),
    "SP": ("La clasificación del {} no dice si el riesgo es superior al promedio: ¿lo es?", "S-17, D-15, §3.2"),
    "PB": (
        "¿El plazo de un año del AMLR (art. 26.2.a) exige riesgo elevado y medidas de la sección 4, o basta uno?",
        "S-4, §4.2",
    ),
    "NC": ("El cliente no está calificado con el AMLR: ¿qué plazo se le aplica?", "S-2, S-4, §4.2"),
    "PM": (
        "Si el manual fija un plazo más corto que el máximo del AMLR, ¿cuál es el de la revisión obligatoria?",
        "S-11, §4.2",
    ),
    "riesgo_elevado_amlr desconocido": (
        "La clasificación del {} no dice si hay riesgo elevado según el AMLR: ¿lo hay?",
        "S-17, D-15, §4.2",
    ),
    "medidas_seccion_4_amlr desconocido": (
        "La clasificación del {} no dice si se aplican medidas de la sección 4 del AMLR: ¿se aplican?",
        "S-17, D-15, §4.2",
    ),
    "FV": ("¿«Se verifique» (RD 33.1.b) es cuando ocurre el cambio o cuando la entidad lo conoce?", "S-8, §6.2"),
    "L72": (
        "¿El art. 7.2 de la Ley se aplica a cualquier cliente o solo a los que ya lo eran cuando entró en vigor?",
        "S-10, §6.2",
    ),
    "LC": ("¿Un evento «{}» es un cambio de las circunstancias del cliente (Ley 7.2)?", "S-9, §6.2"),
    "EV": ("¿A qué letra del art. 26.3 del AMLR corresponde un evento «{}»?", "S-9, §6.3"),
    "TE": (
        "Un evento que el RD activa en A o después y el AMLR antes de A: ¿qué norma lo rige?",
        "S-14, D-31, §5.2",
    ),
    "TD": ("Un evento que las dos normas activan en su propio periodo: ¿cuál rige?", "S-15, D-32, §5.2"),
    "TR": (
        "¿Qué norma decide si una revisión posterior a A cierra el periodo del RD?",
        "S-16, D-33, §5.2",
    ),
}

_LECTURAS = {
    "IP-1": "desde el inicio de la relación",
    "IP-2": "desde la revisión inicial",
    "IP-3": "desde la primera clasificación",
    "RA-1": "siempre lo reinicia",
    "RA-2": "nunca: solo las revisiones periódicas marcan el calendario",
    "RA-3": "lo decide el manual",
    "AC-1": "sí cuenta",
    "AC-2": "no cuenta",
    "FR-1": "los del inicio del periodo",
    "FR-2": "los vigentes en la fecha de referencia, desde el inicio del periodo",
    "FR-3": "los vigentes en la fecha de referencia, desde el cambio",
    "SP-1": "sí",
    "SP-2": "no",
    "PB-1": "hacen falta los dos",
    "PB-2": "basta uno",
    "NC-1": "cinco años, como «todos los demás clientes»",
    "NC-2": "el que corresponde a su calificación con el RD",
    "PM-1": "el máximo del AMLR",
    "PM-2": "el del manual",
    "true": "sí",
    "false": "no",
    "FV-1": "cuando ocurre",
    "FV-2": "cuando la entidad lo conoce",
    "L72-1": "solo a los clientes anteriores al 2010-04-30",
    "L72-2": "a cualquier cliente",
    "LC-1": "no",
    "LC-2": "sí",
    "EV-A": "letra a), desde la fecha del hecho",
    "EV-C": "letra c), desde la fecha de conocimiento",
    "EV-N": "ninguna: no activa una revisión",
    "TE-1": "el RD, en su fecha",
    "TE-2": "el AMLR, desde A",
    "TE-3": "ninguna",
    "TD-1": "el RD",
    "TD-2": "el AMLR",
    "TR-1": "el AMLR",
    "TR-2": "el RD, mientras dura su periodo",
}


def pregunta(dimension: str) -> tuple[str, str]:
    """(pregunta, referencia) de una dimensión."""
    nombre, _, resto = dimension.partition(" (")
    parametro = resto.rstrip(")")
    if dimension in _PREGUNTAS:
        texto, referencia = _PREGUNTAS[dimension]
    else:
        texto, referencia = _PREGUNTAS[nombre]
    return texto.format(parametro), referencia


def descripcion(lectura: str) -> str:
    if lectura in _LECTURAS:
        return _LECTURAS[lectura]
    if lectura.startswith("RA-3 ("):
        # RA-3 con el manual a null (D-10): la etiqueta ya dice hasta qué revisión.
        return _LECTURAS["RA-3"]
    return lectura


# --- Estructuras del informe ------------------------------------------------------


# D-41: los estados que exigen hacer algo con el cliente.
ESTADOS_QUE_EXIGEN_ACTUAR = frozenset({VENCIDA, PENDIENTE_SIN_PLAZO, SIN_PLAZO})


@dataclass(frozen=True)
class Activador:
    """D-41: una combinación de lecturas de un régimen que da un estado que exige actuar.

    `lecturas` está vacía si el régimen no tiene ninguna dimensión que decida.
    """

    regimen: str
    lecturas: tuple[str, ...]
    estado: str


@dataclass(frozen=True)
class RespuestaLectura:
    """Qué pasa si se responde con esta lectura (D-36).

    `depende_de`: las dimensiones que siguen causando un `indeterminado` con
    esta lectura fijada. Vacío si con ella el estado queda resuelto.
    """

    lectura: str
    descripcion: str
    estados: tuple[str, ...]
    fechas: tuple[date | None, ...]
    depende_de: tuple[str, ...]


@dataclass(frozen=True)
class Decision:
    """Una dimensión que causa el `indeterminado` (D-30), como pregunta (D-36)."""

    dimension: str
    pregunta: str
    referencia: str
    respuestas: tuple[RespuestaLectura, ...]
    datos: tuple[str, ...]


@dataclass(frozen=True)
class Componente:
    """Un componente distinto de un régimen y en cuántas combinaciones aparece (D-37)."""

    componente: Periodico | EventoPendiente
    combinaciones: int


@dataclass(frozen=True)
class InformeRegimen:
    resultado: ResultadoRegimen
    decisiones: tuple[Decision, ...]
    periodicos: tuple[Componente, ...]
    eventos: tuple[Componente, ...]

    @property
    def regimen(self) -> str:
        return self.resultado.regimen

    @property
    def estado(self) -> str:
        return self.resultado.estado

    @property
    def fechas(self) -> tuple[date | None, ...]:
        return self.resultado.fechas_proxima_revision


@dataclass(frozen=True)
class Informe:
    errores: tuple[Incidencia, ...]
    cliente_id: str | None = None
    fecha_referencia: date | None = None
    fecha_aplicacion_amlr: date | None = None
    regimenes: tuple[InformeRegimen, ...] = ()

    @property
    def valida(self) -> bool:
        return not self.errores

    def __getitem__(self, regimen: str) -> InformeRegimen:
        return next(r for r in self.regimenes if r.regimen == regimen)

    @property
    def estados(self) -> dict[str, str]:
        return {r.regimen: r.estado for r in self.regimenes}

    @property
    def estados_distintos(self) -> bool:
        return len(set(self.estados.values())) > 1

    @property
    def fechas_distintas(self) -> bool:
        return len({r.fechas for r in self.regimenes}) > 1

    @property
    def normas_difieren(self) -> bool:
        """D-28 y D-40: `ley_rd` frente a `amlr`, en estado o en fechas."""
        return self[LEY_RD].estado != self[AMLR].estado or self[LEY_RD].fechas != self[AMLR].fechas

    @property
    def transicion_difiere(self) -> bool:
        """D-28 y D-40: T-1 a T-4 entre sí, en estado o en fechas."""
        return len({(self[t].estado, self[t].fechas) for t in TRANSICION}) > 1

    @property
    def hay_indeterminado(self) -> bool:
        return INDETERMINADO in self.estados.values()

    @property
    def activadores(self) -> tuple[Activador, ...]:
        """D-41: cada régimen y combinación de lecturas que da un estado que exige actuar."""
        return tuple(
            Activador(r.regimen, tuple(valor for _, valor in lectura.lecturas), lectura.estado)
            for r in self.regimenes
            for lectura in r.resultado.lecturas
            if lectura.estado in ESTADOS_QUE_EXIGEN_ACTUAR
        )

    @property
    def exige_actuar(self) -> bool:
        """D-41: alguna lectura de algún régimen da un estado que exige actuar."""
        return bool(self.activadores)

    @property
    def grupos(self) -> dict[str, tuple[str, ...]]:
        """Estado → regímenes que lo dan, en el orden de REGIMENES."""
        grupos: dict[str, list[str]] = {}
        for regimen, estado in self.estados.items():
            grupos.setdefault(estado, []).append(regimen)
        return {estado: tuple(rs) for estado, rs in grupos.items()}


# --- Construcción -------------------------------------------------------------------


def informe(carga: ResultadoCarga) -> Informe:
    if not carga.valida:
        return Informe(errores=carga.errores)
    entrada = carga.entrada
    resultado = calcular(entrada)
    return Informe(
        errores=(),
        cliente_id=entrada.cliente.id,
        fecha_referencia=entrada.fecha_referencia,
        fecha_aplicacion_amlr=fecha_aplicacion(entrada.sujeto.actividad),
        regimenes=tuple(_informe_regimen(r) for r in resultado.regimenes),
    )


def _informe_regimen(resultado: ResultadoRegimen) -> InformeRegimen:
    decisiones = tuple(_decision(resultado, a.dimension, a.datos) for a in resultado.atribuciones)
    return InformeRegimen(
        resultado,
        decisiones,
        _distintos(resultado.lecturas, lambda h: h.periodicos),
        _distintos(resultado.lecturas, lambda h: h.eventos),
    )


def _con_lectura(hojas: tuple[Lectura, ...], dimension: str, lectura: str) -> list[Lectura]:
    """Las hojas compatibles con fijar `dimension` = `lectura`: las que la fijan así
    y las que no la consultan, que valen con cualquier lectura."""
    return [h for h in hojas if dict(h.lecturas).get(dimension, lectura) == lectura]


def _decision(resultado: ResultadoRegimen, dimension: str, datos: tuple[str, ...]) -> Decision:
    """D-36: la pregunta de la dimensión y qué pasa con cada respuesta."""
    lecturas: list[str] = []
    for h in resultado.lecturas:
        lectura = dict(h.lecturas).get(dimension)
        if lectura is not None and lectura not in lecturas:
            lecturas.append(lectura)
    respuestas = []
    for lectura in lecturas:
        hojas = _con_lectura(resultado.lecturas, dimension, lectura)
        estados = tuple(dict.fromkeys(h.estado for h in hojas))
        fechas = tuple(sorted({h.fecha_proxima_revision for h in hojas}, key=lambda f: (f is None, f)))
        # D-30 aplicado solo a esta lectura: lo que queda por decidir.
        depende = () if len(estados) == 1 else tuple(a.dimension for a in atribuir(hojas, {}))
        respuestas.append(RespuestaLectura(lectura, descripcion(lectura), estados, fechas, depende))
    texto, referencia = pregunta(dimension)
    return Decision(dimension, texto, referencia, tuple(respuestas), datos)


def _distintos(hojas, extraer) -> tuple[Componente, ...]:
    """Cada componente distinto y en cuántas combinaciones aparece, en orden (D-37)."""
    cuenta: dict = {}
    for h in hojas:
        for componente in extraer(h):
            cuenta[componente] = cuenta.get(componente, 0) + 1
    return tuple(Componente(c, n) for c, n in cuenta.items())


# --- JSON -------------------------------------------------------------------------


MAX_ACTIVADORES_TEXTO = 3


def _exige_actuar_texto(inf) -> list[str]:
    """D-41: qué régimen y qué lecturas exigen actuar, para que el código 1 se explique en el informe.

    Los regímenes con exactamente las mismas combinaciones, estados y nota se agrupan en una
    entrada. Después de agrupar, más de tres combinaciones en una entrada se resumen; el JSON las
    da todas.
    """
    if not inf.exige_actuar:
        return ["  No: ninguna lectura de ningún régimen exige actuar (D-41)."]
    por_regimen: dict[str, list[str]] = {}
    for a in inf.activadores:
        lecturas = " y ".join(a.lecturas) if a.lecturas else "sin lecturas que decidir"
        por_regimen.setdefault(a.regimen, []).append(f"{lecturas}: {a.estado}")
    grupos: dict[tuple, list[str]] = {}
    for regimen, combinaciones in por_regimen.items():
        estado = inf[regimen].estado
        nota = "" if estado in ESTADOS_QUE_EXIGEN_ACTUAR else f"estado del régimen: {estado}"
        grupos.setdefault((tuple(combinaciones), nota), []).append(regimen)
    lineas = ["  Sí (D-41). Lo exigen:"]
    for (combinaciones, nota), regimenes in grupos.items():
        lineas.append(f"    {', '.join(regimenes)}" + (f" ({nota})" if nota else "") + ":")
        mostradas = combinaciones[:MAX_ACTIVADORES_TEXTO]
        lineas += [f"      {c}" for c in mostradas]
        if resto := len(combinaciones) - len(mostradas):
            lineas.append(f"      y {resto} combinaciones más (todas en --json)")
    return lineas


def _fecha(valor):
    return valor.isoformat() if valor else None


def _periodico_dict(p: Periodico):
    return {
        "norma": p.norma,
        "ancla": _fecha(p.ancla),
        "meses": p.meses,
        "fecha_limite": _fecha(p.fecha_limite),
        "estado": p.estado,
    }


def _evento_dict(e: EventoPendiente):
    return {
        "id": e.id,
        "bases": list(e.bases),
        "fecha_activacion": _fecha(e.fecha_activacion),
        "fecha_limite": _fecha(e.fecha_limite),
        "estado": e.estado,
    }


def _regimen_dict(r: InformeRegimen):
    total = len(r.resultado.lecturas)
    return {
        "estado": r.estado,
        "fechas_proxima_revision": [_fecha(f) for f in r.fechas],
        "decisiones": [
            {
                "dimension": d.dimension,
                "pregunta": d.pregunta,
                "referencia": d.referencia,
                "respuestas": [
                    {
                        "lectura": x.lectura,
                        "descripcion": x.descripcion,
                        "estados": list(x.estados),
                        "fechas_proxima_revision": [_fecha(f) for f in x.fechas],
                        "resuelve": not x.depende_de,
                        "depende_de": list(x.depende_de),
                    }
                    for x in d.respuestas
                ],
                "datos": list(d.datos),
            }
            for d in r.decisiones
        ],
        "componentes": {
            "periodicos": [
                {**_periodico_dict(c.componente), "combinaciones": c.combinaciones} for c in r.periodicos
            ],
            "eventos": [{**_evento_dict(c.componente), "combinaciones": c.combinaciones} for c in r.eventos],
            "combinaciones": total,
        },
        "lecturas": [
            {
                "lecturas": dict(h.lecturas),
                "estado": h.estado,
                "fecha_proxima_revision": _fecha(h.fecha_proxima_revision),
                "periodicos": [_periodico_dict(p) for p in h.periodicos],
                "eventos": [_evento_dict(e) for e in h.eventos],
                "avisos": list(h.avisos),
            }
            for h in r.resultado.lecturas
        ],
        "avisos": list(r.resultado.avisos),
    }


def como_dict(inf: Informe) -> dict:
    datos = {
        "advertencia": ADVERTENCIA,
        "valida": inf.valida,
        "errores": [{"codigo": e.codigo, "mensaje": e.mensaje, "ruta": e.ruta} for e in inf.errores],
        "cliente": inf.cliente_id,
        "fecha_referencia": _fecha(inf.fecha_referencia),
        "fecha_aplicacion_amlr": _fecha(inf.fecha_aplicacion_amlr),
        "exige_actuar": None,
        "comparacion": None,
        "regimenes": {},
    }
    if inf.valida:
        datos["exige_actuar"] = {
            "valor": inf.exige_actuar,
            "activado_por": [
                {"regimen": a.regimen, "lecturas": list(a.lecturas), "estado": a.estado} for a in inf.activadores
            ],
        }
        datos["comparacion"] = {
            "estados_distintos": inf.estados_distintos,
            "fechas_distintas": inf.fechas_distintas,
            "hay_indeterminado": inf.hay_indeterminado,
            "normas_difieren": inf.normas_difieren,
            "transicion_difiere": inf.transicion_difiere,
            "grupos": [{"estado": e, "regimenes": list(rs)} for e, rs in inf.grupos.items()],
        }
        datos["regimenes"] = {r.regimen: _regimen_dict(r) for r in inf.regimenes}
    return datos


def como_json(inf: Informe) -> str:
    return json.dumps(como_dict(inf), ensure_ascii=False, indent=2)


# --- Texto ------------------------------------------------------------------------

ANCHO_REGIMEN = max(len(r) for r in REGIMENES)


# D-39: en texto, a partir de esta cantidad las fechas se resumen como intervalo.
MAXIMO_FECHAS_TEXTO = 3


def _fechas_texto(fechas) -> str:
    textos = [str(f) if f else "sin fecha" for f in fechas]
    if len(textos) <= MAXIMO_FECHAS_TEXTO:
        return " o ".join(textos)
    con_fecha = [f for f in fechas if f]
    resumen = f"entre el {min(con_fecha)} y el {max(con_fecha)} ({len(textos)} fechas posibles"
    return resumen + (", o sin fecha)" if None in fechas else ")")


def _periodico_texto(p: Periodico) -> str:
    if p.meses is None:
        return f"{p.norma}: desde el {p.ancla}, sin periodicidad ({p.estado})"
    return f"{p.norma}: desde el {p.ancla}, {p.meses} meses → vence el {p.fecha_limite} ({p.estado})"


def _evento_texto(e: EventoPendiente) -> str:
    limite = f"vence el {e.fecha_limite}" if e.fecha_limite else "sin plazo"
    return f"{e.id} · {', '.join(e.bases)} · activado el {e.fecha_activacion} · {limite} ({e.estado})"


def _componentes_texto(componentes, total, formato) -> list[str]:
    lineas = []
    for c in componentes:
        cuantas = "" if c.combinaciones == total else f"  [en {c.combinaciones} de {total} combinaciones]"
        lineas.append(f"      {formato(c.componente)}{cuantas}")
    return lineas


def _decision_texto(d: Decision) -> list[str]:
    lineas = [f"    {d.dimension} — {d.pregunta} ({d.referencia})"]
    for x in d.respuestas:
        estados = " o ".join(x.estados)
        fechas = _fechas_texto(x.fechas)
        if x.depende_de:
            resto = f"; aún depende de {', '.join(x.depende_de)}"
        else:
            resto = ""
        lineas.append(f"      {x.lectura} ({x.descripcion}): {estados}, {fechas}{resto}")
    if d.datos:
        lineas.append(f"      Datos: {'; '.join(d.datos)}")
    return lineas


def _clave_decisiones(r: InformeRegimen):
    return r.estado, r.fechas, r.decisiones


def _clave_componentes(r: InformeRegimen):
    return r.periodicos, r.eventos, len(r.resultado.lecturas)


def texto(inf: Informe) -> str:
    lineas: list[str] = []
    if not inf.valida:
        lineas.append(f"La entrada no es válida ({len(inf.errores)} errores):")
        for e in inf.errores:
            lineas.append(f"  {e.codigo}  {e.ruta or '(raíz)'}: {e.mensaje}")
        return "\n".join(lineas) + "\n"

    ref = inf.fecha_referencia
    lineas += [
        f"Cliente {inf.cliente_id}",
        f"Fecha de referencia: {ref} · AMLR aplicable desde el {inf.fecha_aplicacion_amlr}",
        "",
        ADVERTENCIA,
        "",
        f"Próxima revisión y estado el {ref}:",
    ]
    ancho_fechas = max(len(_fechas_texto(r.fechas)) for r in inf.regimenes)
    for r in inf.regimenes:
        lineas.append(f"  {r.regimen:<{ANCHO_REGIMEN}}  {_fechas_texto(r.fechas):<{ancho_fechas}}  {r.estado}")

    lineas += ["", "Dónde difieren:"]
    if not inf.estados_distintos and not inf.fechas_distintas:
        lineas.append("  Los seis regímenes coinciden en el estado y en la fecha.")
    else:
        if inf.normas_difieren:
            lineas.append("  ley_rd y amlr no coinciden: la norma cambia el resultado.")
        if inf.transicion_difiere:
            lineas.append(
                "  T-1 a T-4 no coinciden: el resultado depende de cómo se resuelva la transición del "
                f"{inf.fecha_aplicacion_amlr} (S-2, D-28)."
            )
        if inf.estados_distintos:
            lineas.append("  " + "; ".join(f"{', '.join(rs)}: {e}" for e, rs in inf.grupos.items()))
        else:
            lineas.append(f"  Mismo estado en los seis ({inf[LEY_RD].estado}), con fechas distintas.")
    if inf.hay_indeterminado:
        lineas.append("  «indeterminado»: las lecturas de ese régimen dan estados distintos (D-6).")

    lineas += ["", f"Exige actuar el {ref}:"]
    lineas += _exige_actuar_texto(inf)

    if inf.hay_indeterminado:
        lineas += ["", "Qué hay que decidir para salir del indeterminado (D-30, D-36):"]
        mostrados: dict = {}
        for r in inf.regimenes:
            if r.estado != INDETERMINADO:
                continue
            clave = _clave_decisiones(r)
            if clave in mostrados:
                # D-35.
                lineas.append(f"  {r.regimen}: lo mismo que {mostrados[clave]}")
                continue
            mostrados[clave] = r.regimen
            lineas.append(f"  {r.regimen}:")
            for d in r.decisiones:
                lineas += _decision_texto(d)

    lineas += ["", "Componentes (D-37):"]
    mostrados = {}
    for r in inf.regimenes:
        clave = _clave_componentes(r)
        if clave in mostrados:
            lineas.append(f"  {r.regimen}: los mismos que {mostrados[clave]}")
            continue
        mostrados[clave] = r.regimen
        total = len(r.resultado.lecturas)
        lineas.append(f"  {r.regimen}:")
        if r.periodicos:
            lineas.append("    Periódico:")
            lineas += _componentes_texto(r.periodicos, total, _periodico_texto)
        else:
            # D-22: con la relación terminada no hay próxima revisión.
            lineas.append("    Periódico: ninguno.")
        if r.eventos:
            lineas.append("    Por evento:")
            lineas += _componentes_texto(r.eventos, total, _evento_texto)
        else:
            lineas.append("    Por evento: ninguno pendiente.")

    avisos: dict[str, list[str]] = {}
    for r in inf.regimenes:
        for a in r.resultado.avisos:
            avisos.setdefault(a, []).append(r.regimen)
    if avisos:
        lineas += ["", "Avisos:"]
        for aviso, regimenes in avisos.items():
            lineas.append(f"  ({', '.join(regimenes)}) {aviso}")

    return "\n".join(lineas) + "\n"
