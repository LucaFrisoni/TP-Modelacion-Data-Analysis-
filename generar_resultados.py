"""Genera las tablas (CSV) y figuras (PNG o HTML) del TP en la carpeta resultados/.

Uso:  docker compose run --rm app python generar_resultados.py
Usa los datos del grupo y las decisiones de calculos/datos/, así los resultados son reproducibles.
"""

import sys
from pathlib import Path

from calculos import reporte
from calculos.datos import decisiones as D
from calculos.items import item6

SALIDA = Path(__file__).parent / "resultados"


def calibracion_definida(valor) -> item6.Calibracion | None:
    return item6.Calibracion(*valor, origen="Definida por el equipo") if valor else None


def guardar(archivos: dict[str, bytes]):
    for nombre, contenido in archivos.items():
        (SALIDA / nombre).write_bytes(contenido)
        print(f"  {nombre}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    SALIDA.mkdir(exist_ok=True)
    e = reporte.Entradas(cal3=calibracion_definida(D.CALIBRACION_ITEM3_C),
                         cal4=calibracion_definida(D.CALIBRACION_ITEM4_C))
    print("Resolviendo el Ítem 5…")
    resultados_item5 = reporte.resolver_item5(e)
    print("Tablas:")
    guardar({f"{n}.csv": reporte.csv_bytes(df) for n, df in reporte.tablas(e, resultados_item5).items()})
    print("Figuras:")
    guardar(reporte.imagenes(reporte.figuras(e, resultados_item5)))
    print(f"Listo. Resultados en {SALIDA}")


if __name__ == "__main__":
    main()
