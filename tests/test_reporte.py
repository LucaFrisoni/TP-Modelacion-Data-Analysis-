"""Pruebas de las descargas globales (figuras y tablas en ZIP) y de la versión oscura de los gráficos."""

import io
import zipfile

import pandas as pd

from calculos import reporte
from calculos.items import item6
from calculos.presentacion import graficos as G

CAL3 = item6.Calibracion(690.0, 565.0, "Elegida en esta sesión")
CAL4 = item6.Calibracion(700.0, 575.0, "Elegida en esta sesión")


# Sin calibraciones, los Ítems 3 y 4 no tienen figura; al elegirlas, se agregan al ZIP.
def test_figuras_de_items_3_y_4_aparecen_solo_con_calibracion():
    sin = reporte.figuras(reporte.Entradas())
    con = reporte.figuras(reporte.Entradas(cal3=CAL3, cal4=CAL4))
    assert not {"item3_soaking", "item4_comparacion"} & set(sin)
    assert {"item3_soaking", "item4_comparacion"} <= set(con)


# El ZIP de tablas debe abrirse y cada CSV debe conservar las filas de su tabla (con acentos legibles).
def test_zip_de_tablas_contiene_cada_csv_completo():
    dfs = {"a": pd.DataFrame({"Ítem": ["1", "2"]}), "b": pd.DataFrame({"x": [1.5]})}
    with zipfile.ZipFile(io.BytesIO(reporte.zip_tablas(dfs))) as z:
        assert sorted(z.namelist()) == ["a.csv", "b.csv"]
        leida = pd.read_csv(z.open("a.csv"), encoding="utf-8-sig", dtype=str)
    assert leida.equals(dfs["a"])


# La síntesis del Ítem 6 forma parte de las tablas descargables con el método pedido.
def test_tablas_incluyen_resumen_del_item6():
    dfs = reporte.tablas(reporte.Entradas(metodo="Secante (Broyden)"))
    resumen = dfs["item6_resumen"]
    assert resumen[resumen["Ítem"].str.startswith("5")]["Origen"].str.contains("Broyden").all()


# En modo oscuro cada serie conserva su identidad (mismo tono, otro paso) y el fondo es oscuro;
# la figura original, que se exporta para el informe, no se modifica.
def test_version_oscura_recolorea_sin_tocar_la_original():
    fig = G.evolucion([G.Curva("RK2", [0, 1], [20, 30], color=G.SERIES[1])], "prueba")
    oscura = G.version_oscura(fig)
    assert oscura.data[0].line.color != G.SERIES[1]
    assert oscura.layout.paper_bgcolor != G.FONDO
    assert fig.data[0].line.color == G.SERIES[1] and fig.layout.paper_bgcolor == G.FONDO
