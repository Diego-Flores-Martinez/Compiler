from AST import *

class LexerError(Exception):
    pass

def lexer(codigo_fuente):
    linea = 1
    columna = 1
    posicion = 0
    n = len(codigo_fuente)

    tokens = []
    palabras_reservadas = {"if", "else", "while", "int", "bool", "true", "false"}
    simbolos_multiples = {"==", "!=", "<=", ">=", "&&", "||"}
    simbolos_simples = {';', '(', ')', '{', '}', '=', '+', '-', '*', '/', '<', '>'}

    def es_letra(c): return c.isalpha() or c == '_'
    def es_digito(c): return c.isdigit()

    while posicion < n:
        c = codigo_fuente[posicion]

        if c in (' ', '\t'):
            posicion += 1
            columna += 1
            continue

        if c in ('\n', '\r'):
            posicion += 1
            linea += 1
            columna = 1
            if c == '\r' and posicion < n and codigo_fuente[posicion] == '\n':
                posicion += 1
            continue

        # Tokens múltiples primero
        match = None
        for sym in simbolos_multiples:
            if codigo_fuente.startswith(sym, posicion):
                tokens.append(("SIMBOLO", sym, linea, columna))
                posicion += len(sym)
                columna += len(sym)
                match = True
                break
        if match:
            continue

        if es_letra(c):
            inicio = posicion
            while posicion < n and (es_letra(codigo_fuente[posicion]) or es_digito(codigo_fuente[posicion])):
                posicion += 1
            lexema = codigo_fuente[inicio:posicion]
            tipo = "PALABRA_RESERVADA" if lexema in palabras_reservadas else "IDENTIFICADOR"
            tokens.append((tipo, lexema, linea, columna))
            columna += len(lexema)
            continue

        if es_digito(c):
            inicio = posicion
            while posicion < n and es_digito(codigo_fuente[posicion]):
                posicion += 1
            lexema = codigo_fuente[inicio:posicion]
            tokens.append(("NUMERO", lexema, linea, columna))
            columna += len(lexema)
            continue

        if c in simbolos_simples:
            tokens.append(("SIMBOLO", c, linea, columna))
            posicion += 1
            columna += 1
            continue

        raise LexerError(f"Carácter no reconocido '{c}' en línea {linea}, columna {columna}")

    tokens.append(("EOF", "", linea, columna))
    return tokens

