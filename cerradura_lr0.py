"""
Problema 2: Función CERRADURA LR(0)
Implementación de la cerradura (closure) para ítems LR(0).
"""

import os
import sys

# ─────────────────────────────────────────────
# 1. Lectura de la gramática desde archivo
# ─────────────────────────────────────────────
# Formato del archivo:
#   # Comentarios (líneas que empiezan con #)
#   # Gramática
#   E' -> E
#   E  -> E + T
#   ...
#   # Items
#   E' -> . E

def leer_archivo_gramatica(ruta):
    """Lee la gramática y los ítems iniciales desde un archivo.
    El archivo tiene dos secciones separadas por '# Items'.
    Retorna (grammar_dict, non_terminals_set, orden_nt, items_iniciales).
    """
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    grammar = {}
    orden_nt = []
    items = []
    seccion = "gramatica"  # empezamos leyendo producciones

    for linea in contenido.splitlines():
        linea_strip = linea.strip()

        # Líneas vacías se ignoran
        if linea_strip == "":
            continue

        # Detectar cambio de sección
        if linea_strip.lower().startswith("# items"):
            seccion = "items"
            continue

        # Ignorar comentarios
        if linea_strip.startswith("#"):
            continue

        if "->" not in linea_strip:
            continue

        izq, der = linea_strip.split("->", 1)
        nt = izq.strip()
        simbolos = der.strip().split()

        if seccion == "gramatica":
            if nt not in grammar:
                grammar[nt] = []
                orden_nt.append(nt)
            grammar[nt].append(simbolos)
        else:
            # Sección de ítems
            if "." not in simbolos:
                print(f"  ⚠ Falta el punto '.' en el ítem: {linea_strip}")
                continue
            dot_pos = simbolos.index(".")
            prod = tuple(s for s in simbolos if s != ".")
            items.append((nt, prod, dot_pos))

    non_terminals = set(grammar.keys())
    return grammar, non_terminals, orden_nt, items


# ─────────────────────────────────────────────
# 2. Representación de un ítem LR(0)
# ─────────────────────────────────────────────
# Un ítem es una tupla: (no_terminal, producción, posición_del_punto)
# Ejemplo: ("E'", ["E"], 0) representa E' -> . E
#          ("E", ["E", "+", "T"], 1) representa E -> E . + T


def formato_item(item):
    """Devuelve la representación legible de un ítem LR(0)."""
    nt, prod, dot = item
    # Insertar el punto en la posición correcta
    simbolos = list(prod)
    simbolos.insert(dot, ".")
    return f"{nt} -> {' '.join(simbolos)}"


def formato_conjunto(items):
    """Imprime un conjunto de ítems de forma legible."""
    for item in items:
        print(f"  - {formato_item(item)}")


# ─────────────────────────────────────────────
# 3. Función CERRADURA LR(0)
# ─────────────────────────────────────────────

def cerradura(items_iniciales, grammar, non_terminals, verbose=True):
    """
    Calcula la cerradura LR(0) de un conjunto de ítems.

    Regla:
      Si A -> α . B β está en el conjunto y B es un no terminal,
      entonces se agregan todos los ítems B -> . γ para cada
      producción B -> γ.

    Se repite hasta que no se agreguen más ítems (punto fijo).
    """
    # Usar una lista para mantener el orden de inserción
    closure = list(items_iniciales)
    # Conjunto auxiliar para verificar existencia en O(1)
    seen = set(items_iniciales)

    if verbose:
        print("APLICANDO CERRADURA...\n")

    paso = 0
    # Índice para recorrer los ítems pendientes de revisar
    i = 0

    while i < len(closure):
        item = closure[i]
        nt, prod, dot = item
        paso += 1

        if verbose:
            print(f"Paso {paso}:")
            print(f"  Se revisa: {formato_item(item)}")

        # ¿Hay un símbolo después del punto?
        if dot < len(prod):
            simbolo = prod[dot]

            if simbolo in non_terminals:
                if verbose:
                    print(f"  Después del punto está el no terminal {simbolo}")

                nuevos = []
                # Agregar todas las producciones de ese no terminal con punto al inicio
                for produccion in grammar[simbolo]:
                    nuevo_item = (simbolo, tuple(produccion), 0)
                    if nuevo_item not in seen:
                        nuevos.append(nuevo_item)
                        seen.add(nuevo_item)
                        closure.append(nuevo_item)

                if nuevos:
                    if verbose:
                        print("  Se agregan:")
                        for ni in nuevos:
                            print(f"    - {formato_item(ni)}")
                else:
                    if verbose:
                        print("  No se agrega nada nuevo porque esos ítems ya existen.")
            else:
                if verbose:
                    print(f'  Después del punto está "{simbolo}"')
                    print("  No se agrega nada porque no es no terminal.")
        else:
            if verbose:
                print("  El punto está al final del ítem (ítem de reducción).")
                print("  No se agrega nada.")

        if verbose:
            print()

        i += 1

    return closure


# ─────────────────────────────────────────────
# 4. Función para imprimir la gramática
# ─────────────────────────────────────────────

def imprimir_gramatica(grammar):
    """Imprime la gramática numerada."""
    print("GRAMÁTICA:")
    num = 1
    for nt in grammar:
        for prod in grammar[nt]:
            print(f"  {num}. {nt} -> {' '.join(prod)}")
            num += 1
    print()


# ─────────────────────────────────────────────
# 5. Función principal de demostración
# ─────────────────────────────────────────────

def ejecutar_cerradura(grammar, non_terminals, items_iniciales, titulo=""):
    """Ejecuta y muestra la cerradura de un conjunto de ítems."""
    separador = "=" * 55

    if titulo:
        print(separador)
        print(f"  {titulo}")
        print(separador)
        print()

    imprimir_gramatica(grammar)

    print("CONJUNTO INICIAL I:")
    formato_conjunto(items_iniciales)
    print()

    resultado = cerradura(items_iniciales, grammar, non_terminals, verbose=True)

    print("CERRADURA FINAL:")
    formato_conjunto(resultado)
    print()

    return resultado


# ─────────────────────────────────────────────
# 6. Ejecuciones de prueba
# ─────────────────────────────────────────────

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Uso: python cerradura_lr0.py <archivo_gramatica.txt>")
        print("  El archivo debe contener la gramática y los ítems iniciales.")
        sys.exit(1)

    ruta = sys.argv[1]

    if not os.path.isfile(ruta):
        print(f"Error: No se encontró el archivo '{ruta}'")
        sys.exit(1)

    grammar, non_terminals, orden_nt, items_iniciales = leer_archivo_gramatica(ruta)

    if not grammar:
        print("No se encontró ninguna gramática en el archivo.")
        sys.exit(1)

    if not items_iniciales:
        print("No se encontraron ítems iniciales en el archivo.")
        sys.exit(1)

    nombre = os.path.basename(ruta)
    titulo = f"CERRADURA LR(0) — {nombre}"
    ejecutar_cerradura(grammar, non_terminals, items_iniciales, titulo=titulo)

    print("¡Hasta luego!")
