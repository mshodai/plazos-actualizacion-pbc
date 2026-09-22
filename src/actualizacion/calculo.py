"""Cálculo de la próxima revisión obligatoria, según docs/especificacion-calculo.md.

`calcular` recibe una entrada validada (actualizacion.carga) y devuelve, en la
fecha de referencia, el estado y la fecha de la próxima revisión en los seis
regímenes (especificación, §1.1), con sus lecturas y la atribución de cada
`indeterminado` (D-30).

Cómo se recorren las lecturas: el cálculo de un régimen se ejecuta con unas
lecturas fijadas. Cuando necesita una dimensión que aún no está fijada y sus
opciones dan valores distintos, se interrumpe, y `_explorar` lo vuelve a
ejecutar con cada opción. Cada ejecución completa es una hoja: la combinación de
las dimensiones que ha consultado de verdad, con su resultado. Una dimensión
cuyas opciones dan el mismo valor no se consulta, porque no puede cambiar nada.

Las decisiones de la especificación se citan como «D-n»; las lecturas, por su
identificador (RA-2, EV-C...).
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import combinations

from actualizacion.modelo import (
    ACTUALIZADA,
    INICIAL,
    NO_COMPLETADA,
    OTRO,
    PERIODICA,
    SIN_CAMBIOS,
    TIPOS_CONTACTO,
    Entrada,
)

# --- Constantes ----------------------------------------------------------------

LEY_RD = "ley_rd"
AMLR = "amlr"
REGIMENES = (LEY_RD, AMLR, "T-1", "T-2", "T-3", "T-4")
TRANSICION = ("T-1", "T-2", "T-3", "T-4")

EN_PLAZO = "en_plazo"
VENCIDA = "vencida"
PENDIENTE_SIN_PLAZO = "revision_pendiente_sin_plazo"
SIN_PLAZO = "sin_plazo"
RELACION_TERMINADA = "relacion_terminada"
INDETERMINADO = "indeterminado"

# D-23: prioridad de los estados de los componentes dentro de una lectura.
_PRIORIDAD = (VENCIDA, PENDIENTE_SIN_PLAZO, SIN_PLAZO, EN_PLAZO)

# Especificación, §1.1 (AMLR, art. 90).
APLICACION_AMLR = date(2027, 7, 10)
APLICACION_AMLR_FUTBOL = date(2029, 7, 10)
# Especificación, §6.2 (Ley, disposición final séptima).
ENTRADA_EN_VIGOR_LEY = date(2010, 4, 30)

# Normas con que se cuentan las revisiones y se calcula el plazo.
_RD = "RD"
_AMLR = "AMLR"

# §6.2: tipos que recoge la Ley 7.2. Información de riesgo y `otro`, según LC-n.
_LEY_7_2 = (
    "cambio_actividad",
    "cambio_identidad",
    "cambio_titularidad_real_o_control",
    "cambio_situacion_financiera",
    "nuevo_producto",
    "operacion_significativa",
    "obligacion_contacto_titularidad_real",
)
_LEY_7_2_SEGUN_LC = ("informacion_de_riesgo", OTRO)

# §6.3: letra del art. 26.3 de cada tipo; las tuplas son las lecturas EV-n.
_LETRA_AMLR = {
    "cambio_actividad": "a",
    "cambio_identidad": "a",
    "cambio_titularidad_real_o_control": "a",
    "cambio_situacion_financiera": "a",
    "nuevo_producto": ("EV-A", "EV-N"),
    "operacion_significativa": ("EV-A", "EV-C", "EV-N"),
    "anomalia_operativa": ("EV-A", "EV-C", "EV-N"),
    OTRO: ("EV-A", "EV-C", "EV-N"),
    "informacion_de_riesgo": "c",
    "obligacion_contacto_titularidad_real": "b",
    "obligacion_contacto_dac": "b",
}
_LETRA_DE_LECTURA = {"EV-A": "a", "EV-C": "c", "EV-N": None}


# --- Fechas (§1.3) ---------------------------------------------------------------


def sumar_meses(fecha: date, meses: int) -> date:
    """D-1: mismo día, N meses después; si no existe, el último día del mes."""
    total = fecha.month - 1 + meses
    anio, mes = fecha.year + total // 12, total % 12 + 1
    return date(anio, mes, min(fecha.day, calendar.monthrange(anio, mes)[1]))


def sumar_dias(fecha: date, dias: int) -> date:
    """D-3: días naturales."""
    return fecha + timedelta(days=dias)


def fecha_aplicacion(actividad: str) -> date:
    """A (§1.1)."""
    if actividad in ("agente_de_futbol", "club_de_futbol_profesional"):
        return APLICACION_AMLR_FUTBOL
    return APLICACION_AMLR


def _mas_temprana(candidatas):
    """(fecha más temprana, todas las bases con esa fecha), o None si no hay
    candidatas. `candidatas` es una lista de (fecha, base), en orden (D-21, D-34)."""
    if not candidatas:
        return None
    primera = min(f for f, _ in candidatas)
    bases = []
    for f, b in candidatas:
        if f == primera and b not in bases:
            bases.append(b)
    return primera, tuple(bases)


# --- Resultado -------------------------------------------------------------------


@dataclass(frozen=True)
class Periodico:
    """Componente periódico (§1.2). `fecha_limite` None: sin plazo (D-16)."""

    norma: str
    ancla: date
    meses: int | None
    fecha_limite: date | None
    estado: str


@dataclass(frozen=True)
class EventoPendiente:
    """Evento que activa una revisión y no está atendido (§6).

    `bases`: todos los supuestos que lo activan en `fecha_activacion`, en el orden
    RD 33.1.b, Ley 7.2, AMLR. Si varios empatan, se informan todos (D-34).
    """

    id: str
    bases: tuple[str, ...]
    fecha_activacion: date
    fecha_limite: date | None
    estado: str


@dataclass(frozen=True)
class Lectura:
    """Una hoja: las lecturas consultadas, en orden, y su resultado.

    `lecturas` solo tiene las dimensiones que han cambiado algo en este
    recorrido. Las demás pueden tomar cualquier valor sin cambiar el resultado.
    """

    lecturas: tuple[tuple[str, str], ...]
    estado: str
    fecha_proxima_revision: date | None
    # Uno, o varios si empatan en la fecha límite (D-34). Vacío solo con
    # `relacion_terminada`, que no tiene próxima revisión (D-22).
    periodicos: tuple[Periodico, ...]
    eventos: tuple[EventoPendiente, ...]
    avisos: tuple[str, ...]


@dataclass(frozen=True)
class Atribucion:
    """D-30: una dimensión que causa el `indeterminado`.

    `lecturas`: cada lectura de la dimensión con los estados que da.
    `datos`: los datos de la entrada que ponen la dimensión en juego.
    """

    dimension: str
    lecturas: tuple[tuple[str, tuple[str, ...]], ...]
    datos: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoRegimen:
    regimen: str
    estado: str
    fechas_proxima_revision: tuple[date | None, ...]
    lecturas: tuple[Lectura, ...]
    atribuciones: tuple[Atribucion, ...]
    avisos: tuple[str, ...]

    @property
    def fecha_proxima_revision(self) -> date | None:
        """La fecha si todas las lecturas coinciden (D-5); si no, None."""
        return self.fechas_proxima_revision[0] if len(self.fechas_proxima_revision) == 1 else None


@dataclass(frozen=True)
class ResultadoCliente:
    fecha_referencia: date
    regimenes: tuple[ResultadoRegimen, ...]

    def __getitem__(self, regimen: str) -> ResultadoRegimen:
        for r in self.regimenes:
            if r.regimen == regimen:
                return r
        raise KeyError(regimen)

    @property
    def estados(self) -> dict[str, str]:
        return {r.regimen: r.estado for r in self.regimenes}

    @property
    def coinciden_normas(self) -> bool:
        """D-28: `ley_rd` frente a `amlr`."""
        return self[LEY_RD].estado == self[AMLR].estado

    @property
    def coincide_transicion(self) -> bool:
        """D-28: T-1 a T-4 entre sí."""
        return len({self[t].estado for t in TRANSICION}) == 1


def calcular(entrada: Entrada) -> ResultadoCliente:
    """Los seis regímenes en `entrada.fecha_referencia` (D-4)."""
    return ResultadoCliente(
        entrada.fecha_referencia,
        tuple(calcular_regimen(entrada, regimen) for regimen in REGIMENES),
    )


def calcular_regimen(entrada: Entrada, regimen: str) -> ResultadoRegimen:
    datos: dict[str, list[str]] = {}
    hojas = _explorar(lambda eleccion: _Evaluador(entrada, eleccion).evaluar(regimen), datos)
    estados = {h.estado for h in hojas}
    estado = estados.pop() if len(estados) == 1 else INDETERMINADO  # D-6
    fechas = sorted({h.fecha_proxima_revision for h in hojas}, key=lambda f: (f is None, f))
    avisos = []
    for h in hojas:
        avisos.extend(a for a in h.avisos if a not in avisos)
    atribuciones = atribuir(hojas, datos) if estado == INDETERMINADO else ()
    return ResultadoRegimen(regimen, estado, tuple(fechas), tuple(hojas), atribuciones, tuple(avisos))


# --- Recorrido de las lecturas -------------------------------------------------------


class _Bifurcar(Exception):
    def __init__(self, dimension, opciones):
        self.dimension = dimension
        self.opciones = opciones


class _Imposible(Exception):
    """La combinación elige una lectura que no existe en este caso (D-11)."""


_NO_DISPONIBLE = object()


class _Eleccion:
    """Las lecturas fijadas en un recorrido y las que se han consultado."""

    def __init__(self, fijadas, datos):
        self.fijadas = fijadas
        self.consultadas: dict[str, str] = {}
        self.datos = datos

    def elegir_clave(self, dimension, opciones, datos=()):
        """La opción que rige. `opciones` es {lectura: valor}, en orden.

        Si todas las opciones disponibles dan el mismo valor, no se consulta la
        dimensión y se devuelve la primera: no puede cambiar el resultado.
        """
        disponibles = {k: v for k, v in opciones.items() if v is not _NO_DISPONIBLE}
        valores = list(disponibles.values())
        if all(v == valores[0] for v in valores):
            return next(iter(disponibles))
        registro = self.datos.setdefault(dimension, [])
        registro.extend(d for d in datos if d not in registro)
        if dimension not in self.fijadas:
            raise _Bifurcar(dimension, tuple(opciones))
        clave = self.fijadas[dimension]
        self.consultadas[dimension] = clave
        if clave not in disponibles:
            raise _Imposible
        return clave

    def elegir(self, dimension, opciones, datos=()):
        return opciones[self.elegir_clave(dimension, opciones, datos)]


def _explorar(funcion, datos):
    """Todas las hojas del cálculo, en orden de recorrido."""
    hojas = []
    pendientes = [{}]
    while pendientes:
        fijadas = pendientes.pop(0)
        eleccion = _Eleccion(fijadas, datos)
        try:
            resultado = funcion(eleccion)
        except _Bifurcar as b:
            pendientes[0:0] = [{**fijadas, b.dimension: opcion} for opcion in b.opciones]
            continue
        except _Imposible:
            continue
        hojas.append(
            Lectura(
                tuple(eleccion.consultadas.items()),
                resultado.estado,
                resultado.fecha_proxima_revision,
                resultado.periodicos,
                resultado.eventos,
                resultado.avisos,
            )
        )
    return hojas


def atribuir(hojas, datos):
    """D-30: una dimensión causa el `indeterminado` si, en alguna combinación de
    las demás, cambiar solo esa cambia el estado.

    Dos hojas con estados distintos que se contradicen en una sola dimensión son
    dos combinaciones que solo difieren en ella: las demás dimensiones, o
    coinciden, o alguna de las dos hojas no las ha consultado y admiten
    cualquier valor. Y si dos combinaciones que solo difieren en D dan estados
    distintos, sus hojas se contradicen exactamente en D. Por eso basta con
    mirar los pares de hojas.
    """
    causantes = []
    for a, b in combinations(hojas, 2):
        if a.estado == b.estado:
            continue
        la, lb = dict(a.lecturas), dict(b.lecturas)
        contradicciones = [d for d in la if d in lb and la[d] != lb[d]]
        if len(contradicciones) == 1 and contradicciones[0] not in causantes:
            causantes.append(contradicciones[0])

    atribuciones = []
    for dimension in causantes:
        por_lectura: dict[str, list[str]] = {}
        for h in hojas:
            lectura = dict(h.lecturas).get(dimension)
            if lectura is not None:
                estados = por_lectura.setdefault(lectura, [])
                if h.estado not in estados:
                    estados.append(h.estado)
        atribuciones.append(
            Atribucion(
                dimension,
                tuple((lectura, tuple(e)) for lectura, e in por_lectura.items()),
                tuple(datos.get(dimension, ())),
            )
        )
    return tuple(atribuciones)


# --- Evaluación de una combinación ------------------------------------------------


@dataclass(frozen=True)
class _Resultado:
    estado: str
    fecha_proxima_revision: date | None
    periodicos: tuple[Periodico, ...]
    eventos: tuple[EventoPendiente, ...]
    avisos: tuple[str, ...]


class _Evaluador:
    def __init__(self, entrada: Entrada, eleccion: _Eleccion, referencia: date | None = None):
        self.entrada = entrada
        self.e = eleccion
        self.ref = referencia or entrada.fecha_referencia
        self.cliente = entrada.cliente
        self.versiones = entrada.manual.versiones
        self.A = fecha_aplicacion(entrada.sujeto.actividad)
        self.revisiones = [r for r in self.cliente.revisiones if r.fecha <= self.ref]
        self.avisos: list[str] = []
        # RA-3 (§2.2, D-10): las revisiones no periódicas con el manual a null, en
        # orden. Son las mismas en cualquier contexto, para que las lecturas de RA
        # sean siempre las mismas.
        self.ra_nulas = sorted(
            (r for r in self.cliente.revisiones if r.tipo != PERIODICA and self._reinicia(r) is None),
            key=lambda r: r.fecha,
        )

    # --- Referencias a los datos (D-30) ---

    def _dato_revision(self, r):
        return f"cliente.revisiones[{self.cliente.revisiones.index(r)}] ({r.id})"

    def _dato_evento(self, ev):
        return f"cliente.eventos[{self.cliente.eventos.index(ev)}] ({ev.id})"

    def _dato_clasificacion(self, c):
        return f"cliente.clasificaciones[{self.cliente.clasificaciones.index(c)}] ({c.fecha})"

    def _dato_version(self, v):
        return f"manual.versiones[{self.versiones.index(v)}] ({v.id})"

    def _aviso(self, texto):
        if texto not in self.avisos:
            self.avisos.append(texto)

    # --- Régimen ---

    def evaluar(self, regimen) -> _Resultado:
        terminacion = self.cliente.fecha_terminacion_relacion
        if terminacion is not None and terminacion <= self.ref:
            # D-22. El estado en la fecha de terminación, solo para el aviso.
            previo = _Evaluador(self.entrada, self.e, terminacion)._evaluar_viva(regimen)
            avisos = [f"La relación terminó el {terminacion}: no hay próxima revisión (D-22)."]
            if previo.estado == VENCIDA:
                avisos.append(
                    f"En la fecha de terminación había una revisión vencida: su fecha límite era el "
                    f"{previo.fecha_proxima_revision} (D-2, D-22)."
                )
            return _Resultado(RELACION_TERMINADA, None, (), (), tuple(avisos))
        return self._evaluar_viva(regimen)

    def _evaluar_viva(self, regimen) -> _Resultado:
        if regimen == LEY_RD:
            periodico = self._periodo(_RD, self._ancla(_RD, self.revisiones))
            eventos = self._eventos(_RD)
        elif regimen == AMLR:
            if self.ref < self.A:
                self._aviso(f"El AMLR no es aplicable hasta el {self.A}: resultado solo comparativo (D-24).")
            periodico = self._periodo(_AMLR, self._ancla(_AMLR, self.revisiones))
            eventos = self._eventos(_AMLR)
        elif self.ref < self.A:
            # §5.2: antes de A, los cuatro son `ley_rd`.
            return self._evaluar_viva(LEY_RD)
        else:
            periodico, eventos = self._transicion(regimen)
        return self._componer(periodico, eventos)

    def _transicion(self, regimen):
        """§5.2."""
        if regimen == "T-4":
            rd = self._periodo(_RD, self._ancla(_RD, self.revisiones))
            amlr = self._periodo(_AMLR, self._ancla(_AMLR, self.revisiones))
            return self._mas_temprano(rd, amlr), self._eventos("ambas")

        existente = self.cliente.fecha_inicio_relacion < self.A
        if regimen == "T-2" or not existente:
            return self._periodo(_AMLR, self._ancla(_AMLR, self.revisiones)), self._eventos("transicion")

        # T-1 y T-3 con un cliente existente. D-33: qué norma decide si una revisión
        # posterior a A cuenta para cerrar el periodo del RD (TR-n).
        tr1, avisos_tr1 = self._capturando(lambda: self._periodo_t1_t3(regimen, _AMLR))
        tr2, avisos_tr2 = self._capturando(lambda: self._periodo_t1_t3(regimen, _RD))
        if tr1 != tr2:
            self._aviso(
                "Una revisión posterior a A cuenta con una norma y no con la otra, y cambia el "
                "periodo en curso: lecturas TR-1 (AMLR) y TR-2 (RD) (D-33)."
            )
        datos = [self._dato_revision(r) for r in self.revisiones if r.fecha >= self.A]
        clave = self.e.elegir_clave("TR", {"TR-1": tr1, "TR-2": tr2}, datos)
        periodico, avisos = (tr1, avisos_tr1) if clave == "TR-1" else (tr2, avisos_tr2)
        for a in avisos:
            self._aviso(a)
        return periodico, self._eventos("transicion")

    def _periodo_t1_t3(self, regimen, norma_posteriores):
        """Periodo de T-1 o T-3 de un cliente existente. Las revisiones con fecha ≥ A
        cuentan según `norma_posteriores` para cerrar el periodo del RD (D-33)."""
        posteriores = [r for r in self.revisiones if r.fecha >= self.A and self._cuenta(r, norma_posteriores)]
        if posteriores:
            # D-27: desde la primera revisión que cuenta con fecha ≥ A, AMLR con ella de ancla.
            primera = min(r.fecha for r in posteriores)
            desde = [r for r in self.revisiones if r.fecha >= primera]
            return self._periodo(_AMLR, self._ancla(_AMLR, desde, base=primera))
        # El periodo en curso el día A, con el RD.
        anteriores = [r for r in self.revisiones if r.fecha < self.A]
        periodico = self._periodo(_RD, self._ancla(_RD, anteriores))
        if regimen == "T-3":
            # D-26: A + P, sin superar el vencimiento del RD.
            periodico = self._mas_temprano(periodico, self._periodo(_AMLR, self.A))
        return periodico

    def _capturando(self, funcion):
        """(resultado, avisos nuevos), sin dejar los avisos anotados: solo se anotan
        los de la opción que rige."""
        previos = len(self.avisos)
        resultado = funcion()
        nuevos = self.avisos[previos:]
        del self.avisos[previos:]
        return resultado, nuevos

    @staticmethod
    def _mas_temprano(*componentes) -> tuple[Periodico, ...]:
        """Los componentes con la fecha límite más temprana. Si empatan, todos (D-34).
        Sin fecha límite (D-16) solo rige si ninguno la tiene."""
        planos = [p for c in componentes for p in (c if isinstance(c, tuple) else (c,))]
        con_fecha = [p for p in planos if p.fecha_limite is not None]
        if not con_fecha:
            return tuple(planos)
        primera = min(p.fecha_limite for p in con_fecha)
        return tuple(p for p in con_fecha if p.fecha_limite == primera)

    def _componer(self, periodicos, eventos) -> _Resultado:
        if isinstance(periodicos, Periodico):
            periodicos = (periodicos,)
        # Si empatan, todos tienen la misma fecha límite y el mismo estado.
        estados = [periodicos[0].estado] + [ev.estado for ev in eventos]
        estado = next(e for e in _PRIORIDAD if e in estados)  # D-23
        limites = [periodicos[0].fecha_limite] + [ev.fecha_limite for ev in eventos]
        limites = [f for f in limites if f is not None]
        # D-29: la más temprana sin cumplir.
        fecha = min(limites) if limites else None
        return _Resultado(estado, fecha, tuple(periodicos), tuple(eventos), tuple(self.avisos))

    def _estado(self, fecha_limite):
        if fecha_limite is None:
            return SIN_PLAZO
        return EN_PLAZO if fecha_limite >= self.ref else VENCIDA  # D-2

    # --- Clasificación y manual vigentes ---

    def _vigente(self, elementos, fecha_de, fecha):
        """El elemento con la fecha más reciente ≤ `fecha`; si no hay, el primero (D-13)."""
        if not elementos:
            return None
        anteriores = [x for x in elementos if fecha_de(x) <= fecha]
        if anteriores:
            return max(anteriores, key=fecha_de)
        return min(elementos, key=fecha_de)

    def _clasificacion_en(self, fecha):
        return self._vigente(self.cliente.clasificaciones, lambda c: c.fecha, fecha)

    def _version_en(self, fecha):
        return self._vigente(self.versiones, lambda v: v.vigente_desde, fecha)

    def _reinicia(self, revision):
        version = self._version_en(revision.fecha)
        return version.revision_anticipada_reinicia_plazo if version else None

    # --- Qué revisiones cuentan (§2.3) ---

    def _cuenta(self, revision, norma):
        if revision.resultado == NO_COMPLETADA:
            return False  # D-8
        if revision.resultado == ACTUALIZADA or norma == _RD:
            return True
        return self.e.elegir("AC", {"AC-1": True, "AC-2": False}, [self._dato_revision(revision)])

    # --- Ancla (§2.1 y §2.2) ---

    def _inicio_primer_periodo(self, norma):
        """IP-n (§2.1). IP-2 no existe si no hay revisión inicial que cuente (D-11)."""
        iniciales = sorted(r.fecha for r in self.revisiones if r.tipo == INICIAL and self._cuenta(r, norma))
        hay_inicial = any(r.tipo == INICIAL for r in self.cliente.revisiones)
        opciones = {"IP-1": self.cliente.fecha_inicio_relacion}
        if iniciales:
            opciones["IP-2"] = iniciales[0]
        elif hay_inicial:
            opciones["IP-2"] = _NO_DISPONIBLE
        opciones["IP-3"] = min(c.fecha for c in self.cliente.clasificaciones)
        if not iniciales:
            self._aviso("No hay revisión inicial que cuente: la lectura IP-2 no existe (D-11).")
        datos = ["cliente.fecha_inicio_relacion"]
        datos += [self._dato_revision(r) for r in self.cliente.revisiones if r.tipo == INICIAL]
        datos.append(self._dato_clasificacion(min(self.cliente.clasificaciones, key=lambda c: c.fecha)))
        return self.e.elegir("IP", opciones, datos)

    def _ancla(self, norma, revisiones, base=None):
        """La revisión más reciente que marca el calendario según RA-n (§2.2)."""
        contadas = [r for r in revisiones if self._cuenta(r, norma)]

        def respaldo():
            return base if base is not None else self._inicio_primer_periodo(norma)

        if not contadas:
            return respaldo()
        periodicas = [r for r in contadas if r.tipo == PERIODICA]
        otras = [r for r in contadas if r.tipo != PERIODICA]
        ra2 = max(r.fecha for r in periodicas) if periodicas else respaldo()
        if not otras:
            return ra2
        ra1 = max(r.fecha for r in contadas)

        # RA-3: las que el manual dice que reinician, más las periódicas.
        definidas = periodicas + [r for r in otras if self._reinicia(r) is True]
        base3 = max(r.fecha for r in definidas) if definidas else respaldo()
        opciones = {"RA-1": ra1, "RA-2": ra2}
        if self.ra_nulas:
            # D-10: cada revisión con el manual a null, de las dos maneras. Todas las
            # combinaciones dan como ancla la más reciente de las que reinician, así que
            # basta con elegir hasta cuál reinician.
            nulas = [r for r in otras if self._reinicia(r) is None]
            opciones["RA-3 (las revisiones con el manual a null no reinician)"] = base3
            for umbral in self.ra_nulas:
                hasta = [r.fecha for r in nulas if r.fecha <= umbral.fecha]
                opciones[f"RA-3 (reinician hasta {umbral.id})"] = max([base3, *hasta])
        else:
            opciones["RA-3"] = base3
        return self.e.elegir("RA", opciones, [self._dato_revision(r) for r in otras])

    # --- Periodicidad (§3.2 y §4.2) ---

    def _periodicidad(self, norma, c, version):
        """(meses o None, avisos) para la clasificación y la versión dadas."""
        pm = version.periodicidad(c.nivel_entidad) if version else None
        if norma == _RD:
            return self._periodicidad_rd(c, pm)
        return self._periodicidad_amlr(c, pm)

    def _periodicidad_rd(self, c, pm):
        def con(superior):
            if not superior:
                return pm, ()  # D-16 si pm es None
            if pm is None:
                return 12, ()
            if pm > 12:
                return 12, (f"El manual fija {pm} meses para «{c.nivel_entidad}», más que el mínimo anual del RD 11.2 con riesgo superior al promedio: se aplican 12 (D-14).",)
            return pm, ()

        if c.superior_al_promedio is None:
            # D-15.
            return self.e.elegir(
                f"SP ({c.fecha})", {"SP-1": con(True), "SP-2": con(False)}, [self._dato_clasificacion(c)]
            )
        return con(c.superior_al_promedio)

    def _periodicidad_amlr(self, c, pm):
        dato = [self._dato_clasificacion(c)]

        def limite(elevado, seccion_4):
            if elevado == seccion_4:
                return 12 if elevado else 60
            return self.e.elegir("PB", {"PB-1": 60, "PB-2": 12}, dato)

        elevado, seccion_4 = c.riesgo_elevado_amlr, c.medidas_seccion_4_amlr
        if elevado is None and seccion_4 is None:
            if c.superior_al_promedio is None:
                nc2 = self.e.elegir(f"SP ({c.fecha})", {"SP-1": 12, "SP-2": 60}, dato)
            else:
                nc2 = 12 if c.superior_al_promedio else 60
            limite_legal = self.e.elegir("NC", {"NC-1": 60, "NC-2": nc2}, dato)
        elif elevado is None:
            limite_legal = self.e.elegir(
                f"riesgo_elevado_amlr desconocido ({c.fecha})",
                {"true": limite(True, seccion_4), "false": limite(False, seccion_4)},
                dato,
            )
        elif seccion_4 is None:
            limite_legal = self.e.elegir(
                f"medidas_seccion_4_amlr desconocido ({c.fecha})",
                {"true": limite(elevado, True), "false": limite(elevado, False)},
                dato,
            )
        else:
            limite_legal = limite(elevado, seccion_4)

        if pm is not None and pm > limite_legal:
            return limite_legal, (f"El manual fija {pm} meses para «{c.nivel_entidad}», más que el límite del AMLR 26.2 ({limite_legal}): se aplica el límite (D-17).",)
        if pm is not None and pm < limite_legal:
            return self.e.elegir("PM", {"PM-1": limite_legal, "PM-2": pm}, dato), ()
        return limite_legal, ()

    def _periodo(self, norma, ancla) -> Periodico:
        """Fecha límite periódica, con FR-n si la clasificación o el manual cambian (§2.4)."""
        ca, va = self._clasificacion_en(ancla), self._version_en(ancla)
        cr, vr = self._clasificacion_en(self.ref), self._version_en(self.ref)
        pa, avisos_a = self._periodicidad(norma, ca, va)
        if (ca, va) == (cr, vr):
            return self._periodico(norma, ancla, pa, avisos_a)

        pr, avisos_r = self._periodicidad(norma, cr, vr)
        # FR-3: la fecha más reciente, posterior al ancla, en que cambió P.
        cambios = sorted(
            {c.fecha for c in self.cliente.clasificaciones if ancla < c.fecha <= self.ref}
            | {v.vigente_desde for v in self.versiones if ancla < v.vigente_desde <= self.ref}
        )
        desde, previa = ancla, pa
        for fecha in cambios:
            p, _ = self._periodicidad(norma, self._clasificacion_en(fecha), self._version_en(fecha))
            if p != previa:
                desde, previa = fecha, p

        opciones = {"FR-1": (ancla, pa, avisos_a), "FR-2": (ancla, pr, avisos_r), "FR-3": (desde, pr, avisos_r)}
        datos = [self._dato_clasificacion(c) for c in self.cliente.clasificaciones if ancla < c.fecha <= self.ref]
        datos += [self._dato_version(v) for v in self.versiones if ancla < v.vigente_desde <= self.ref]
        clave = self.e.elegir_clave(
            "FR", {k: (self._limite(i, p), p) for k, (i, p, _) in opciones.items()}, datos
        )
        inicio, meses, avisos = opciones[clave]
        return self._periodico(norma, inicio, meses, avisos)

    @staticmethod
    def _limite(inicio, meses):
        return sumar_meses(inicio, meses) if meses is not None else None

    def _periodico(self, norma, ancla, meses, avisos):
        for a in avisos:
            self._aviso(a)
        limite = self._limite(ancla, meses)
        return Periodico(norma, ancla, meses, limite, self._estado(limite))

    # --- Eventos (§6) ---

    def _atendido(self, evento):
        # D-19: lo incluye una revisión que no es `no_completada`, sea cual sea su fecha.
        return any(evento.id in r.eventos and r.resultado != NO_COMPLETADA for r in self.revisiones)

    def _activacion_rd(self, ev):
        """(fecha, base) con la Ley y el RD (§6.2), o None."""
        dato = [self._dato_evento(ev)]
        candidatas = []
        if ev.tipo == "cambio_actividad":
            fecha = self.e.elegir("FV", {"FV-1": ev.fecha_hecho, "FV-2": ev.fecha_conocimiento}, dato)
            candidatas.append((fecha, "RD 33.1.b"))
        if ev.tipo in _LEY_7_2 or ev.tipo in _LEY_7_2_SEGUN_LC:
            if self.cliente.fecha_inicio_relacion < ENTRADA_EN_VIGOR_LEY:
                aplica = True
            else:
                aplica = self.e.elegir("L72", {"L72-1": False, "L72-2": True}, dato)
            if aplica and ev.tipo in _LEY_7_2_SEGUN_LC:
                aplica = self.e.elegir(f"LC ({ev.tipo})", {"LC-1": False, "LC-2": True}, dato)
            if aplica:
                candidatas.append((ev.fecha_hecho, "Ley 7.2"))
        return _mas_temprana(candidatas)  # D-21, D-34

    def _activacion_amlr(self, ev):
        """(fecha, base) con el AMLR (§6.3), o None."""

        def por_letra(letra):
            if letra is None:
                return None
            fecha = ev.fecha_conocimiento if letra == "c" else ev.fecha_hecho
            return fecha, (f"AMLR 26.3.{letra}",)

        letra = _LETRA_AMLR[ev.tipo]
        if isinstance(letra, str):
            return por_letra(letra)
        opciones = {lectura: por_letra(_LETRA_DE_LECTURA[lectura]) for lectura in letra}
        return self.e.elegir(f"EV ({ev.tipo})", opciones, [self._dato_evento(ev)])

    def _activacion(self, ev, modo):
        if modo == _RD:
            return self._activacion_rd(ev)
        if modo == _AMLR:
            return self._activacion_amlr(ev)
        if modo == "ambas":
            # D-25, T-4: con las dos normas; rige la activación más temprana (D-21).
            activaciones = [a for a in (self._activacion_rd(ev), self._activacion_amlr(ev)) if a]
            return _mas_temprana([(f, b) for f, bases in activaciones for b in bases])
        # D-25, T-1 a T-3: la norma aplicable en la fecha de activación: el RD si lo
        # activa antes de A, el AMLR si lo activa en A o después. El RD no puede
        # activarlo antes de A si el hecho y su conocimiento son posteriores.
        rd = None
        if min(ev.fecha_hecho, ev.fecha_conocimiento) < self.A:
            rd = self._activacion_rd(ev)
        amlr = self._activacion_amlr(ev)
        rd_en_su_periodo = rd is not None and rd[0] < self.A
        amlr_en_su_periodo = amlr is not None and amlr[0] >= self.A
        if rd_en_su_periodo and amlr_en_su_periodo:
            # D-32: las dos lo activan en su periodo. Ninguna tiene preferencia.
            self._aviso(
                f"El evento {ev.id} se activa con el RD el {rd[0]} (antes de A) y con el AMLR el "
                f"{amlr[0]} (en A o después): lecturas TD-1 y TD-2 (D-32)."
            )
            return self.e.elegir("TD", {"TD-1": rd, "TD-2": amlr}, [self._dato_evento(ev)])
        if rd_en_su_periodo:
            return rd
        if amlr_en_su_periodo:
            return amlr
        if rd is None:
            # Antes de A y sin supuesto en el RD: no obliga (D-25).
            return None
        # D-31: el RD lo activa en A o después y el AMLR antes de A (o no lo activa).
        # Ninguna norma lo activa en su periodo: lecturas TE-n, sin descartarlo en silencio.
        self._aviso(
            f"El evento {ev.id} se activa con el RD el {rd[0]} (en A o después) y con el AMLR "
            f"{'el ' + str(amlr[0]) + ' (antes de A)' if amlr else 'en ninguna fecha'}: lecturas TE-1 a TE-3 (D-31)."
        )
        opciones = {
            "TE-1": rd,
            "TE-2": (self.A, tuple(f"{b}, desde A" for b in amlr[1])) if amlr else None,
            "TE-3": None,
        }
        return self.e.elegir("TE", opciones, [self._dato_evento(ev)])

    def _eventos(self, modo):
        pendientes = []
        for ev in self.cliente.eventos:
            if ev.fecha_hecho > self.ref or not ev.relevante_segun_entidad:  # D-18
                continue
            if self._atendido(ev):
                continue
            activacion = self._activacion(ev, modo)
            if activacion is None or activacion[0] > self.ref:
                continue
            fecha, bases = activacion
            pendientes.append(self._pendiente(ev, fecha, bases))
        return pendientes

    def _pendiente(self, ev, activacion, bases):
        """D-20."""
        version = self._version_en(activacion)
        plazo = version.plazo_revision_por_evento_dias if version else None
        limite = sumar_dias(activacion, plazo) if plazo else None
        if ev.tipo in TIPOS_CONTACTO:
            fin_de_anio = date(ev.anio_natural, 12, 31)
            limite = min(limite, fin_de_anio) if limite else fin_de_anio
        if limite is None:
            estado = PENDIENTE_SIN_PLAZO
        else:
            estado = self._estado(limite)
        if "AMLR 26.3.a" in bases and limite is not None and limite < ev.fecha_conocimiento:
            self._aviso(
                f"El evento {ev.id} se activa por la letra a) el {activacion} y la entidad lo conoció el "
                f"{ev.fecha_conocimiento}, después de su fecha límite ({limite}) (§6.3)."
            )
        return EventoPendiente(ev.id, bases, activacion, limite, estado)
