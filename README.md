# TP Modelación Numérica (CB051): revenido de tubos de acero

Aplicación web de análisis numérico para el TP _"Métodos numéricos aplicados a la ingeniería de procesos"_ (FIUBA, 2.º cuatrimestre 2026). Simula la temperatura de un tubo de acero dentro de un horno de revenido, compara métodos numéricos y calibra las condiciones de operación resolviendo un sistema no lineal.

**Integrantes:** Rocío Menán Iglesias (113591) · Julieta Lara Arregui (113517) · Marcelo Tomás Cuneo Senmache (113790) · Luca Frisoni (113497)

**Stack:** Python · NumPy · pandas · Plotly · Streamlit · Docker · pytest

> **Datos del grupo:** NREF = 0.35, tabla B. Algunas decisiones del equipo (grado de C(T), conteo de Sk, configuración del Ítem 5) todavía tienen valores de ejemplo;

## Funcionalidades

| Página       | Contenido                                                                                                   |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| Introducción | Integrantes, consigna en PDF, planteo del problema, modelo, métodos, parámetros y qué cambia en cada ítem   |
| Ítem 1       | Euler explícito, RK2 y solución analítica; error relativo en escala log; estudio del orden de convergencia  |
| Ítem 2       | Ajustes de C(T) por mínimos cuadrados (grados 0 a 6); efecto de la radiación; Sk y Tsk con la banda marcada |
| Ítem 3       | Calibración manual de T1 y T2 con indicadores de tolerancia e iteraciones numeradas descargables            |
| Ítem 4       | Nueva condición con +15 % de productividad, a partir del resultado del Ítem 3                               |
| Ítem 5       | NR, secante (enunciado y Broyden) y punto fijo; configuraciones con nombre (JSON); historiales en CSV       |
| Ítem 6       | Tabla resumen con 3 cifras significativas                                                                   |

- **Gráficos:** son interactivos. El ícono de cámara descarga cada uno en PNG de alta resolución.
- **Tablas:** cada una se descarga en CSV.
- **Descargas globales (panel lateral):** todas las figuras en PNG y todas las tablas en CSV, cada grupo en un ZIP, con las decisiones y calibraciones de la sesión. Las figuras salen siempre con estilo claro, para el informe.
- **Carga:** la primera vez que se abre cada página se ve una silueta animada hasta que todo está calculado, y después el contenido aparece completo con un fundido.
- **Tema claro y oscuro:** interruptor en el panel lateral (también desde el menú ⋮). Los colores están en `.streamlit/config.toml` y los estilos propios en `interfaz/recursos/estilos.css`.

## Desarrollo local con Docker

Requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker compose up --build        # app en http://localhost:8501
docker compose down              # detener
```

- El puerto se define en `.env`. Para crear ese archivo, copiá `.env.example`.
- El código se monta como volumen: los cambios en `interfaz/` se ven al recargar la página. Los cambios en `calculos/` requieren `docker compose restart`.

| Tarea                                            | Comando                                                    |
| ------------------------------------------------ | ---------------------------------------------------------- |
| Pruebas                                          | `docker compose run --rm app python -m pytest`             |
| Figuras y tablas para el informe (`resultados/`) | `docker compose run --rm app python generar_resultados.py` |

**La imagen tiene dos etapas:**

- **Base (las dos etapas):** incluye Chromium, que kaleido necesita para exportar las figuras a PNG.
- **`dev`:** agrega pytest.
- **`prod`:** la etapa por defecto. Solo tiene lo necesario para servir la app y corre con un usuario sin privilegios. Respeta la variable `PORT` que asignan las plataformas de despliegue.

## Despliegue

**Recomendado: [Streamlit Community Cloud](https://share.streamlit.io).** Es gratis, está pensado para Streamlit y se redespliega solo con cada `git push`.

1. Subí el proyecto a un repositorio de GitHub.
2. En share.streamlit.io elegí _Create app_, el repositorio, la rama y el archivo `app.py`. En _Advanced settings_ elegí Python 3.12 o superior.
3. Compartí la URL (`https://<nombre>.streamlit.app`). Los usuarios solo necesitan el link.

Detalles a tener en cuenta:

- Usa `requirements.txt`, `packages.txt` (instala Chromium para exportar PNG) y `.streamlit/config.toml`. El Dockerfile no se usa en esta plataforma. Si Chromium no estuviera disponible, el ZIP de figuras trae HTML interactivos en lugar de PNG.
- Si la app no recibe visitas por un tiempo, se suspende. La primera visita la reactiva en unos segundos.

**Alternativa con Docker: [Render](https://render.com) (plan gratuito).** Creá un _Web Service_ desde el repositorio con runtime _Docker_. Render construye la etapa `prod` y le asigna el puerto por `PORT`. Se suspende tras 15 minutos sin uso, y la primera carga después tarda entre 30 y 60 s.

## Datos del grupo y decisiones del equipo

- **[calculos/datos/grupo.py](calculos/datos/grupo.py):** integrantes, NREF y tabla asignados. Son fijos.
- **[calculos/datos/decisiones.py](calculos/datos/decisiones.py):** lo que decide el equipo. Cada valor tiene un comentario `TODO` que explica qué es y dónde se usa. Al hacer `git push`, la app publicada lo toma.
  1. `GRADO_C` y `CONVENCION_SK`: en la app se pueden probar desde el panel lateral.
  2. Configuración del Ítem 5: el equipo la arma en la app, la descarga en JSON y se copia acá.
  3. `CALIBRACION_ITEM3_C` y `CALIBRACION_ITEM4_C`: resultados finales de la calibración manual.

## Validación

Hay 87 pruebas automáticas. Verifican, entre otras cosas:

- **Integradores:** Euler y RK2 coinciden con la fórmula cerrada de la ecuación lineal y tienen orden 1 y 2.
- **Ítem 1:** RK2 reproduce la solución analítica.
- **Datos derivados:** la masa coincide con el volumen de la corona circular, y el ejemplo del enunciado (NREF = 0.5 → cad = 30 s, T = 625 °C) se reproduce.
- **Mínimos cuadrados:** el ajuste de grado 6 interpola la tabla y coincide con `numpy.polyfit`.
- **Sk y Tsk:** se calculan bien sobre series conocidas.
- **Ítem 5:** la J_SEC del enunciado es siempre singular, y Newton y Broyden resuelven un sistema con solución conocida.
- **Ítems:** con los datos del grupo, Newton converge en los casos A, B y C y la solución cumple las tolerancias al re-simular.
- **Descargas:** los ZIP contienen cada tabla completa; las figuras de los Ítems 3 y 4 aparecen solo con calibración; la versión oscura de un gráfico no altera la del informe.
- **Aplicación web:** cada página se ejecuta sin errores; las iteraciones del Ítem 3 se numeran; el Ítem 4 toma el resultado del Ítem 3; las configuraciones del Ítem 5 se guardan con nombre; el modo oscuro funciona; la introducción muestra integrantes y padrones; el esqueleto de carga desaparece al terminar cada página.

Las pruebas **no** validan las decisiones académicas pendientes (grado de C(T), convención de Sk, etc.).

## Organización del código

```
app.py                       punto de entrada (navegación y panel lateral)
calculos/                    todo el cálculo, independiente de la interfaz
  datos/                     enunciado.py · grupo.py (integrantes, NREF, tabla) · decisiones.py (equipo)
  modelo/                    parámetros, C(T), ecuación diferencial, simulación, soaking, unidades
  metodos/                   integradores (Euler, RK2) · minimos_cuadrados · sistemas_no_lineales
  items/                     configuracion.py · item1.py … item6.py (cálculo de cada ítem)
  presentacion/              gráficos Plotly (tema claro y oscuro) y formato de cifras significativas
  reporte.py                 arma todas las figuras y tablas y las empaqueta en ZIP
interfaz/
  paginas/                   introduccion.py · item1.py … item6.py
  componentes/               panel lateral, tema, descargas, calibración manual, opciones del Ítem 5, sesión
  recursos/                  logos de FIUBA, consigna del TP (PDF) y estilos CSS
generar_resultados.py        exporta figuras y tablas para el informe
tests/                       pruebas automáticas
Dockerfile, docker-compose.yml, .env.example, packages.txt
```

**Decisiones de implementación:**

- Las cuentas se hacen en K y s; los resultados se muestran en °C y min.
- C(T) recibe °C porque las tablas están en °C.
- En x = L/2 exacto rige T1, con una tolerancia para que el redondeo no cambie ese punto de zona.
- Los métodos numéricos están implementados a mano. NumPy solo se usa para arreglos y sistemas lineales pequeños.

**Entrega a la cátedra:** el campus exige que el material de cálculo se llame `software_grupo_xx`. Comprimí esta carpeta con ese nombre al entregar.
