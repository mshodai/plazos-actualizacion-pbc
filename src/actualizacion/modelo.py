"""Estructuras de datos de la entrada, según docs/modelo-datos.md (versión 1).

Describen la entrada ya validada y no contienen ninguna regla de cálculo. No
hay régimen: es un parámetro del cálculo (modelo, §0). Todas las fechas son
`date`; el texto AAAA-MM-DD solo existe en el JSON.

Las listas conservan el orden de la entrada, y cada elemento se identifica de
forma única: por `id` (versiones del manual, revisiones, eventos) o por
`fecha` (clasificaciones; modelo, V-4). El cálculo tendrá que atribuir cada
estado `indeterminado` a las lecturas que lo causan y a los datos que las
activan (especificación, §1.5), y lo hará citando esos identificadores.
"""

from dataclasses import dataclass
from datetime import date

VERSION_MODELO = 1

# §2.1
ACTIVIDADES = ("agente_de_futbol", "club_de_futbol_profesional", "otra")

# §5
INICIAL = "inicial"
PERIODICA = "periodica"
POR_EVENTO = "por_evento"
TIPOS_REVISION = (INICIAL, PERIODICA, POR_EVENTO)

ACTUALIZADA = "actualizada"
SIN_CAMBIOS = "sin_cambios"
NO_COMPLETADA = "no_completada"
RESULTADOS_REVISION = (ACTUALIZADA, SIN_CAMBIOS, NO_COMPLETADA)

# §6.2
OBLIGACION_CONTACTO_TITULARIDAD_REAL = "obligacion_contacto_titularidad_real"
OBLIGACION_CONTACTO_DAC = "obligacion_contacto_dac"
TIPOS_CONTACTO = (OBLIGACION_CONTACTO_TITULARIDAD_REAL, OBLIGACION_CONTACTO_DAC)
OTRO = "otro"
TIPOS_EVENTO = (
    "cambio_actividad",
    "cambio_identidad",
    "cambio_titularidad_real_o_control",
    "cambio_situacion_financiera",
    "nuevo_producto",
    "operacion_significativa",
    "anomalia_operativa",
    "informacion_de_riesgo",
    *TIPOS_CONTACTO,
    OTRO,
)

# Modelo, §9.1 (V-14).
ERRORES = {
    "ERR-01": "JSON mal formado o con claves repetidas, campo obligatorio ausente, valor de tipo no válido, "
    "`version_modelo` distinto de 1, o campo `regimen` u otro desconocido",
    "ERR-02": "`id` repetido, o `vigente_desde` o `fecha` de clasificación repetida",
    "ERR-03": "`nivel_entidad` repetido en las periodicidades de una versión del manual",
    "ERR-04": "`cliente.clasificaciones` vacía",
    "ERR-05": "Una revisión cita un evento que no existe",
    "ERR-06": "`fecha_conocimiento` anterior a `fecha_hecho`",
    "ERR-07": "`fecha_terminacion_relacion` anterior a `fecha_inicio_relacion`",
    "ERR-08": "Un hecho posterior a `fecha_referencia`",
}


@dataclass(frozen=True)
class Sujeto:
    actividad: str


@dataclass(frozen=True)
class Periodicidad:
    """§3.3. `meses` > 0."""

    nivel_entidad: str
    meses: int


@dataclass(frozen=True)
class VersionManual:
    """§3.3."""

    id: str
    vigente_desde: date
    periodicidades: tuple[Periodicidad, ...]
    plazo_revision_por_evento_dias: int | None
    revision_anticipada_reinicia_plazo: bool | None

    def periodicidad(self, nivel_entidad: str) -> int | None:
        """Meses fijados para ese nivel, o None. Comparación exacta (modelo, V-21)."""
        for p in self.periodicidades:
            if p.nivel_entidad == nivel_entidad:
                return p.meses
        return None


@dataclass(frozen=True)
class Manual:
    versiones: tuple[VersionManual, ...]


@dataclass(frozen=True)
class Clasificacion:
    """§4.2. Una calificación a None es que la entidad no la hizo."""

    fecha: date
    nivel_entidad: str
    superior_al_promedio: bool | None
    riesgo_elevado_amlr: bool | None
    medidas_seccion_4_amlr: bool | None


@dataclass(frozen=True)
class Revision:
    """§5."""

    id: str
    tipo: str
    fecha: date
    resultado: str
    eventos: tuple[str, ...]


@dataclass(frozen=True)
class Evento:
    """§6.1. `anio_natural` solo en los tipos de obligación de contacto."""

    id: str
    tipo: str
    fecha_hecho: date
    fecha_conocimiento: date
    relevante_segun_entidad: bool
    descripcion: str | None = None
    anio_natural: int | None = None


@dataclass(frozen=True)
class Cliente:
    """§7."""

    id: str
    fecha_inicio_relacion: date
    fecha_terminacion_relacion: date | None
    clasificaciones: tuple[Clasificacion, ...]
    revisiones: tuple[Revision, ...]
    eventos: tuple[Evento, ...]


@dataclass(frozen=True)
class Entrada:
    version_modelo: int
    fecha_referencia: date
    sujeto: Sujeto
    manual: Manual
    cliente: Cliente


@dataclass(frozen=True)
class Incidencia:
    """Error de validación del §9. `ruta` señala el dato en el JSON, p. ej.
    `cliente.eventos[2].fecha_conocimiento`."""

    codigo: str
    mensaje: str
    ruta: str = ""


@dataclass(frozen=True)
class ResultadoCarga:
    """La entrada validada, o None si hay algún error.

    El modelo no define avisos, así que solo hay errores.
    """

    entrada: Entrada | None
    errores: tuple[Incidencia, ...]

    @property
    def valida(self) -> bool:
        return not self.errores
