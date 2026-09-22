"""Línea de órdenes: plazos-actualizacion FICHERO [--json]."""

import argparse
import sys

from actualizacion.carga import cargar_fichero
from actualizacion.salida import como_json, informe, texto

EPILOG = (
    "códigos de salida: 0 si, en la fecha de referencia, los seis regímenes (ley_rd, amlr, "
    "T-1 a T-4) dan el mismo estado y ninguno es «indeterminado»; 1 si difieren o alguno es "
    "«indeterminado»; 2 si el fichero no se puede leer o la entrada no es válida."
)


class _Formato(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix or "uso: ")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="plazos-actualizacion",
        description=(
            "Calcula la fecha de la próxima revisión obligatoria de la información de un cliente de "
            "prevención del blanqueo de capitales con el RD 304/2014, con el AMLR y con cada lectura "
            "de la transición entre ambos, muestra dónde difieren y qué hay que decidir para salir "
            "de cada «indeterminado». Es un cálculo bajo las lecturas que declara la especificación, "
            "no una determinación jurídica."
        ),
        epilog=EPILOG,
        formatter_class=_Formato,
        add_help=False,
    )
    argumentos = parser.add_argument_group("argumentos")
    argumentos.add_argument("fichero", help="fichero JSON con el cliente (docs/modelo-datos.md)")
    opciones = parser.add_argument_group("opciones")
    opciones.add_argument("-h", "--help", action="help", help="muestra esta ayuda y termina")
    opciones.add_argument("--json", action="store_true", help="emite el informe en JSON en lugar de texto")
    args = parser.parse_args(argv)  # un uso incorrecto termina con código 2 (argparse)

    try:
        carga = cargar_fichero(args.fichero)
    except FileNotFoundError:
        return _error(parser, f"no existe el fichero {args.fichero}")
    except IsADirectoryError:
        return _error(parser, f"{args.fichero} es un directorio")
    except UnicodeDecodeError:
        return _error(parser, f"el fichero {args.fichero} no está codificado en UTF-8")
    except OSError as e:
        return _error(parser, f"no se puede leer el fichero {args.fichero}: {e.strerror}")

    inf = informe(carga)
    if args.json:
        print(como_json(inf))
    else:
        print(texto(inf), end="")
    return codigo_de_salida(inf)


def codigo_de_salida(inf) -> int:
    """§10.3."""
    if not inf.valida:
        return 2
    # D-38: solo cuenta el estado; un `indeterminado` da 1 aunque los seis coincidan.
    if inf.estados_distintos or inf.hay_indeterminado:
        return 1
    return 0


def _error(parser, mensaje):
    print(f"{parser.prog}: error: {mensaje}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
