"""
Lógica matemática para calcular determinantes.
Usa fracciones exactas (Fraction) para evitar errores de redondeo.

Métodos:
  - Cofactores (expansión de Laplace)
  - Eliminación Gaussiana
  - Gauss-Jordan
  - Regla de Cramer (para sistemas A·x = b)
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


def matriz_texto(M):
    celdas = [[fmt_corto(v) for v in fila] for fila in M]
    ancho = max(len(c) for fila in celdas for c in fila)
    return "\n".join("[ " + "  ".join(c.rjust(ancho) for c in fila) + " ]"
                     for fila in celdas)


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


# ------------------------------------------------------------- Cramer
def cramer(M):
    """
    M es la matriz aumentada [A | b] de tamaño n x (n+1).
    Resuelve A·x = b con x_i = det(A_i) / det(A).
    """
    m = len(M)
    n = len(M[0]) if m else 0
    if n != m + 1:
        raise ValueError(
            f"Cramer necesita la matriz aumentada [A | b] de tamaño "
            f"m x (m+1). Ingresaste {m}x{n}; usa {m}x{m + 1}.")
    A = [list(map(Fraction, fila[:-1])) for fila in M]
    b = [Fraction(fila[-1]) for fila in M]
    pasos = ["REGLA DE CRAMER", "Matriz de coeficientes A:", matriz_texto(A),
             "Vector b: [" + ", ".join(fmt_corto(v) for v in b) + "]", ""]
    d = _det_cof(A) if m <= 4 else det_gauss(A)[0]
    pasos.append(f"det(A) = {fmt(d)}")
    if d == 0:
        pasos.append("det(A) = 0 -> el sistema no tiene solución única; "
                     "Cramer no se puede aplicar.")
        return d, None, pasos
    sol = []
    for i in range(m):
        Ai = [fila[:i] + [b[r]] + fila[i + 1:] for r, fila in enumerate(A)]
        di = _det_cof(Ai) if m <= 4 else det_gauss(Ai)[0]
        xi = di / d
        sol.append(xi)
        pasos.append("")
        pasos.append(f"A{i + 1} (columna {i + 1} reemplazada por b):")
        pasos.append(matriz_texto(Ai))
        pasos.append(f"det(A{i + 1}) = {fmt_corto(di)}")
        pasos.append(f"x{i + 1} = {fmt_corto(di)} / {fmt_corto(d)} = {fmt(xi)}")
    pasos.append("")
    pasos.append("SOLUCIÓN:")
    for i, v in enumerate(sol):
        pasos.append(f"  x{i + 1} = {fmt(v)}")
    return d, sol, pasos


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


METODOS = ["Cofactores", "Gauss", "Gauss-Jordan", "Cramer",
           "Inversa (Gauss-Jordan)", "Inversa (Adjunta)", "Todos"]


def resolver(M, metodo):
    """Devuelve el texto completo del resultado para el método elegido."""
    m, n = len(M), len(M[0])
    if metodo == "Cramer":
        return "\n".join(cramer(M)[2])

    if metodo.startswith("Inversa"):
        f = inversa_gauss_jordan if "Jordan" in metodo else inversa_adjunta
        inv, pasos = f(M)
        if inv is not None:
            pasos += ["", _verificar(M, inv)]
        return "\n".join(pasos)

    # Si el usuario ingresó una matriz aumentada, se usa solo la parte A
    nota = []
    if n == m + 1 and metodo != "Todos":
        M = [fila[:-1] for fila in M]
        nota = ["(Matriz aumentada detectada: se usa la parte cuadrada A)", ""]

    funcs = {"Cofactores": det_cofactores, "Gauss": det_gauss,
             "Gauss-Jordan": det_gauss_jordan}
    if metodo in funcs:
        d, pasos = funcs[metodo](M)
        return "\n".join(nota + pasos + ["", f"RESULTADO: det = {fmt(d)}"])

    # Todos
    salida = []
    if n == m + 1:
        salida += cramer(M)[2] + ["", "=" * 30, ""]
        M = [fila[:-1] for fila in M]
    validar_cuadrada(M)
    resumen = []
    for nombre, f in funcs.items():
        if nombre == "Cofactores" and len(M) > 7:
            salida += ["Cofactores omitido (n > 7, demasiado lento)", "", "=" * 30, ""]
            continue
        d, pasos = f(M)
        resumen.append(f"{nombre}: {fmt(d)}")
        salida += pasos + ["", "=" * 30, ""]
    salida += ["RESUMEN"] + resumen
    return "\n".join(salida)
