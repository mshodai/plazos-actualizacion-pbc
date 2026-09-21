"""El ejemplo completo de docs/modelo-datos.md, §1, leído del propio documento.

Si el ejemplo cambia y deja de ser válido, o el modelo cambia y el ejemplo no,
estos tests fallan. También comprueban que los códigos y las decisiones de
validación del documento son los del código.
"""

import dataclasses
import re
from datetime import date
from pathlib import Path

from actualizacion.carga import cargar
from actualizacion.modelo import ERRORES, Clasificacion, Evento, Revision, VersionManual

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "docs" / "modelo-datos.md"
CARGA = RAIZ / "src" / "actualizacion" / "carga.py"


def _seccion(texto, titulo):
    """Texto desde el encabezado `titulo` hasta el siguiente de igual o mayor nivel."""
    nivel = titulo.split(" ")[0]
    inicio = texto.index(titulo)
    fin = re.search(rf"^#{{1,{len(nivel)}}} ", texto[inicio + len(titulo) :], re.MULTILINE)
    return texto[inicio : inicio + len(titulo) + fin.start()] if fin else texto[inicio:]


TEXTO = MODELO.read_text(encoding="utf-8")
EJEMPLO = re.search(r"```json\n(.*?)\n```", _seccion(TEXTO, "## 1. Ejemplo completo"), re.DOTALL).group(1)
RESULTADO = cargar(EJEMPLO)


def test_el_ejemplo_es_valido():
    assert RESULTADO.errores == ()
    assert RESULTADO.valida


def test_estructura_leida():
    entrada = RESULTADO.entrada
    assert entrada.version_modelo == 1
    assert entrada.fecha_referencia == date(2027, 11, 15)
    assert entrada.sujeto.actividad == "otra"

    v2019, v2027 = entrada.manual.versiones
    assert isinstance(v2019, VersionManual)
    assert (v2019.id, v2019.vigente_desde) == ("MANUAL-2019", date(2019, 1, 1))
    assert v2019.periodicidad("medio") == 36
    assert v2019.plazo_revision_por_evento_dias is None
    assert v2019.revision_anticipada_reinicia_plazo is None
    assert v2027.periodicidad("alto") == 6
    assert v2027.periodicidad("inexistente") is None
    assert (v2027.plazo_revision_por_evento_dias, v2027.revision_anticipada_reinicia_plazo) == (30, True)

    cliente = entrada.cliente
    assert cliente.id == "CLI-0042"
    assert cliente.fecha_inicio_relacion == date(2019, 5, 10)
    assert cliente.fecha_terminacion_relacion is None

    c1, c2, c3 = cliente.clasificaciones
    assert all(isinstance(c, Clasificacion) for c in cliente.clasificaciones)
    assert (c1.superior_al_promedio, c1.riesgo_elevado_amlr, c1.medidas_seccion_4_amlr) == (False, None, None)
    assert (c2.fecha, c2.riesgo_elevado_amlr) == (date(2027, 7, 10), False)
    assert (c3.nivel_entidad, c3.superior_al_promedio, c3.medidas_seccion_4_amlr) == ("alto", True, True)

    r1, r2, r3 = cliente.revisiones
    assert all(isinstance(r, Revision) for r in cliente.revisiones)
    assert (r1.tipo, r1.resultado, r1.eventos) == ("inicial", "actualizada", ())
    assert (r2.tipo, r2.fecha, r2.resultado) == ("periodica", date(2025, 2, 14), "sin_cambios")
    assert (r3.tipo, r3.eventos) == ("por_evento", ("EV-1",))

    (evento,) = cliente.eventos
    assert isinstance(evento, Evento)
    assert evento.tipo == "cambio_titularidad_real_o_control"
    assert (evento.fecha_hecho, evento.fecha_conocimiento) == (date(2027, 9, 1), date(2027, 9, 12))
    assert evento.relevante_segun_entidad is True
    assert evento.anio_natural is None


def _campos_fecha(objeto, ruta="entrada"):
    """(ruta, valor) de todos los campos cuyo nombre empieza por «fecha» o es `vigente_desde`."""
    if dataclasses.is_dataclass(objeto):
        for campo in dataclasses.fields(objeto):
            valor = getattr(objeto, campo.name)
            if campo.name.startswith("fecha") or campo.name == "vigente_desde":
                yield f"{ruta}.{campo.name}", valor
            yield from _campos_fecha(valor, f"{ruta}.{campo.name}")
    elif isinstance(objeto, tuple):
        for i, elemento in enumerate(objeto):
            yield from _campos_fecha(elemento, f"{ruta}[{i}]")


def test_todas_las_fechas_son_date():
    fechas = list(_campos_fecha(RESULTADO.entrada))
    assert len(fechas) == 13
    for ruta, valor in fechas:
        assert valor is None or type(valor) is date, ruta


def test_los_codigos_son_los_del_documento():
    """§9.1: los códigos de la tabla son los de ERRORES, en el mismo orden."""
    tabla = _seccion(TEXTO, "### 9.1. Errores")
    assert re.findall(r"^\| `(ERR-\d\d)` \|", tabla, re.MULTILINE) == list(ERRORES)


def test_las_decisiones_citadas_en_el_codigo_existen():
    """Cada «Modelo, V-n» del código es una fila del §9.2, y las filas son V-1 a V-23."""
    tabla = _seccion(TEXTO, "### 9.2. Decisiones de validación")
    decisiones = re.findall(r"^\| (V-\d+) \|", tabla, re.MULTILINE)
    assert decisiones == [f"V-{n}" for n in range(1, 24)]
    citadas = set(re.findall(r"Modelo, (V-\d+)", CARGA.read_text(encoding="utf-8")))
    assert citadas and citadas <= set(decisiones)
