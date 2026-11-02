"""
Almacenamiento del celular según fotos y videos  ·  EC4 Cálculo I   (versión de escritorio)

Qué hace este programa:
  1. Lee los datos y calcula las regresiones con Python (archivo calculos.py).
  2. Abre una ventana con la interfaz (carpeta web/) y le entrega los resultados.

Cómo abrirlo:   python app.py
"""
import json
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from calculos import CARPETA, ajustar, leer_datos

WEB = CARPETA / "web"
TITULO = "Almacenamiento del celular según fotos y videos"


class Manejador(SimpleHTTPRequestHandler):
    """Sirve la carpeta web/ y dos respuestas en JSON: /api/datos y /api/ajustes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta == "/api/datos":
            return self.responder({"filas": leer_datos()})
        if ruta == "/api/ajustes":
            return self.responder(ajustar(leer_datos()))
        return super().do_GET()

    def responder(self, contenido):
        cuerpo = json.dumps(contenido, allow_nan=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):  # no llenar la consola de mensajes
        pass


def esperar_en_consola():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def main():
    solo_servidor = "--servidor" in sys.argv
    en_navegador = "--navegador" in sys.argv
    puerto = 0
    if "--puerto" in sys.argv:
        puerto = int(sys.argv[sys.argv.index("--puerto") + 1])

    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    threading.Thread(target=servidor.serve_forever, daemon=True).start()

    if solo_servidor:
        print("Servidor listo en", url, "(Ctrl+C para cerrar)")
        return esperar_en_consola()

    if not en_navegador:
        try:
            import webview  # pywebview: abre una ventana propia, como una app

            webview.create_window(TITULO, url, width=1100, height=820, min_size=(380, 600))
            # En Windows se usa el motor de Edge (WebView2) para que se vea igual que en el navegador
            webview.start(gui="edgechromium" if sys.platform == "win32" else None)
            return
        except Exception as error:
            print("No se pudo abrir la ventana propia (", error, ").")

    print("Abriendo en el navegador:", url)
    print("Cierra esta consola para terminar el programa.")
    webbrowser.open(url)
    esperar_en_consola()


if __name__ == "__main__":
    main()
