"""El corpus de corpus/: cada caso da el resultado que documenta.

Se comprueba de cuatro formas: el resultado calculado coincide con el
.esperado.json de cada caso; la línea de órdenes devuelve el código de salida
esperado sobre el fichero real; los ficheros son exactamente los que genera
corpus/generar.py; y el script falla sin escribir si una expectativa no se
cumple.
"""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from actualizacion.carga import cargar_fichero
from actualizacion.cli import main as cli
from actualizacion.salida import informe, texto

CORPUS = Path(__file__).resolve().parent.parent / "corpus"


def _generador():
    spec = importlib.util.spec_from_file_location("corpus_generar", CORPUS / "generar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


G = _generador()
ESPERADOS = sorted(CORPUS.glob("*.esperado.json"))
IDS = [p.name.removesuffix(".esperado.json") for p in ESPERADOS]


def _caso(sufijo):
    (caso,) = [c for c in G.CASOS if c.nombre[3:] == sufijo]
    return caso


def test_estan_todos_los_casos():
    assert IDS == [c.nombre for c in G.CASOS]
    assert len(ESPERADOS) == 9


@pytest.mark.parametrize("esperado", ESPERADOS, ids=IDS)
def test_cada_caso_da_su_resultado(esperado):
    datos = json.loads(esperado.read_text(encoding="utf-8"))
    carga = cargar_fichero(CORPUS / f"{datos['caso']}.json")
    assert carga.valida, carga.errores
    assert G.resumen(informe(carga)) == datos["resultado"]


@pytest.mark.parametrize("esperado", ESPERADOS, ids=IDS)
def test_la_linea_de_ordenes_da_el_codigo_esperado(esperado, capsys):
    datos = json.loads(esperado.read_text(encoding="utf-8"))
    fichero = str(CORPUS / f"{datos['caso']}.json")
    assert cli([fichero]) == datos["resultado"]["codigo_salida"]
    assert cli([fichero, "--json"]) == datos["resultado"]["codigo_salida"]
    capsys.readouterr()


def test_los_ficheros_son_los_que_genera_el_script():
    """Reproducible: si alguien edita un fichero a mano o cambia generar.py sin regenerar, falla."""
    generados = {"README.md": G.readme()}
    for caso in G.CASOS:
        generados.update(G.ficheros(caso))
    en_disco = {p.name: p.read_text(encoding="utf-8") for p in CORPUS.iterdir() if p.suffix in (".json", ".md")}
    assert en_disco == generados


def test_generar_dos_veces_da_lo_mismo():
    otro = _generador()
    assert otro.readme() == G.readme()
    assert [otro.ficheros(c) for c in otro.CASOS] == [G.ficheros(c) for c in G.CASOS]


def test_el_script_falla_sin_escribir_si_una_expectativa_no_se_cumple(tmp_path, monkeypatch):
    caso = _caso("revision-sin-cambios-vencida-con-ac-2")
    esperado = copy.deepcopy(caso.esperado)
    esperado["regimenes"]["ley_rd"]["fechas"] = ["2029-08-21"]
    mal = G.Caso(caso.nombre, caso.demuestra, caso.entrada, esperado)
    (diferencia,) = G.comprobar(mal)
    assert diferencia.startswith("ley_rd.fechas: se esperaba")

    monkeypatch.setattr(G, "DIRECTORIO", tmp_path)
    monkeypatch.setattr(G, "CASOS", [G.CASOS[0], mal])
    with pytest.raises(SystemExit):
        G.main()
    assert list(tmp_path.iterdir()) == []


def test_una_entrada_no_valida_es_un_fallo():
    caso = G.CASOS[0]
    entrada = copy.deepcopy(caso.entrada)
    entrada["regimen"] = "amlr"
    assert G.comprobar(G.Caso(caso.nombre, caso.demuestra, entrada, caso.esperado)) == [
        "la entrada no es válida: ['ERR-01']"
    ]


def test_estan_los_casos_pedidos():
    """Cada caso cubre lo que su nombre dice, en la fecha de referencia."""

    def reg(sufijo, regimen):
        return _caso(sufijo).esperado["regimenes"][regimen]

    def estados(sufijo):
        return {r: e["estado"] for r, e in _caso(sufijo).esperado["regimenes"].items()}

    # Los seis coinciden: código 0.
    assert len(set(estados("mismo-resultado-en-los-seis").values())) == 1
    assert _caso("mismo-resultado-en-los-seis").esperado["codigo_salida"] == 0

    # Revisado a tiempo, sin cambios, vencido con AC-2.
    ac = reg("revision-sin-cambios-vencida-con-ac-2", "amlr")["decisiones"]["AC"]["respuestas"]
    assert ac["AC-2"]["estados"] == ["vencida"]
    assert reg("revision-sin-cambios-vencida-con-ac-2", "ley_rd")["estado"] == "en_plazo"

    # Cliente existente el 2027-07-10 con la transición divergente.
    transicion = estados("cliente-existente-transicion-diverge")
    assert len({transicion[t] for t in ("T-1", "T-2", "T-3", "T-4")}) > 1
    assert _caso("cliente-existente-transicion-diverge").entrada["cliente"]["fecha_inicio_relacion"] < "2027-07-10"

    # Persona del medio político: superior al promedio con el RD, sin riesgo elevado con el AMLR.
    (c,) = _caso("persona-del-medio-politico").entrada["cliente"]["clasificaciones"]
    assert (c["superior_al_promedio"], c["riesgo_elevado_amlr"], c["medidas_seccion_4_amlr"]) == (True, False, True)
    assert set(reg("persona-del-medio-politico", "amlr")["decisiones"]) == {"PB"}

    # Revisión anticipada: el «can reset».
    assert set(reg("revision-anticipada-puede-reiniciar", "ley_rd")["decisiones"]) == {"RA"}

    # Hecho y conocimiento a distinto lado del 2027-07-10, con el resultado dependiendo de ello.
    (ev,) = _caso("evento-conocido-despues-del-10-de-julio-de-2027").entrada["cliente"]["eventos"]
    assert ev["fecha_hecho"] < "2027-07-10" <= ev["fecha_conocimiento"]
    assert "TD" in reg("evento-conocido-despues-del-10-de-julio-de-2027", "T-1")["decisiones"]

    # El cliente de 2020 revisado en diciembre de 2027, vencido en enero de 2028 con AC-2 y TR-1.
    t1 = reg("revision-de-2027-que-ninguna-norma-cuenta", "T-1")
    assert set(t1["decisiones"]) == {"AC", "TR"}
    assert "2028-01-15" in t1["decisiones"]["TR"]["respuestas"]["TR-1"]["fechas"]
    assert "vencida" in t1["decisiones"]["TR"]["respuestas"]["TR-1"]["estados"]

    # Falta un dato de clasificación: la salida lo pregunta.
    sp = reg("falta-un-dato-de-clasificacion", "ley_rd")["decisiones"]["SP (2020-01-10)"]
    assert sp["pregunta"].endswith("¿lo es?")
    salida = texto(informe(cargar_fichero(CORPUS / f"{_caso('falta-un-dato-de-clasificacion').nombre}.json")))
    assert "no dice si el riesgo es superior al promedio: ¿lo es?" in salida

    # Relación terminada.
    assert set(estados("relacion-terminada").values()) == {"relacion_terminada"}


def test_los_datos_son_sinteticos():
    """Identificadores «FICTICIO» y descripciones «ficticio», sin datos de personas ni entidades."""
    for caso in G.CASOS:
        entrada = caso.entrada
        assert "FICTICIO" in entrada["cliente"]["id"]
        for version in entrada["manual"]["versiones"]:
            assert "FICTICIO" in version["id"]
        for revision in entrada["cliente"]["revisiones"]:
            assert "FICTICIO" in revision["id"]
        for evento in entrada["cliente"]["eventos"]:
            assert "FICTICIO" in evento["id"]
            assert evento["descripcion"].startswith("Hecho ficticio:")
