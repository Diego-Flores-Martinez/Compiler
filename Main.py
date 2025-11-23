
from Lexer import lexer
from Parser import Parser
from Semantic import SemanticAnalyzer
from CodeGenerator import CodeGenerator

import os

def ejecutar_programa(nombre_archivo):
    print("\n" + "="*60)
    print(f"RUNNING: {nombre_archivo}")
    print("="*60)

    # Ruta relativa al archivo dentro del repositorio
    ruta = os.path.join(os.path.dirname(__file__), nombre_archivo)

    if not os.path.exists(ruta):
        print(f"ERROR: No se encontró el archivo {nombre_archivo}")
        print("Asegúrate de subirlo al repositorio junto a Main.py.")
        return

    with open(ruta, "r", encoding="utf-8") as f:
        codigo = f.read()

    # === LÉXICO ===
    try:
        tokens = lexer(codigo) 
        print("\n===== TOKENS =====")
        for t in tokens:
            print(t)
    except Exception as e:
        print("\nLEXER ERROR:", e)
        return

    # === PARSER ===
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("\nAST successfully generated.")
    except Exception as e:
        print("\nPARSER ERROR:", e)
        return

    # === SEMÁNTICO ===
    try:
        sem = SemanticAnalyzer()
        sem.analyze(ast)
        print("\nSemantic OK. Symbols:", sem.symbols)
    except Exception as e:
        print("\nSEMANTIC ERROR:", e)
        return

    # === GENERACIÓN DE CÓDIGO ===
    try:
        gen = CodeGenerator()
        tac = gen.generate(ast)

        print("\n===== TAC =====")
        for line in tac:
            print(line)

    except Exception as e:
        print("\nCODEGEN ERROR:", e)
        return


if __name__ == "__main__":
    # Programa válido
    ejecutar_programa("programa.txt")

    # Programa con error semántico
    ejecutar_programa("programa_error.txt")
