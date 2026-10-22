"""
Calculadora de Determinantes y Matriz Inversa - App Android con Kivy.
"""
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex as hexc

from determinantes import METODOS, matriz_desde_texto, parse_valor, resolver

MAX_DIM = 10

# Paleta "hibisco"
MAGENTA = hexc("#B00C60")
CREMA = hexc("#F6DF96")
VERDE = hexc("#658D10")
LIMA = hexc("#D7E525")
CELESTE = hexc("#BFF5F5")
TURQUESA = hexc("#00B7C7")
BLANCO = (1, 1, 1, 1)
TEXTO = hexc("#2E2A24")

Window.softinput_mode = "below_target"
Window.clearcolor = CELESTE


def con_fondo(widget, color, radio=12):
    """Dibuja un fondo redondeado detrás del widget."""
    with widget.canvas.before:
        Color(*color)
        rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radio)])
    widget.bind(pos=lambda w, v: setattr(rect, "pos", v),
                size=lambda w, v: setattr(rect, "size", v))
    return widget


def boton(texto, fondo, color_texto=BLANCO, **kw):
    b = Button(text=texto, bold=True, font_size=sp(16), color=color_texto,
               background_normal="", background_down="",
               background_color=(0, 0, 0, 0), **kw)
    con_fondo(b, fondo)
    return b


def entrada(**kw):
    return TextInput(multiline=False, background_normal="", background_active="",
                     background_color=BLANCO, foreground_color=TEXTO,
                     cursor_color=MAGENTA, **kw)


class OpcionMetodo(SpinnerOption):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ""
        self.background_color = TURQUESA
        self.color = BLANCO
        self.height = dp(44)


class Calculadora(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(8), **kw)
        self.celdas = []

        titulo = Label(text="[b]Determinantes e Inversa[/b]", markup=True,
                       font_size=sp(21), color=BLANCO,
                       size_hint_y=None, height=dp(48))
        self.add_widget(con_fondo(titulo, MAGENTA))

        # --- dimensiones
        fila = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        fila.add_widget(Label(text="Filas m:", color=TEXTO, bold=True,
                              size_hint_x=0.22))
        self.in_m = entrada(text="3", input_filter="int", font_size=sp(18),
                            size_hint_x=0.16)
        fila.add_widget(self.in_m)
        fila.add_widget(Label(text="Columnas n:", color=TEXTO, bold=True,
                              size_hint_x=0.28))
        self.in_n = entrada(text="3", input_filter="int", font_size=sp(18),
                            size_hint_x=0.16)
        fila.add_widget(self.in_n)
        btn = boton("Crear", TURQUESA, size_hint_x=0.24)
        btn.bind(on_release=lambda *_: self.crear_matriz())
        fila.add_widget(btn)
        self.add_widget(fila)

        # --- matriz
        marco = con_fondo(BoxLayout(size_hint_y=0.38, padding=dp(6)), LIMA)
        self.scroll_matriz = ScrollView(do_scroll_x=True)
        self.grid = GridLayout(size_hint=(None, None), spacing=dp(5), padding=dp(4))
        self.grid.bind(minimum_width=self.grid.setter("width"),
                       minimum_height=self.grid.setter("height"))
        self.scroll_matriz.add_widget(self.grid)
        marco.add_widget(self.scroll_matriz)
        self.add_widget(marco)

        # --- método y acciones
        self.metodo = Spinner(text="Todos", values=METODOS, option_cls=OpcionMetodo,
                              bold=True, color=BLANCO, background_normal="",
                              background_color=(0, 0, 0, 0),
                              size_hint_y=None, height=dp(46))
        self.add_widget(con_fondo(self.metodo, TURQUESA))

        acciones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        b1 = boton("Calcular", MAGENTA, size_hint_x=0.4)
        b1.bind(on_release=lambda *_: self.calcular())
        acciones.add_widget(b1)
        b3 = boton("Pegar matriz", VERDE, size_hint_x=0.35)
        b3.bind(on_release=lambda *_: self.pegar_matriz())
        acciones.add_widget(b3)
        b2 = boton("Limpiar", CREMA, TEXTO, size_hint_x=0.25)
        b2.bind(on_release=lambda *_: self.limpiar())
        acciones.add_widget(b2)
        self.add_widget(acciones)

        self.add_widget(Label(
            text="Valores: enteros, decimales o fracciones (ej. -2, 0.5, 1/3).\n"
                 "Cramer: matriz aumentada [A | b] de m x (m+1). Inversa: m = n.",
            font_size=sp(12), size_hint_y=None, height=dp(36), color=VERDE))

        # --- resultados
        caja = con_fondo(BoxLayout(size_hint_y=0.62, padding=dp(8)), CREMA)
        self.scroll_res = ScrollView(do_scroll_x=True)
        self.resultado = Label(text="", font_name="RobotoMono-Regular",
                               font_size=sp(13), color=TEXTO,
                               size_hint=(None, None), halign="left", valign="top")
        self.resultado.bind(texture_size=self.resultado.setter("size"))
        self.scroll_res.add_widget(self.resultado)
        caja.add_widget(self.scroll_res)
        self.add_widget(caja)

        self.crear_matriz()

    def crear_matriz(self, valores=None):
        try:
            m, n = int(self.in_m.text), int(self.in_n.text)
        except ValueError:
            return self.mostrar("Ingresa m y n como enteros.")
        if not (1 <= m <= MAX_DIM and 1 <= n <= MAX_DIM):
            return self.mostrar(f"m y n deben estar entre 1 y {MAX_DIM}.")
        self.grid.clear_widgets()
        self.grid.cols = n
        self.celdas = []
        for i in range(m):
            fila = []
            for j in range(n):
                ti = entrada(hint_text=f"a{i + 1}{j + 1}", font_size=sp(16),
                             halign="center", size_hint=(None, None),
                             width=dp(64), height=dp(44), write_tab=False)
                if valores:
                    ti.text = valores[i][j]
                self.grid.add_widget(ti)
                fila.append(ti)
            self.celdas.append(fila)
        aviso = ""
        if n == m + 1:
            aviso = "Matriz aumentada: lista para Cramer."
        elif m != n:
            aviso = "Atención: el determinante requiere m = n."
        self.mostrar(f"Matriz {m}x{n} creada. {aviso}")

    def pegar_matriz(self):
        """Ventana para pegar la matriz como texto (por ejemplo, desde Google Lens)."""
        caja = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        caja.add_widget(Label(
            text="Pega o escribe la matriz: una fila por línea,\n"
                 "valores separados por espacios.\n"
                 "Tip: con Google Lens toma foto a la matriz,\n"
                 "toca \"Texto\" > \"Copiar\" y pégala aquí.",
            color=TEXTO, font_size=sp(13), size_hint_y=None, height=dp(80)))
        texto = TextInput(hint_text="2 1 -1\n-3 -1 2\n-2 1 2", font_size=sp(16),
                          background_normal="", background_active="",
                          background_color=BLANCO, foreground_color=TEXTO,
                          cursor_color=MAGENTA)
        caja.add_widget(texto)
        botones = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        usar = boton("Usar matriz", MAGENTA)
        cancelar = boton("Cancelar", CREMA, TEXTO)
        botones.add_widget(usar)
        botones.add_widget(cancelar)
        caja.add_widget(botones)
        con_fondo(caja, CELESTE)

        popup = Popup(title="Pegar matriz", title_color=BLANCO,
                      separator_color=MAGENTA, background="",
                      background_color=TURQUESA, content=caja,
                      size_hint=(0.95, 0.75))

        def usar_texto(*_):
            try:
                M = matriz_desde_texto(texto.text)
            except ValueError as e:
                self.mostrar(f"Error al leer la matriz: {e}")
                return
            if len(M) > MAX_DIM or len(M[0]) > MAX_DIM:
                self.mostrar(f"Máximo {MAX_DIM}x{MAX_DIM}.")
                return
            popup.dismiss()
            self.in_m.text, self.in_n.text = str(len(M)), str(len(M[0]))
            self.crear_matriz([[_corto(v) for v in fila] for fila in M])

        usar.bind(on_release=usar_texto)
        cancelar.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def leer_matriz(self):
        return [[parse_valor(c.text) for c in fila] for fila in self.celdas]

    def calcular(self):
        try:
            M = self.leer_matriz()
            self.mostrar(resolver(M, self.metodo.text))
        except ValueError as e:
            self.mostrar(f"Error: {e}")
        except RecursionError:
            self.mostrar("Error: matriz demasiado grande para cofactores.")

    def limpiar(self):
        for fila in self.celdas:
            for c in fila:
                c.text = ""
        self.mostrar("")

    def mostrar(self, texto):
        self.resultado.text = texto
        self.scroll_res.scroll_y = 1


def _corto(v):
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


class DeterminantesApp(App):
    title = "Determinantes"

    def build(self):
        return Calculadora()


if __name__ == "__main__":
    DeterminantesApp().run()
