"""La línea de órdenes plazos-actualizacion y sus códigos de salida (§10.3)."""

import json
import subprocess
import sys

import pytest

from actualizacion.cli import main


def _datos(referencia, clasificaciones, revisiones, eventos=(), periodicidades=None, inicio="2020-03-02"):
    return {
        "version_modelo": 1,
        "fecha_referencia": referencia,
        "sujeto": {"actividad": "otra"},
        "manual": {
            "versiones": [
                {
                    "id": "M",
                    "vigente_desde": "2000-01-01",
                    "periodicidades": [
                        {"nivel_entidad": n, "meses": m} for n, m in (periodicidades or {"medio": 36}).items()
                    ],
                    "plazo_revision_por_evento_dias": None,
                    "revision_anticipada_reinicia_plazo": None,
                }
            ]
        },
        "cliente": {
            "id": "C",
            "fecha_inicio_relacion": inicio,
            "fecha_terminacion_relacion": None,
            "clasificaciones": clasificaciones,
            "revisiones": revisiones,
            "eventos": list(eventos),
        },
    }


CLASIFICACION = [
    {
        "fecha": "2020-03-02",
        "nivel_entidad": "medio",
        "superior_al_promedio": False,
        "riesgo_elevado_amlr": False,
        "medidas_seccion_4_amlr": False,
    }
]
INICIAL = [{"id": "R1", "tipo": "inicial", "fecha": "2020-03-02", "resultado": "actualizada", "eventos": []}]


@pytest.fixture
def fichero(tmp_path):
    def escribir(datos, nombre="entrada.json"):
        ruta = tmp_path / nombre
        ruta.write_text(json.dumps(datos) if not isinstance(datos, str) else datos, encoding="utf-8")
        return str(ruta)

    return escribir


def test_codigo_0_si_los_seis_coinciden(fichero, capsys):
    # Ejemplo 1 después de A: vencida en los seis. D-38: las fechas distintas no cuentan.
    assert main([fichero(_datos("2028-01-15", CLASIFICACION, INICIAL))]) == 0
    assert "vencida" in capsys.readouterr().out


def test_codigo_1_si_difieren(fichero, capsys):
    # Ejemplo 9 en 2030: ley_rd en plazo, amlr vencida.
    clasificaciones = [
        {**CLASIFICACION[0], "fecha": "2012-02-01", "nivel_entidad": "bajo", "riesgo_elevado_amlr": None, "medidas_seccion_4_amlr": None},
        {**CLASIFICACION[0], "fecha": "2027-07-10", "nivel_entidad": "bajo"},
    ]
    revisiones = [
        {"id": "R1", "tipo": "inicial", "fecha": "2012-02-01", "resultado": "actualizada", "eventos": []},
        {"id": "R2", "tipo": "periodica", "fecha": "2024-01-15", "resultado": "actualizada", "eventos": []},
    ]
    datos = _datos("2030-01-01", clasificaciones, revisiones, periodicidades={"bajo": 120}, inicio="2012-02-01")
    assert main([fichero(datos)]) == 1
    salida = capsys.readouterr().out
    assert "T-1 a T-4 no coinciden" in salida


def test_codigo_1_con_indeterminado_aunque_coincidan(fichero, capsys):
    # D-38: antes de A, los T-n son ley_rd; aquí todos indeterminado por SP.
    clasificaciones = [{**CLASIFICACION[0], "superior_al_promedio": None}]
    assert main([fichero(_datos("2021-06-01", clasificaciones, INICIAL))]) == 1
    assert "Qué hay que decidir" in capsys.readouterr().out


def test_json(fichero, capsys):
    assert main([fichero(_datos("2028-01-15", CLASIFICACION, INICIAL)), "--json"]) == 0
    datos = json.loads(capsys.readouterr().out)
    assert datos["valida"] is True
    assert set(datos["regimenes"]) == {"ley_rd", "amlr", "T-1", "T-2", "T-3", "T-4"}


def test_entrada_no_valida(fichero, capsys):
    assert main([fichero({"version_modelo": 2})]) == 2
    assert capsys.readouterr().out.startswith("La entrada no es válida")


def test_entrada_no_valida_en_json(fichero, capsys):
    assert main([fichero("{", "roto.json"), "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["valida"] is False


def test_fichero_inexistente(tmp_path, capsys):
    assert main([str(tmp_path / "no.json")]) == 2
    salida = capsys.readouterr()
    assert salida.out == ""
    assert "plazos-actualizacion: error: no existe el fichero" in salida.err


def test_directorio(tmp_path, capsys):
    assert main([str(tmp_path)]) == 2
    assert "es un directorio" in capsys.readouterr().err


def test_no_utf8(tmp_path, capsys):
    ruta = tmp_path / "latin1.json"
    ruta.write_bytes('{"cliente": "Peña"}'.encode("latin-1"))
    assert main([str(ruta)]) == 2
    assert "no está codificado en UTF-8" in capsys.readouterr().err


def test_uso_incorrecto(capsys):
    with pytest.raises(SystemExit) as salida:
        main([])
    assert salida.value.code == 2
    assert "uso: plazos-actualizacion" in capsys.readouterr().err


def test_ayuda(capsys):
    with pytest.raises(SystemExit) as salida:
        main(["--help"])
    assert salida.value.code == 0
    ayuda = capsys.readouterr().out
    assert "códigos de salida" in ayuda
    assert "--json" in ayuda


def test_como_modulo(fichero):
    # La orden declarada en pyproject.toml apunta a actualizacion.cli:main.
    resultado = subprocess.run(
        [sys.executable, "-m", "actualizacion.cli", fichero(_datos("2028-01-15", CLASIFICACION, INICIAL))],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": "src"},
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.startswith("Cliente C")
