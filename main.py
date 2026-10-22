"""
Calculadora de Determinantes y Matriz Inversa - App Android con Kivy.
"""
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from determinantes import METODOS, parse_valor, resolver

MAX_DIM = 10

Window.softinput_mode = "below_target"


class Calculadora(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(8), spacing=dp(6), **kw)
        self.celdas = []

        self.add_widget(Label(text="[b]Determinantes e Inversa[/b]",
                              markup=True, font_size=sp(20),
                              size_hint_y=None, height=dp(40)))

        # --- dimensiones
        fila = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        fila.add_widget(Label(text="Filas m:", size_hint_x=0.22))
        self.in_m = TextInput(text="3", multiline=False, input_filter="int",
                              font_size=sp(18), size_hint_x=0.18)
        fila.add_widget(self.in_m)
        fila.add_widget(Label(text="Columnas n:", size_hint_x=0.28))
        self.in_n = TextInput(text="3", multiline=False, input_filter="int",
                              font_size=sp(18), size_hint_x=0.18)
        fila.add_widget(self.in_n)
        btn = Button(text="Crear", size_hint_x=0.24)
        btn.bind(on_release=lambda *_: self.crear_matriz())
        fila.add_widget(btn)
        self.add_widget(fila)

        # --- matriz
        self.scroll_matriz = ScrollView(size_hint_y=0.38, do_scroll_x=True)
        self.grid = GridLayout(size_hint=(None, None), spacing=dp(4), padding=dp(4))
        self.grid.bind(minimum_width=self.grid.setter("width"),
                       minimum_height=self.grid.setter("height"))
        self.scroll_matriz.add_widget(self.grid)
        self.add_widget(self.scroll_matriz)

        # --- método y acciones
        self.metodo = Spinner(text="Todos", values=METODOS,
                              size_hint_y=None, height=dp(46))
        self.add_widget(self.metodo)
        acciones = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        b1 = Button(text="Calcular", background_color=(0.2, 0.6, 1, 1),
                    size_hint_x=0.6)
        b1.bind(on_release=lambda *_: self.calcular())
        acciones.add_widget(b1)
        b2 = Button(text="Limpiar", size_hint_x=0.4)
        b2.bind(on_release=lambda *_: self.limpiar())
        acciones.add_widget(b2)
        self.add_widget(acciones)

        self.add_widget(Label(
            text="Valores: enteros, decimales o fracciones (ej. -2, 0.5, 1/3).\n"
                 "Cramer: matriz aumentada [A | b] de m x (m+1). Inversa: m = n.",
            font_size=sp(12), size_hint_y=None, height=dp(36),
            color=(0.7, 0.7, 0.7, 1)))

        # --- resultados
        self.scroll_res = ScrollView(size_hint_y=0.62, do_scroll_x=True)
        self.resultado = Label(text="", font_name="RobotoMono-Regular",
                               font_size=sp(13), size_hint=(None, None),
                               halign="left", valign="top")
        self.resultado.bind(texture_size=self.resultado.setter("size"))
        self.scroll_res.add_widget(self.resultado)
        self.add_widget(self.scroll_res)

        self.crear_matriz()

    def crear_matriz(self):
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
                ti = TextInput(hint_text=f"a{i + 1}{j + 1}", multiline=False,
                               font_size=sp(16), halign="center",
                               size_hint=(None, None), width=dp(64), height=dp(44),
                               write_tab=False)
                self.grid.add_widget(ti)
                fila.append(ti)
            self.celdas.append(fila)
        aviso = ""
        if n == m + 1:
            aviso = "Matriz aumentada: lista para Cramer."
        elif m != n:
            aviso = "Atención: el determinante requiere m = n."
        self.mostrar(f"Matriz {m}x{n} creada. {aviso}")

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


class DeterminantesApp(App):
    title = "Determinantes"

    def build(self):
        return Calculadora()


if __name__ == "__main__":
    DeterminantesApp().run()
