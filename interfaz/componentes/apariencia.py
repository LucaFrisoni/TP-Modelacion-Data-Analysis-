"""Apariencia de la app: logo de FIUBA, estilos propios, tema claro/oscuro y esqueleto de carga."""

from contextlib import contextmanager
from pathlib import Path

import streamlit as st

RECURSOS = Path(__file__).parent.parent / "recursos"
_CLAVE = "modo_oscuro"
_PAGINAS_VISTAS = "paginas_vistas"

# Silueta de una página (título, texto, tarjetas y gráfico); la animación está en estilos.css.
_ESQUELETO = """<div class="tp-esqueleto" aria-busy="true" aria-label="Cargando">
  <div class="tp-hueso tp-hueso-titulo"></div>
  <div class="tp-hueso tp-hueso-linea"></div>
  <div class="tp-hueso tp-hueso-linea tp-hueso-corta"></div>
  <div class="tp-esqueleto-fila"><div class="tp-hueso tp-hueso-tarjeta"></div>
    <div class="tp-hueso tp-hueso-tarjeta"></div></div>
  <div class="tp-hueso tp-hueso-grafico"></div>
</div>"""

# En el tema oscuro el color principal es claro: el texto de los botones principales va oscuro.
_CSS_OSCURO = '<style>[data-testid="stBaseButton-primary"] { color: #130f0e; }</style>'

# Los temas claro y oscuro están en .streamlit/config.toml. Este script cambia el tema de Streamlit
# (el mismo que ofrece el menú ⋮) para que coincida con el interruptor del panel lateral.
_SCRIPT = """<script>
(() => {
  const quiere = "__TEMA__";
  const [r, g, b] = getComputedStyle(document.querySelector(".stApp")).backgroundColor.match(/\\d+/g).map(Number);
  if ((0.299 * r + 0.587 * g + 0.114 * b < 128) === (quiere === "Dark")) return;
  document.querySelector('[data-testid="stMainMenuButton"]')?.click();
  const elegir = (intentos) => {
    const opcion = document.querySelector(`[data-testid="stMainMenuItem-theme-${quiere}"]`);
    if (opcion) {
      opcion.click();
      const escape = new KeyboardEvent("keydown", {key: "Escape", code: "Escape", keyCode: 27, bubbles: true});
      setTimeout(() => (document.activeElement || document.body).dispatchEvent(escape), 50);
    } else if (intentos > 0) setTimeout(() => elegir(intentos - 1), 50);
  };
  elegir(40);
})();
</script>"""


def modo_oscuro() -> bool:
    return bool(st.session_state.get(_CLAVE, False))


def estilos():
    """Estilos propios (títulos, tarjetas, encabezado) y logo de FIUBA según el tema."""
    st.html(RECURSOS / "estilos.css")
    if modo_oscuro():
        st.html(_CSS_OSCURO)
    variante = "oscuro" if modo_oscuro() else "claro"
    st.logo(RECURSOS / f"logo_fiuba_{variante}.png", size="large", link="https://www.fi.uba.ar/",
            icon_image=RECURSOS / f"emblema_fiuba_{variante}.png")


def interruptor_tema():
    """Interruptor del panel lateral; arranca según el tema del sistema operativo."""
    if _CLAVE not in st.session_state:
        st.session_state[_CLAVE] = st.context.theme.type == "dark"
    st.toggle("Modo oscuro", key=_CLAVE)
    st.html(_SCRIPT.replace("__TEMA__", "Dark" if modo_oscuro() else "Light"), unsafe_allow_javascript=True)


@contextmanager
def esqueleto(pagina: str):
    """La primera vez que se abre cada página en la sesión, muestra una silueta mientras se calcula.

    El contenido real queda oculto (por CSS) hasta que termina y aparece completo, con un fundido.
    """
    vistas = st.session_state.setdefault(_PAGINAS_VISTAS, set())
    lugar = None if pagina in vistas else st.empty()
    if lugar is not None:
        lugar.html(_ESQUELETO)
    try:
        yield
        vistas.add(pagina)  # solo si terminó: si se interrumpe para recalcular, el esqueleto sigue
    finally:  # también si la página falla
        if lugar is not None:
            lugar.empty()
