"""Pruebas de la aplicación web: cada página se ejecuta y los flujos entre ítems funcionan."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).parent.parent
PAGINAS = ["introduccion", "item1", "item2", "item3", "item4", "item5", "item6"]


def abrir(pagina: str) -> AppTest:
    app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=180)
    app.run()
    return app.switch_page(f"interfaz/paginas/{pagina}.py").run()


# Un error en cualquier página la dejaría inutilizable para el equipo; esta prueba
# ejecuta cada una con los valores por defecto y verifica que no haya excepciones.
@pytest.mark.parametrize("pagina", PAGINAS)
def test_pagina_se_ejecuta_sin_excepciones(pagina):
    app = abrir(pagina)
    assert not app.exception, app.exception
    assert app.title, "la página no renderizó su título"


# Calibración manual (Ítem 3): la condición inicial es la iteración 1 y cada cambio de
# T1 suma una iteración numerada.
def test_item3_numera_cada_combinacion_probada():
    app = abrir("item3")
    app.number_input(key="item3_T1").set_value(680.0).run()
    historial = app.session_state["item3_historial"]
    assert [f["Iteración"] for f in historial] == [1, 2]
    assert historial[1]["T1 [°C]"] == 680.0


# El Ítem 4 parte del resultado del Ítem 3: sin él, se detiene y avisa; con él, muestra
# esas temperaturas fijas y el panel de la nueva condición.
def test_item4_usa_el_resultado_elegido_en_el_item3():
    app = abrir("item3")
    app.number_input(key="item3_T1").set_value(690.0).run()
    next(b for b in app.button if b.key == "usar_item3").click().run()
    app.switch_page("interfaz/paginas/item4.py").run()
    assert not app.exception
    assert app.number_input(key="item4_T1").value == 690.0


# Guardar una configuración del Ítem 5 con nombre la deja disponible y activa.
def test_item5_guarda_configuracion_con_nombre():
    app = abrir("item5")
    app.text_input(key="i5_nombre").set_value("Newton Δ 5").run()
    next(b for b in app.button if b.label == "Guardar").click().run()
    assert "Newton Δ 5" in app.session_state["i5_configs"]
    assert app.selectbox(key="i5_sel").value == "Newton Δ 5"


# El interruptor de tema cambia los gráficos a la versión oscura sin errores en la página.
def test_modo_oscuro_se_aplica_sin_errores():
    app = abrir("item2")
    app.toggle(key="modo_oscuro").set_value(True).run()
    assert not app.exception
    assert app.session_state["modo_oscuro"]


# La introducción muestra a los cuatro integrantes con su padrón.
def test_introduccion_muestra_integrantes_y_padrones():
    from calculos.datos.grupo import INTEGRANTES
    html = " ".join(h.proto.body for h in abrir("introduccion").get("html"))
    assert all(f"Padrón {padron}" in html for *_, padron in INTEGRANTES)


# El esqueleto de carga no debe quedar en pantalla al terminar, ni siquiera si la página
# se detiene antes (el Ítem 4 sin resultado del Ítem 3 llama a st.stop()).
@pytest.mark.parametrize("pagina", ["item2", "item4"])
def test_esqueleto_de_carga_desaparece_al_terminar(pagina):
    app = abrir(pagina)
    assert not any('class="tp-esqueleto"' in h.proto.body for h in app.get("html"))
