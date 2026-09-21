"""Lectura y validación de la entrada, según docs/modelo-datos.md (versión 1).

`cargar` lee el JSON y devuelve un ResultadoCarga con la entrada validada (o
None si hay errores) y los errores del §9 del modelo. No calcula nada, y la
validación no depende del régimen (modelo, §0, principio 3).

Se recogen todos los errores de una pasada, no solo el primero (modelo, §9).
Un dato mal formado se anota como ERR-01 y las comprobaciones que dependen de
él se omiten (modelo, V-23).

Las decisiones de validación del modelo se citan como «Modelo, V-n». Los
demás comentarios son de implementación.
"""

import json
import re
from datetime import date
from pathlib import Path

from actualizacion.modelo import (
    ACTIVIDADES,
    OTRO,
    RESULTADOS_REVISION,
    TIPOS_CONTACTO,
    TIPOS_EVENTO,
    TIPOS_REVISION,
    VERSION_MODELO,
    Clasificacion,
    Cliente,
    Entrada,
    Evento,
    Incidencia,
    Manual,
    Periodicidad,
    ResultadoCarga,
    Revision,
    Sujeto,
    VersionManual,
)

_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


class _Invalido:
    """Marca un campo presente pero mal formado (ya anotado como ERR-01).

    Se distingue de None, que es un null válido o un campo opcional ausente.
    """

    def __repr__(self):
        return "INVALIDO"


INVALIDO = _Invalido()


def cargar(texto: str) -> ResultadoCarga:
    """Lee y valida una entrada en JSON."""
    return _Carga().ejecutar(texto)


def cargar_fichero(ruta) -> ResultadoCarga:
    return cargar(Path(ruta).read_text(encoding="utf-8"))


# --- Lectura del JSON --------------------------------------------------------


def _leer_json(texto):
    """Devuelve (datos, claves repetidas). Rechaza NaN e Infinity."""
    repetidas = []

    def objeto(pares):
        resultado = {}
        for clave, valor in pares:
            if clave in resultado:
                repetidas.append(clave)
            resultado[clave] = valor
        return resultado

    def constante(nombre):
        raise ValueError(f"{nombre} no es un número JSON válido")

    datos = json.loads(texto, parse_constant=constante, object_pairs_hook=objeto)
    return datos, repetidas


def _ruta(base, clave):
    return f"{base}.{clave}" if base else clave


def _es_entero(v):
    # Modelo, V-17: ni booleanos (en Python, True es un int) ni reales como 12.0.
    return isinstance(v, int) and not isinstance(v, bool)


def _es_fecha(v):
    return isinstance(v, date)


# --- Validación --------------------------------------------------------------


class _Carga:
    def __init__(self):
        self.errores: list[Incidencia] = []
        # Fechas de hechos para ERR-08: (ruta, fecha).
        self.hechos: list[tuple[str, date]] = []

    def error(self, codigo, mensaje, ruta=""):
        self.errores.append(Incidencia(codigo, mensaje, ruta))

    def ejecutar(self, texto):
        try:
            datos, repetidas = _leer_json(texto)
        except ValueError as e:
            # Modelo, V-15: un JSON mal formado es ERR-01.
            self.error("ERR-01", f"El JSON no es válido: {e}")
            return self._resultado(None)

        for clave in repetidas:
            # Modelo, V-15: una clave repetida es ERR-01. El módulo json se quedaría en
            # silencio con el último valor.
            self.error("ERR-01", f"La clave «{clave}» aparece repetida en un mismo objeto")

        if isinstance(datos, dict) and "regimen" in datos:
            # §2: «Un JSON con `regimen` [...] es un error de validación».
            self.error(
                "ERR-01",
                "La entrada no lleva régimen: es un parámetro del cálculo (modelo, §0 y §2)",
                "regimen",
            )
        if not self._objeto(
            datos,
            "",
            ("version_modelo", "fecha_referencia", "sujeto", "manual", "cliente"),
            ignorar=("regimen",),
        ):
            return self._resultado(None)

        version = self._version(datos)
        fecha_referencia = self._fecha(datos, "fecha_referencia", "", hecho=False)
        sujeto = self._sujeto(datos)
        manual = self._manual(datos)
        cliente = self._cliente(datos)

        if _es_fecha(fecha_referencia):
            self._comprobar_hechos_posteriores(fecha_referencia)

        if self.errores:
            return self._resultado(None)
        return self._resultado(Entrada(version, fecha_referencia, sujeto, manual, cliente))

    def _resultado(self, entrada):
        return ResultadoCarga(
            entrada=entrada,
            errores=tuple(sorted(self.errores, key=lambda i: i.codigo)),
        )

    # --- Campos (ERR-01) -----------------------------------------------------

    def _objeto(self, obj, ruta, obligatorios, opcionales=(), ignorar=()):
        """Comprueba que `obj` es un objeto con esos campos. Devuelve si lo es."""
        if not isinstance(obj, dict):
            self.error("ERR-01", "Debe ser un objeto", ruta)
            return False
        for clave in obligatorios:
            if clave not in obj:
                # Modelo, V-2: también los campos que admiten null.
                self.error("ERR-01", f"Falta el campo obligatorio «{clave}»", _ruta(ruta, clave))
        for clave in obj:
            if clave not in obligatorios and clave not in opcionales and clave not in ignorar:
                # Modelo, V-1: cualquier campo desconocido es ERR-01, no solo `regimen`.
                self.error("ERR-01", f"Campo desconocido «{clave}»", _ruta(ruta, clave))
        return True

    def _campo(self, obj, clave, ruta, es_valido, descripcion, nulo):
        """obj[clave]: None si falta o es un null admitido; INVALIDO si está mal.

        La falta de un campo obligatorio ya la anota `_objeto`.
        """
        if clave not in obj:
            return None
        valor = obj[clave]
        if valor is None and nulo:
            return None
        if valor is None or not es_valido(valor):
            self.error("ERR-01", f"«{clave}» debe ser {descripcion}", _ruta(ruta, clave))
            return INVALIDO
        return valor

    def _texto(self, obj, clave, ruta, nulo=False):
        # Modelo, V-18: se admiten textos vacíos.
        return self._campo(obj, clave, ruta, lambda v: isinstance(v, str), "un texto", nulo)

    def _booleano(self, obj, clave, ruta, nulo=False):
        descripcion = "true, false o null" if nulo else "true o false"
        return self._campo(obj, clave, ruta, lambda v: isinstance(v, bool), descripcion, nulo)

    def _entero(self, obj, clave, ruta, minimo, maximo=None, nulo=False):
        # Modelo, V-17.
        if maximo is None:
            descripcion = f"un entero mayor o igual que {minimo}"
        else:
            descripcion = f"un entero entre {minimo} y {maximo}"
        if nulo:
            descripcion += " o null"
        return self._campo(
            obj,
            clave,
            ruta,
            lambda v: _es_entero(v) and v >= minimo and (maximo is None or v <= maximo),
            descripcion,
            nulo,
        )

    def _enumerado(self, obj, clave, ruta, valores):
        descripcion = " o ".join(f"«{v}»" for v in valores)
        return self._campo(obj, clave, ruta, lambda v: isinstance(v, str) and v in valores, descripcion, False)

    def _fecha(self, obj, clave, ruta, nulo=False, hecho=True):
        """Fecha como `date`. Si `hecho`, se guarda para ERR-08."""
        texto = self._campo(obj, clave, ruta, lambda v: isinstance(v, str), "una fecha AAAA-MM-DD", nulo)
        if texto is None or texto is INVALIDO:
            return texto
        try:
            # Modelo, V-16: fromisoformat admite también otras formas (20240101,
            # semanas); el modelo pide AAAA-MM-DD (§2).
            if not _FECHA.fullmatch(texto):
                raise ValueError
            fecha = date.fromisoformat(texto)
        except ValueError:
            self.error("ERR-01", f"«{clave}» debe ser una fecha AAAA-MM-DD", _ruta(ruta, clave))
            return INVALIDO
        if hecho:
            self.hechos.append((_ruta(ruta, clave), fecha))
        return fecha

    def _lista(self, obj, clave, ruta):
        """obj[clave] si es una lista; None si falta o no lo es (ya anotado)."""
        if clave not in obj:
            return None
        valor = obj[clave]
        if not isinstance(valor, list):
            self.error("ERR-01", f"«{clave}» debe ser una lista", _ruta(ruta, clave))
            return None
        return valor

    def _version(self, datos):
        version = self._campo(datos, "version_modelo", "", _es_entero, "un entero", False)
        if _es_entero(version) and version != VERSION_MODELO:
            # Modelo, V-3: otra versión es ERR-01.
            self.error("ERR-01", f"«version_modelo» debe ser {VERSION_MODELO}", "version_modelo")
            return INVALIDO
        return version

    def _unicos(self, valores, ruta_lista, campo, codigo, que):
        """Anota `codigo` por cada valor repetido de `campo`. `valores` es una
        lista de (índice, valor); los INVALIDO y None se ignoran (modelo, V-23)."""
        vistos = set()
        for i, valor in valores:
            if valor is None or valor is INVALIDO:
                continue
            if valor in vistos:
                self.error(codigo, f"{que} «{valor}» repetido", f"{ruta_lista}[{i}].{campo}")
            vistos.add(valor)

    # --- Sujeto (§2.1) -------------------------------------------------------

    def _sujeto(self, datos):
        obj = datos.get("sujeto")
        if not self._objeto(obj, "sujeto", ("actividad",)):
            return None
        return Sujeto(self._enumerado(obj, "actividad", "sujeto", ACTIVIDADES))

    # --- Manual (§3) ---------------------------------------------------------

    def _manual(self, datos):
        obj = datos.get("manual")
        if not self._objeto(obj, "manual", ("versiones",)):
            return None
        # Modelo, V-19: la lista de versiones puede estar vacía.
        lista = self._lista(obj, "versiones", "manual") or []
        versiones = [self._version_manual(v, f"manual.versiones[{i}]") for i, v in enumerate(lista)]
        self._unicos(
            [(i, v.id) for i, v in enumerate(versiones) if v], "manual.versiones", "id", "ERR-02", "id de versión"
        )
        self._unicos(
            [(i, v.vigente_desde) for i, v in enumerate(versiones) if v],
            "manual.versiones",
            "vigente_desde",
            "ERR-02",
            "vigente_desde",
        )
        return Manual(tuple(v for v in versiones if v))

    def _version_manual(self, obj, ruta):
        if not self._objeto(
            obj,
            ruta,
            (
                "id",
                "vigente_desde",
                "periodicidades",
                "plazo_revision_por_evento_dias",
                "revision_anticipada_reinicia_plazo",
            ),
        ):
            return None
        id_ = self._texto(obj, "id", ruta)
        # Modelo, §7: `vigente_desde` es un hecho a efectos de ERR-08.
        vigente_desde = self._fecha(obj, "vigente_desde", ruta)
        # Modelo, V-19: puede estar vacía.
        lista = self._lista(obj, "periodicidades", ruta) or []
        periodicidades = [self._periodicidad(p, f"{ruta}.periodicidades[{i}]") for i, p in enumerate(lista)]
        self._unicos(
            [(i, p.nivel_entidad) for i, p in enumerate(periodicidades) if p],
            f"{ruta}.periodicidades",
            "nivel_entidad",
            "ERR-03",
            "nivel_entidad",
        )
        plazo = self._entero(obj, "plazo_revision_por_evento_dias", ruta, 1, nulo=True)
        reinicia = self._booleano(obj, "revision_anticipada_reinicia_plazo", ruta, nulo=True)
        return VersionManual(id_, vigente_desde, tuple(p for p in periodicidades if p), plazo, reinicia)

    def _periodicidad(self, obj, ruta):
        if not self._objeto(obj, ruta, ("nivel_entidad", "meses")):
            return None
        return Periodicidad(self._texto(obj, "nivel_entidad", ruta), self._entero(obj, "meses", ruta, 1))

    # --- Cliente (§4 a §7) ---------------------------------------------------

    def _cliente(self, datos):
        obj = datos.get("cliente")
        ruta = "cliente"
        if not self._objeto(
            obj,
            ruta,
            ("id", "fecha_inicio_relacion", "fecha_terminacion_relacion", "clasificaciones", "revisiones", "eventos"),
        ):
            return None
        id_ = self._texto(obj, "id", ruta)
        inicio = self._fecha(obj, "fecha_inicio_relacion", ruta)
        terminacion = self._fecha(obj, "fecha_terminacion_relacion", ruta, nulo=True)
        if _es_fecha(inicio) and _es_fecha(terminacion) and terminacion < inicio:
            # Modelo, V-10.
            self.error(
                "ERR-07",
                f"«fecha_terminacion_relacion» ({terminacion}) es anterior a «fecha_inicio_relacion» ({inicio})",
                "cliente.fecha_terminacion_relacion",
            )

        clasificaciones = self._clasificaciones(obj)
        # En el orden del JSON, para que los errores también lo sigan. Las referencias
        # de las revisiones a los eventos se comprueban después.
        revisiones = self._revisiones(obj)
        eventos = self._eventos(obj)
        self._comprobar_referencias(revisiones, eventos)
        return Cliente(id_, inicio, terminacion, clasificaciones, revisiones, eventos)

    def _clasificaciones(self, cliente):
        lista = self._lista(cliente, "clasificaciones", "cliente")
        if lista is not None and not lista:
            # Modelo, V-7.
            self.error("ERR-04", "«clasificaciones» no puede estar vacía", "cliente.clasificaciones")
        clasificaciones = [
            self._clasificacion(c, f"cliente.clasificaciones[{i}]") for i, c in enumerate(lista or [])
        ]
        # Modelo, V-4: la fecha identifica la clasificación.
        self._unicos(
            [(i, c.fecha) for i, c in enumerate(clasificaciones) if c],
            "cliente.clasificaciones",
            "fecha",
            "ERR-02",
            "fecha de clasificación",
        )
        return tuple(c for c in clasificaciones if c)

    def _clasificacion(self, obj, ruta):
        if not self._objeto(
            obj,
            ruta,
            ("fecha", "nivel_entidad", "superior_al_promedio", "riesgo_elevado_amlr", "medidas_seccion_4_amlr"),
        ):
            return None
        return Clasificacion(
            self._fecha(obj, "fecha", ruta),
            self._texto(obj, "nivel_entidad", ruta),
            # Modelo, V-13: se admiten todas las combinaciones.
            self._booleano(obj, "superior_al_promedio", ruta, nulo=True),
            self._booleano(obj, "riesgo_elevado_amlr", ruta, nulo=True),
            self._booleano(obj, "medidas_seccion_4_amlr", ruta, nulo=True),
        )

    def _revisiones(self, cliente):
        lista = self._lista(cliente, "revisiones", "cliente") or []
        revisiones = [self._revision(r, f"cliente.revisiones[{i}]") for i, r in enumerate(lista)]
        self._unicos(
            [(i, r.id) for i, r in enumerate(revisiones) if r], "cliente.revisiones", "id", "ERR-02", "id de revisión"
        )
        return tuple(r for r in revisiones if r)

    def _comprobar_referencias(self, revisiones, eventos):
        if eventos is INVALIDO:
            # Modelo, V-23: sin la lista de eventos, o con algún id mal formado, no se
            # sabe qué eventos existen y ERR-05 no se comprueba.
            return
        ids_eventos = {e.id for e in eventos}
        for i, r in enumerate(revisiones):
            if r.eventos is INVALIDO:
                continue
            for j, id_ in enumerate(r.eventos):
                if id_ not in ids_eventos:
                    # Modelo, V-8.
                    self.error(
                        "ERR-05",
                        f"La revisión cita el evento «{id_}», que no existe",
                        f"cliente.revisiones[{i}].eventos[{j}]",
                    )

    def _revision(self, obj, ruta):
        if not self._objeto(obj, ruta, ("id", "tipo", "fecha", "resultado", "eventos")):
            return None
        id_ = self._texto(obj, "id", ruta)
        tipo = self._enumerado(obj, "tipo", ruta, TIPOS_REVISION)
        fecha = self._fecha(obj, "fecha", ruta)
        resultado = self._enumerado(obj, "resultado", ruta, RESULTADOS_REVISION)
        eventos = self._ids_eventos(obj, ruta)
        return Revision(id_, tipo, fecha, resultado, eventos)

    def _ids_eventos(self, obj, ruta):
        lista = self._lista(obj, "eventos", ruta)
        if lista is None:
            return INVALIDO if "eventos" in obj else ()
        ids = []
        vistos = set()
        valido = True
        for j, id_ in enumerate(lista):
            if not isinstance(id_, str):
                self.error("ERR-01", "Cada elemento de «eventos» debe ser un texto", f"{ruta}.eventos[{j}]")
                valido = False
                continue
            if id_ in vistos:
                # Modelo, V-20: un mismo evento no se cita dos veces en una revisión.
                self.error("ERR-02", f"El evento «{id_}» se cita dos veces", f"{ruta}.eventos[{j}]")
            vistos.add(id_)
            ids.append(id_)
        return tuple(ids) if valido else INVALIDO

    def _eventos(self, cliente):
        """La tupla de eventos, o INVALIDO si la lista o algún `id` está mal formado."""
        if "eventos" not in cliente:
            return INVALIDO
        lista = self._lista(cliente, "eventos", "cliente")
        if lista is None:
            return INVALIDO
        eventos = [self._evento(e, f"cliente.eventos[{i}]") for i, e in enumerate(lista)]
        self._unicos(
            [(i, e.id) for i, e in enumerate(eventos) if e], "cliente.eventos", "id", "ERR-02", "id de evento"
        )
        if any(e is None or e.id is INVALIDO or e.id is None for e in eventos):
            return INVALIDO
        return tuple(eventos)

    def _evento(self, obj, ruta):
        tipo_crudo = obj.get("tipo") if isinstance(obj, dict) else None
        contacto = tipo_crudo in TIPOS_CONTACTO
        otro = tipo_crudo == OTRO
        obligatorios = ["id", "tipo", "fecha_hecho", "fecha_conocimiento", "relevante_segun_entidad"]
        opcionales = []
        if contacto:
            obligatorios.append("anio_natural")
        # Modelo, V-1: `anio_natural` en otro tipo es un campo desconocido.
        if otro:
            obligatorios.append("descripcion")
        else:
            opcionales.append("descripcion")
        if not self._objeto(obj, ruta, tuple(obligatorios), tuple(opcionales)):
            return None

        id_ = self._texto(obj, "id", ruta)
        tipo = self._enumerado(obj, "tipo", ruta, TIPOS_EVENTO)
        # Modelo, V-18: con `otro`, `descripcion` no admite null; en los demás tipos,
        # null equivale a omitirla.
        descripcion = self._texto(obj, "descripcion", ruta, nulo=not otro)
        hecho = self._fecha(obj, "fecha_hecho", ruta)
        conocimiento = self._fecha(obj, "fecha_conocimiento", ruta)
        relevante = self._booleano(obj, "relevante_segun_entidad", ruta)
        # Modelo, V-17: un año que `date` pueda representar. Modelo, V-22: no se
        # compara con `fecha_hecho`.
        anio = self._entero(obj, "anio_natural", ruta, 1, 9999) if contacto else None

        if _es_fecha(hecho) and _es_fecha(conocimiento) and conocimiento < hecho:
            # Modelo, V-9.
            self.error(
                "ERR-06",
                f"«fecha_conocimiento» ({conocimiento}) es anterior a «fecha_hecho» ({hecho})",
                _ruta(ruta, "fecha_conocimiento"),
            )
        return Evento(id_, tipo, hecho, conocimiento, relevante, descripcion, anio)

    # --- Hechos posteriores a la fecha de referencia (§7) ---------------------

    def _comprobar_hechos_posteriores(self, fecha_referencia):
        # Modelo, V-11: un error por cada fecha. `anio_natural` no es una fecha y no
        # se comprueba.
        for ruta, fecha in self.hechos:
            if fecha > fecha_referencia:
                self.error(
                    "ERR-08",
                    f"{fecha} es posterior a la fecha de referencia ({fecha_referencia})",
                    ruta,
                )
