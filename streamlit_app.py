"""
Almacenamiento del celular según fotos y videos  ·  EC4 Cálculo I   (versión web con Streamlit)

Python lee los datos y calcula las regresiones (calculos.py). Después este
programa mete los resultados dentro de la misma interfaz de la app de escritorio
(web/index.html) y la muestra en la página.

Para probarla en tu computadora:   streamlit run streamlit_app.py
Para publicarla:                   ver PUBLICAR.txt
"""
import base64
import hashlib
import json
import re

import streamlit as st
import streamlit.components.v1 as components

from calculos import CARPETA, ajustar, leer_datos

WEB = CARPETA / "web"

st.set_page_config(page_title="Almacenamiento del celular según fotos y videos", page_icon="📱",
                   layout="wide", initial_sidebar_state="collapsed")

# Quita los adornos de Streamlit para que se vea como una app
st.markdown(
    """
    <style>
      header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
      footer, #MainMenu { display: none !important; }
      .block-container, [data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
      [data-testid="stAppViewContainer"], .stApp { background: #4a1f34; }
      iframe { height: 100vh !important; border: 0; display: block; }
    </style>
    """,
    unsafe_allow_html=True,
)


def huella():
    """Código que cambia cuando cambia la interfaz, los datos o los cálculos.
    Sirve para que la página guardada en memoria se rehaga sola después de cada actualización."""
    h = hashlib.sha256()
    for archivo in (WEB / "index.html", CARPETA / "datos.csv", CARPETA / "calculos.py"):
        h.update(archivo.read_bytes())
    return h.hexdigest()


@st.cache_data
def construir_pagina(version):
    """Arma el HTML final: interfaz + fuentes + datos y ajustes calculados por Python.
    (`version` no se usa dentro: solo hace que se rehaga cuando cambia algún archivo.)"""
    html = (WEB / "index.html").read_text(encoding="utf-8")

    # Las letras se incrustan dentro del HTML, para que se vean sin archivos aparte
    def incrustar(m):
        datos = base64.b64encode((WEB / "fonts" / m.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{datos})"

    html = re.sub(r"url\(fonts/([^)]+\.woff2)\)", incrustar, html)

    # Resultado de Python entregado a la interfaz
    filas = leer_datos()
    carga = json.dumps({"datos": {"filas": filas}, "ajustes": ajustar(filas)}, allow_nan=False)
    carga = carga.replace("</", "<\\/")
    return html.replace("</head>", f"<script>window.GALERIA = {carga};</script>\n</head>", 1)


components.html(construir_pagina(huella()), height=900, scrolling=True)
