"""Pruebas de integración de los ítems con los datos reales del grupo (NREF = 0.35, tabla B)."""

import json

import pytest

from calculos.items import item1, item2, item3, item4, item5, item6
from calculos.items.configuracion import Configuracion
from calculos.modelo.soaking import Soaking
from calculos.presentacion.formato import texto_cifras

CFG = Configuracion(grado_c=3, convencion_sk="intervalos")


# Los parámetros de proceso del grupo salen de NREF = 0.35 según las fórmulas del enunciado.
def test_configuracion_usa_los_datos_del_grupo():
    op = CFG.operacion_base()
    assert (CFG.nref, CFG.tabla_c) == (0.35, "B")
    assert (op.cad_s, op.T1_C, op.T2_C) == pytest.approx((28.5, 602.5, 602.5))


# Requisito del Ítem 1c: el estudio de paso debe mostrar el orden de cada método.
def test_estudio_paso_muestra_orden_1_y_2():
    df = item1.estudio_paso(CFG, "K", subpasos=(1, 2))
    cocientes = df.dropna().set_index("método")["cociente vs h anterior"]
    assert cocientes["EULER"] == pytest.approx(2.0, rel=0.05)
    assert cocientes["RK2"] == pytest.approx(4.0, rel=0.05)


# La radiación debe calentar más que la convección sola (lo que el Ítem 2b pide analizar).
def test_radiacion_eleva_la_temperatura_final():
    assert item2.item2b(CFG).T_final_C > item1.resolver(CFG)["rk2"].T_final_C


# Ítem 4: la cadencia nueva da 1,15 veces más tubos por unidad de tiempo.
def test_cadencia_del_item4_aumenta_productividad_15_por_ciento():
    assert 28.5 / item4.cadencia_nueva_s(CFG) == pytest.approx(1.15)


# Ítem 5 de punta a punta con los datos del grupo: si un método informa convergencia,
# volver a simular en la solución debe cumplir las tolerancias del Ítem 3.
@pytest.mark.parametrize("caso", ["A", "B", "C"])
def test_newton_converge_y_cumple_objetivos_al_resimular(caso):
    tsk = item5.objetivos(CFG)[caso]
    r = item5.resolver(CFG, tsk, "Newton-Raphson")
    assert r.convergio, r.mensaje
    _, sk = item3.evaluar_operacion(CFG, CFG.operacion_base().con_temperaturas(*r.x))
    assert item3.verificar_objetivo(sk, tsk).cumple


# Las configuraciones del Ítem 5 se guardan en JSON y deben volver idénticas.
def test_opciones_item5_sobreviven_ida_y_vuelta_por_json():
    original = item5.OpcionesMetodo(delta_C=7.5, J_punto_fijo=((0.0, 1.0), (1.0, 0.0)), amortiguado=True)
    assert item5.OpcionesMetodo.desde_dict(json.loads(json.dumps(original.a_dict()))) == original


# Un JSON con campos ajenos no debe aceptarse en silencio como configuración.
def test_opciones_item5_rechaza_campos_desconocidos():
    with pytest.raises(ValueError, match="desconocidos"):
        item5.OpcionesMetodo.desde_dict({"otro": 1})


# Calibración manual: cada combinación nueva se numera; recalcular la misma no la duplica.
def test_registrar_iteracion_numera_y_no_duplica():
    historial, op = [], CFG.operacion_base()
    sk, v = Soaking(2.0, 560.0, 565.0, None), item3.Verificacion(False, True)
    assert item3.registrar_iteracion(historial, op, sk, v)
    assert not item3.registrar_iteracion(historial, op, sk, v)
    assert item3.registrar_iteracion(historial, op.con_temperaturas(650.0, 602.5), sk, v)
    assert [f["Iteración"] for f in historial] == [1, 2]


# La tabla del Ítem 6 muestra cada valor en su fila; sin calibrar, los Ítems 3 y 4 lo indican.
def test_tabla_resumen_filas_y_calibraciones_pendientes():
    df = item6.tabla_resumen(CFG, None, item6.Calibracion(700.0, 590.0, "Definida por el equipo"),
                             item5.OpcionesMetodo())
    assert list(df[df["Ítem"] == "1"]["Magnitud"].str.contains("Temperatura final")) == [True] * 3
    assert set(df[df["Ítem"] == "3"]["Resultado"]) == {item6.SIN_CALIBRAR}
    assert list(df[df["Ítem"] == "4"]["Resultado"]) == ["700", "590"]


# La tabla debe mostrar 3 cifras significativas, como pide el Ítem 6.
@pytest.mark.parametrize("valor, texto", [(597.711, "598"), (2.0, "2.00"), (0.012345, "0.0123"),
                                           (10.04, "10.0")])
def test_formato_tres_cifras_significativas(valor, texto):
    assert texto_cifras(valor, 3) == texto
