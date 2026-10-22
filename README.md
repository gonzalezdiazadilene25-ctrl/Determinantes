# Determinantes, Inversa y Sistemas (Android, Python + Kivy)

Resuelve **sistemas de ecuaciones** por **Cramer**, **Gauss**, **Gauss-Jordan** y
**matriz inversa** (indica si hay solución única, infinitas o ninguna), calcula el
**determinante** (cofactores, Gauss, Gauss-Jordan) y la **matriz inversa**
(Gauss-Jordan y adjunta). Muestra el procedimiento paso a paso con fracciones exactas.

- `main.py`: interfaz (Kivy)
- `determinantes.py`: lógica matemática (sin dependencias)
- `buildozer.spec`: configuración para generar el APK

## Uso
1. Escribe m (filas) y n (columnas) y pulsa **Crear**.
2. Llena las casillas (admite `5`, `-2.5`, `1/3`).
3. Elige el método y pulsa **Calcular**.

**Pegar matriz:** toma una foto de la matriz con **Google Lens**, toca *Texto* > *Copiar*,
luego en la app pulsa **Pegar matriz** y pégala (una fila por línea, valores separados por espacios).
La app crea la matriz con el tamaño correcto automáticamente.

* El determinante solo existe si m = n.
* **Sistemas:** ingresa la matriz aumentada [A | b]: los coeficientes y, en la última
  columna, los términos independientes. Gauss y Gauss-Jordan funcionan con cualquier
  número de ecuaciones e incógnitas; Cramer y matriz inversa necesitan tantas
  ecuaciones como incógnitas y det(A) ≠ 0.
* Los botones **+ Fila / - Fila / + Columna / - Columna** agrandan o achican la matriz
  sin borrar lo escrito.
* El **determinante** y la **inversa** requieren una matriz cuadrada (m = n).

## Instalar en el celular

### Opción A: generar el APK con GitHub (no hace falta una PC con Linux)
1. Crea un repositorio en GitHub y sube todos estos archivos (incluida la carpeta `.github`).
2. En la pestaña **Actions** se ejecuta "Construir APK" (tarda unos 20-30 min la primera vez).
3. Al terminar, descarga el artefacto `determinantes-apk` (es un .zip con el `.apk`).
4. Copia el `.apk` al celular, ábrelo y permite "Instalar apps de origen desconocido".

### Opción B: compilar en Linux o WSL
```bash
pip install buildozer cython==0.29.36
sudo apt install -y openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev cmake libffi-dev libssl-dev
buildozer android debug          # el APK queda en bin/
```

### Opción C: probar rápido sin compilar
Instala **Pydroid 3** desde Play Store, instala `kivy` desde su menú Pip,
copia `main.py` y `determinantes.py` en la misma carpeta y ejecuta `main.py`.

### En la PC
```bash
pip install kivy
python main.py
```
