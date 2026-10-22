"""
Lógica matemática para calcular determinantes.
Usa fracciones exactas (Fraction) para evitar errores de redondeo.

Métodos:
  - Cofactores (expansión de Laplace)
  - Eliminación Gaussiana
  - Gauss-Jordan
  - Matriz inversa (Gauss-Jordan y adjunta)
  - Sistemas A·x = b: Cramer, Gauss, Gauss-Jordan y matriz inversa
"""
from fractions import Fraction


# ----------------------------------------------------------------- utilidades
def parse_valor(texto):
    """Convierte '3', '-2.5', '1/3' en Fraction."""
    t = texto.strip().replace(",", ".")
    if t == "":
        raise ValueError("Hay casillas vacías")
    try:
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"Valor no válido: '{texto}'")


def fmt(x):
    """Formatea una fracción: entero, o p/q (aprox. decimal)."""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator} (aprox. {float(x):.6g})"


def fmt_corto(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def matriz_texto(M, barra=None):
    """Matriz alineada; con barra=k se dibuja '|' antes de la columna k."""
    celdas = [[fmt_corto(v) for v in fila] for fila in M]
    ancho = max(len(c) for fila in celdas for c in fila)

    def linea(fila):
        c = [x.rjust(ancho) for x in fila]
        if barra is None:
            return "  ".join(c)
        return "  ".join(c[:barra]) + "  |  " + "  ".join(c[barra:])
    return "\n".join("[ " + linea(fila) + " ]" for fila in celdas)


def copiar(M):
    return [list(map(Fraction, fila)) for fila in M]


def validar_cuadrada(M):
    m = len(M)
    n = len(M[0]) if m else 0
    if m == 0 or m != n:
        raise ValueError(
            f"La matriz es {m}x{n}. El determinante solo existe para "
            "matrices cuadradas (m = n).")


def menor(M, fila, col):
    return [r[:col] + r[col + 1:] for i, r in enumerate(M) if i != fila]


# ------------------------------------------------------------- cofactores
def _det_cof(M):
    n = len(M)
    if n == 1:
        return M[0][0]
    if n == 2:
        return M[0][0] * M[1][1] - M[0][1] * M[1][0]
    total = Fraction(0)
    for j in range(n):
        if M[0][j] != 0:
            total += (-1) ** j * M[0][j] * _det_cof(menor(M, 0, j))
    return total


def det_cofactores(M):
    validar_cuadrada(M)
    M = copiar(M)
    n = len(M)
    pasos = ["MÉTODO DE COFACTORES (expansión por la fila 1)", matriz_texto(M), ""]
    if n == 1:
        pasos.append(f"det = {fmt(M[0][0])}")
        return M[0][0], pasos
    if n == 2:
        d = _det_cof(M)
        pasos.append(f"det = ({fmt_corto(M[0][0])})({fmt_corto(M[1][1])}) - "
                     f"({fmt_corto(M[0][1])})({fmt_corto(M[1][0])}) = {fmt(d)}")
        return d, pasos
    total = Fraction(0)
    for j in range(n):
        signo = (-1) ** j
        sub = menor(M, 0, j)
        dm = _det_cof(sub)
        cof = signo * dm
        total += M[0][j] * cof
        pasos.append(f"a1{j + 1} = {fmt_corto(M[0][j])},  "
                     f"C1{j + 1} = ({'+' if signo > 0 else '-'}1)·M1{j + 1} = "
                     f"{fmt_corto(cof)}")
        pasos.append(f"  Menor M1{j + 1}:\n" + matriz_texto(sub)
                     + f"\n  det(M1{j + 1}) = {fmt_corto(dm)}")
        pasos.append("")
    terminos = " + ".join(f"({fmt_corto(M[0][j])})({fmt_corto((-1) ** j * _det_cof(menor(M, 0, j)))})"
                          for j in range(n))
    pasos.append(f"det = {terminos}")
    pasos.append(f"det = {fmt(total)}")
    return total, pasos


# ------------------------------------------------------------- Gauss
def det_gauss(M):
    validar_cuadrada(M)
    A = copiar(M)
    n = len(A)
    signo = 1
    pasos = ["MÉTODO DE ELIMINACIÓN GAUSSIANA", matriz_texto(A), ""]
    for k in range(n):
        piv = next((i for i in range(k, n) if A[i][k] != 0), None)
        if piv is None:
            pasos.append(f"Columna {k + 1} sin pivote no nulo -> det = 0")
            return Fraction(0), pasos
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            signo = -signo
            pasos.append(f"F{k + 1} <-> F{piv + 1}  (el signo cambia)")
        for i in range(k + 1, n):
            if A[i][k] != 0:
                f = A[i][k] / A[k][k]
                A[i] = [a - f * b for a, b in zip(A[i], A[k])]
                pasos.append(f"F{i + 1} -> F{i + 1} - ({fmt_corto(f)})·F{k + 1}")
        pasos.append(matriz_texto(A))
        pasos.append("")
    d = Fraction(signo)
    for k in range(n):
        d *= A[k][k]
    diag = " · ".join(f"({fmt_corto(A[k][k])})" for k in range(n))
    pasos.append("Matriz triangular superior. det = signo × producto de la diagonal")
    pasos.append(f"det = ({'+' if signo > 0 else '-'}1) · {diag} = {fmt(d)}")
    return d, pasos


# ------------------------------------------------------------- Gauss-Jordan
def det_gauss_jordan(M):
    validar_cuadrada(M)
    A = copiar(M)
    n = len(A)
    factor = Fraction(1)  # det(original) = factor · det(final)
    pasos = ["MÉTODO DE GAUSS-JORDAN", matriz_texto(A), ""]
    for k in range(n):
        piv = next((i for i in range(k, n) if A[i][k] != 0), None)
        if piv is None:
            pasos.append(f"Columna {k + 1} sin pivote no nulo -> det = 0")
            return Fraction(0), pasos
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            factor = -factor
            pasos.append(f"F{k + 1} <-> F{piv + 1}  (factor × -1)")
        p = A[k][k]
        if p != 1:
            A[k] = [v / p for v in A[k]]
            factor *= p
            pasos.append(f"F{k + 1} -> F{k + 1} / ({fmt_corto(p)})  (factor × {fmt_corto(p)})")
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]
                A[i] = [a - f * b for a, b in zip(A[i], A[k])]
                pasos.append(f"F{i + 1} -> F{i + 1} - ({fmt_corto(f)})·F{k + 1}")
        pasos.append(matriz_texto(A))
        pasos.append("")
    pasos.append("Se obtuvo la matriz identidad (det = 1).")
    pasos.append(f"det = producto de pivotes × signo de intercambios = {fmt(factor)}")
    return factor, pasos


# ------------------------------------------------------------- inversa
def inversa_gauss_jordan(M):
    """Reduce [A | I] hasta [I | A^-1]."""
    validar_cuadrada(M)
    n = len(M)
    A = [list(map(Fraction, fila)) + [Fraction(int(i == j)) for j in range(n)]
         for i, fila in enumerate(M)]
    pasos = ["MATRIZ INVERSA POR GAUSS-JORDAN  [A | I] -> [I | A^-1]",
             matriz_texto(A), ""]
    for k in range(n):
        piv = next((i for i in range(k, n) if A[i][k] != 0), None)
        if piv is None:
            pasos.append(f"Columna {k + 1} sin pivote no nulo -> det(A) = 0")
            pasos.append("La matriz NO tiene inversa (es singular).")
            return None, pasos
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            pasos.append(f"F{k + 1} <-> F{piv + 1}")
        p = A[k][k]
        if p != 1:
            A[k] = [v / p for v in A[k]]
            pasos.append(f"F{k + 1} -> F{k + 1} / ({fmt_corto(p)})")
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]
                A[i] = [a - f * b for a, b in zip(A[i], A[k])]
                pasos.append(f"F{i + 1} -> F{i + 1} - ({fmt_corto(f)})·F{k + 1}")
        pasos.append(matriz_texto(A))
        pasos.append("")
    inv = [fila[n:] for fila in A]
    pasos += ["A^-1 =", matriz_texto(inv)]
    return inv, pasos


def inversa_adjunta(M):
    """A^-1 = adj(A) / det(A), con adj(A) = transpuesta de la matriz de cofactores."""
    validar_cuadrada(M)
    A = copiar(M)
    n = len(A)
    pasos = ["MATRIZ INVERSA POR ADJUNTA  A^-1 = adj(A) / det(A)", matriz_texto(A), ""]
    d = _det_cof(A) if n <= 6 else det_gauss(A)[0]
    pasos.append(f"det(A) = {fmt(d)}")
    if d == 0:
        pasos.append("det(A) = 0 -> la matriz NO tiene inversa (es singular).")
        return None, pasos
    if n == 1:
        inv = [[1 / d]]
        pasos += ["", "A^-1 =", matriz_texto(inv)]
        return inv, pasos
    cof = [[(-1) ** (i + j) * (_det_cof(menor(A, i, j)) if n <= 7
                               else det_gauss(menor(A, i, j))[0])
            for j in range(n)] for i in range(n)]
    adj = [[cof[j][i] for j in range(n)] for i in range(n)]
    inv = [[v / d for v in fila] for fila in adj]
    pasos += ["", "Matriz de cofactores  Cij = (-1)^(i+j)·det(Mij):", matriz_texto(cof),
              "", "Adjunta (transpuesta de cofactores):", matriz_texto(adj),
              "", f"A^-1 = adj(A) / ({fmt_corto(d)}) =", matriz_texto(inv)]
    return inv, pasos


def _verificar(M, inv):
    n = len(M)
    ok = all(sum(Fraction(M[i][k]) * inv[k][j] for k in range(n)) == (i == j)
             for i in range(n) for j in range(n))
    return "Verificación: A · A^-1 = I  (correcto)" if ok else "Verificación fallida"


# ------------------------------------------------------------- sistemas A·x = b
def validar_sistema(M):
    """M es la matriz aumentada [A | b]. Devuelve (ecuaciones, incógnitas)."""
    m = len(M)
    n = len(M[0]) if m else 0
    if n < 2:
        raise ValueError("Para un sistema ingresa la matriz aumentada [A | b]: "
                         "los coeficientes y, en la última columna, los "
                         "términos independientes (n >= 2).")
    return m, n - 1


def _plural(k, singular, plural):
    return f"{k} {singular if k == 1 else plural}"


def _termino(coef, nombre, primero):
    """Da '3x2', ' - x1', ' + 1/2t1', según el signo y la posición."""
    v = abs(coef)
    t = ("" if v == 1 else fmt_corto(v)) + nombre
    if primero:
        return ("-" if coef < 0 else "") + t
    return f" {'-' if coef < 0 else '+'} {t}"


def ecuaciones_texto(M):
    k = len(M[0]) - 1
    lineas = []
    for fila in M:
        izq = ""
        for j in range(k):
            if fila[j] != 0:
                izq += _termino(fila[j], f"x{j + 1}", izq == "")
        lineas.append(f"  {izq or '0'} = {fmt_corto(fila[k])}")
    return "\n".join(lineas)


def _encabezado(titulo, M):
    m, k = len(M), len(M[0]) - 1
    return [titulo,
            f"Sistema de {_plural(m, 'ecuación', 'ecuaciones')} con "
            f"{_plural(k, 'incógnita', 'incógnitas')}:",
            ecuaciones_texto(M), "", "Matriz aumentada [A | b]:",
            matriz_texto(M, k), ""]


def _eliminar(A, k, reducida, pasos):
    """Escalona A (aumentada) usando solo las k columnas de coeficientes.
    Con reducida=True llega a la forma escalonada reducida (Gauss-Jordan)."""
    m = len(A)
    fila = 0
    pivotes = []
    for col in range(k):
        if fila >= m:
            break
        piv = next((i for i in range(fila, m) if A[i][col] != 0), None)
        if piv is None:
            continue
        antes = len(pasos)
        if piv != fila:
            A[fila], A[piv] = A[piv], A[fila]
            pasos.append(f"F{fila + 1} <-> F{piv + 1}")
        if reducida and A[fila][col] != 1:
            p = A[fila][col]
            A[fila] = [v / p for v in A[fila]]
            pasos.append(f"F{fila + 1} -> F{fila + 1} / ({fmt_corto(p)})")
        for i in (range(m) if reducida else range(fila + 1, m)):
            if i != fila and A[i][col] != 0:
                f = A[i][col] / A[fila][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[fila])]
                pasos.append(f"F{i + 1} -> F{i + 1} - ({fmt_corto(f)})·F{fila + 1}")
        if len(pasos) > antes:
            pasos += [matriz_texto(A, k), ""]
        pivotes.append(col)
        fila += 1
    return pivotes


def _clasificar(A, k, pivotes, pasos):
    r = len(pivotes)
    for i in range(r, len(A)):
        if A[i][k] != 0:
            pasos.append(f"La fila {i + 1} dice 0 = {fmt_corto(A[i][k])}, "
                         "lo cual es imposible.")
            pasos += ["", "RESULTADO: el sistema NO tiene solución (incompatible)."]
            return "ninguna"
    pasos.append(f"Rango de A = rango de [A | b] = {r};  incógnitas = {k}.")
    return "unica" if r == k else "infinitas"


def _parametrica(R, k, pivotes):
    """Solución general a partir de la forma escalonada reducida R."""
    libres = [j for j in range(k) if j not in pivotes]
    nombres = {j: f"t{i + 1}" for i, j in enumerate(libres)}
    expr = {j: nombres[j] for j in libres}
    for r, c in enumerate(pivotes):
        txt = fmt_corto(R[r][k]) if R[r][k] != 0 else ""
        for j in libres:
            if R[r][j] != 0:
                txt += _termino(-R[r][j], nombres[j], txt == "")
        expr[c] = txt or "0"
    lineas = ["Variables libres: " + ", ".join(f"x{j + 1} = {nombres[j]}" for j in libres)
              + "  (cualquier número real)"]
    lineas += [f"  x{j + 1} = {expr[j]}" for j in range(k)]
    return lineas


def _solucion(x):
    return ["", "SOLUCIÓN:"] + [f"  x{i + 1} = {fmt(v)}" for i, v in enumerate(x)]


def sistema_gauss(M):
    m, k = validar_sistema(M)
    A = copiar(M)
    pasos = _encabezado("SISTEMA POR ELIMINACIÓN GAUSSIANA", A)
    piv = _eliminar(A, k, False, pasos)
    pasos.append("Matriz escalonada obtenida.")
    tipo = _clasificar(A, k, piv, pasos)
    if tipo == "ninguna":
        return tipo, None, pasos
    if tipo == "infinitas":
        R = [fila[:] for fila in A]
        _eliminar(R, k, True, [])
        sol = _parametrica(R, k, piv)
        pasos += ["", "RESULTADO: el sistema tiene INFINITAS soluciones."] + sol
        return tipo, sol, pasos
    pasos += ["", "Sustitución hacia atrás:"]
    x = [Fraction(0)] * k
    for i in range(k - 1, -1, -1):
        suma = sum((A[i][j] * x[j] for j in range(i + 1, k)), Fraction(0))
        x[i] = (A[i][k] - suma) / A[i][i]
        if i == k - 1:
            pasos.append(f"  x{i + 1} = {fmt_corto(A[i][k])} / ({fmt_corto(A[i][i])})"
                         f" = {fmt_corto(x[i])}")
        else:
            pasos.append(f"  x{i + 1} = ({fmt_corto(A[i][k])} - ({fmt_corto(suma)})) / "
                         f"({fmt_corto(A[i][i])}) = {fmt_corto(x[i])}")
    return "unica", x, pasos + _solucion(x)


def sistema_gauss_jordan(M):
    m, k = validar_sistema(M)
    A = copiar(M)
    pasos = _encabezado("SISTEMA POR GAUSS-JORDAN", A)
    piv = _eliminar(A, k, True, pasos)
    pasos.append("Matriz escalonada reducida obtenida.")
    tipo = _clasificar(A, k, piv, pasos)
    if tipo == "ninguna":
        return tipo, None, pasos
    if tipo == "infinitas":
        sol = _parametrica(A, k, piv)
        pasos += ["", "RESULTADO: el sistema tiene INFINITAS soluciones."] + sol
        return tipo, sol, pasos
    x = [A[i][k] for i in range(k)]
    pasos.append("La solución se lee en la última columna.")
    return "unica", x, pasos + _solucion(x)


def _no_aplica(pasos, motivo):
    pasos += [motivo, "Usa Gauss o Gauss-Jordan: indican si hay una solución, "
                      "infinitas o ninguna."]
    return "no_aplica", None, pasos


def cramer(M):
    """Resuelve A·x = b con x_i = det(A_i) / det(A). Requiere A cuadrada."""
    m, k = validar_sistema(M)
    pasos = _encabezado("SISTEMA POR REGLA DE CRAMER", copiar(M))
    if m != k:
        return _no_aplica(pasos, f"Cramer necesita tantas ecuaciones como incógnitas "
                                 f"(aquí hay {m} y {k}).")
    A = [list(map(Fraction, fila[:-1])) for fila in M]
    b = [Fraction(fila[-1]) for fila in M]
    d = _det_cof(A) if m <= 4 else det_gauss(A)[0]
    pasos.append(f"det(A) = {fmt(d)}")
    if d == 0:
        return _no_aplica(pasos, "det(A) = 0: Cramer no se puede aplicar "
                                 "(no hay solución única).")
    sol = []
    for i in range(m):
        Ai = [fila[:i] + [b[r]] + fila[i + 1:] for r, fila in enumerate(A)]
        di = _det_cof(Ai) if m <= 4 else det_gauss(Ai)[0]
        xi = di / d
        sol.append(xi)
        pasos += ["", f"A{i + 1} (columna {i + 1} reemplazada por b):", matriz_texto(Ai),
                  f"det(A{i + 1}) = {fmt_corto(di)}",
                  f"x{i + 1} = det(A{i + 1}) / det(A) = {fmt_corto(di)} / {fmt_corto(d)}"
                  f" = {fmt_corto(xi)}"]
    return "unica", sol, pasos + _solucion(sol)


def sistema_inversa(M):
    m, k = validar_sistema(M)
    pasos = _encabezado("SISTEMA POR MATRIZ INVERSA  x = A^-1 · b", copiar(M))
    if m != k:
        return _no_aplica(pasos, f"A es de {m}x{k} (no cuadrada) y no tiene inversa.")
    A = [list(map(Fraction, fila[:-1])) for fila in M]
    b = [Fraction(fila[-1]) for fila in M]
    inv, p2 = inversa_gauss_jordan(A)
    pasos += p2
    if inv is None:
        return _no_aplica(pasos, "Sin inversa no se puede calcular x = A^-1 · b.")
    pasos += ["", "x = A^-1 · b:"]
    x = []
    for i in range(k):
        xi = sum((inv[i][j] * b[j] for j in range(k)), Fraction(0))
        x.append(xi)
        pasos.append(f"  x{i + 1} = " + " + ".join(
            f"({fmt_corto(inv[i][j])})({fmt_corto(b[j])})" for j in range(k))
            + f" = {fmt_corto(xi)}")
    return "unica", x, pasos + _solucion(x)


METODOS_SIS = {"Sistema Cramer": cramer, "Sistema Gauss": sistema_gauss,
               "Sistema Gauss-Jordan": sistema_gauss_jordan,
               "Sistema Matriz inversa": sistema_inversa}
METODOS_DET = {"Det. Cofactores": det_cofactores, "Det. Gauss": det_gauss,
               "Det. Gauss-Jordan": det_gauss_jordan}
METODOS = (["Sistema todos los métodos"] + list(METODOS_SIS)
           + ["Det. todos los métodos"] + list(METODOS_DET)
           + ["Inversa Gauss-Jordan", "Inversa Adjunta"])
SEP = ["", "=" * 30, ""]


def _resumen_sistema(tipo, sol):
    if tipo == "unica":
        return ", ".join(f"x{i + 1} = {fmt_corto(v)}" for i, v in enumerate(sol))
    return {"infinitas": "infinitas soluciones", "ninguna": "sin solución"}.get(
        tipo, "no aplica")


def resolver(M, metodo):
    """Devuelve el texto completo del resultado para el método elegido."""
    m, n = len(M), len(M[0])
    if metodo in METODOS_SIS:
        return "\n".join(METODOS_SIS[metodo](M)[2])
    if metodo == "Sistema todos los métodos":
        validar_sistema(M)
        salida, resumen = [], []
        for nombre, f in METODOS_SIS.items():
            tipo, sol, pasos = f(M)
            salida += pasos + SEP
            resumen.append(f"{nombre[8:]}: {_resumen_sistema(tipo, sol)}")
        return "\n".join(salida + ["RESUMEN"] + resumen)

    # Determinante o inversa: con matriz aumentada se usa solo la parte A
    nota = []
    if n == m + 1:
        M = [fila[:-1] for fila in M]
        nota = ["(Matriz aumentada detectada: se usa la parte cuadrada A)", ""]

    if metodo.startswith("Inversa"):
        f = inversa_gauss_jordan if "Jordan" in metodo else inversa_adjunta
        inv, pasos = f(M)
        if inv is not None:
            pasos += ["", _verificar(M, inv)]
        return "\n".join(nota + pasos)

    if metodo in METODOS_DET:
        d, pasos = METODOS_DET[metodo](M)
        return "\n".join(nota + pasos + ["", f"RESULTADO: det = {fmt(d)}"])

    # Det. todos los métodos
    validar_cuadrada(M)
    salida, resumen = list(nota), []
    for nombre, f in METODOS_DET.items():
        if nombre == "Det. Cofactores" and len(M) > 7:
            salida += ["Cofactores omitido (n > 7, demasiado lento)"] + SEP
            continue
        d, pasos = f(M)
        resumen.append(f"{nombre[5:]}: {fmt(d)}")
        salida += pasos + SEP
    return "\n".join(salida + ["RESUMEN"] + resumen)


# ------------------------------------------------------------- texto -> matriz
def matriz_desde_texto(texto):
    """
    Convierte texto pegado (por ejemplo, copiado de una foto con Google Lens)
    en una matriz. Una fila por línea; valores separados por espacios, tab,
    ';' o '|'. Si una fila no tiene esos separadores, se separa por comas.
    """
    import re
    filas = []
    for linea in texto.strip().splitlines():
        linea = linea.strip().strip("[]()|").strip()
        if not linea:
            continue
        partes = [p for p in re.split(r"[\s;|]+", linea) if p]
        if len(partes) == 1 and "," in partes[0]:
            partes = [p for p in partes[0].split(",") if p]
        filas.append([parse_valor(p.replace("−", "-")) for p in partes])
    if not filas:
        raise ValueError("No se encontraron números.")
    n = len(filas[0])
    for i, f in enumerate(filas):
        if len(f) != n:
            raise ValueError(f"La fila {i + 1} tiene {len(f)} valores; "
                             f"la fila 1 tiene {n}.")
    return filas
