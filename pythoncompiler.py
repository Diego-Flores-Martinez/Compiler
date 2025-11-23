#        LEXICAL ANALYZER
class LexerError(Exception):
    pass

def lexer(codigo_fuente):
    linea = 1
    columna = 1
    posicion = 0
    n = len(codigo_fuente)
    tokens = []

    palabras_reservadas = {
        "if", "else", "while", "return", "int", "float", "bool", "true", "false"
    }

    simbolos_uno = {';', '(', ')', '{', '}', '+', '-', '*', '/', '<', '>', '=', '!', '&', '|'}
    simbolos_dos = {"<=", ">=", "==", "!=", "&&", "||"}

    def es_letra(c): return c.isalpha() or c == '_'
    def es_digito(c): return c.isdigit()

    while posicion < n:
        c = codigo_fuente[posicion]

        # Espacios
        if c in (' ', '\t'):
            posicion += 1
            columna += 1
            continue

        # Saltos de línea
        if c in ('\n', '\r'):
            posicion += 1
            linea += 1
            columna = 1
            if c == '\r' and posicion < n and codigo_fuente[posicion] == '\n':
                posicion += 1
            continue

        # Identificadores / palabras reservadas
        if es_letra(c):
            inicio = posicion
            while posicion < n and (es_letra(codigo_fuente[posicion]) or es_digito(codigo_fuente[posicion])):
                posicion += 1
            lexema = codigo_fuente[inicio:posicion]
            tipo = "PALABRA_RESERVADA" if lexema in palabras_reservadas else "IDENTIFICADOR"
            tokens.append((tipo, lexema, linea, columna))
            columna += len(lexema)
            continue

        # Números (enteros)
        if es_digito(c):
            inicio = posicion
            while posicion < n and es_digito(codigo_fuente[posicion]):
                posicion += 1
            lexema = codigo_fuente[inicio:posicion]
            tokens.append(("NUMERO", lexema, linea, columna))
            columna += len(lexema)
            continue

        # Cadenas (no las usamos pero las dejamos por si acaso)
        if c == '"':
            inicio = posicion + 1
            posicion = inicio
            lexema_chars = []
            while posicion < n:
                ch = codigo_fuente[posicion]
                if ch == '\\':
                    if posicion + 1 < n:
                        lexema_chars.append(codigo_fuente[posicion:posicion+2])
                        posicion += 2
                        continue
                    else:
                        raise LexerError("Escape incompleto")
                if ch == '"':
                    break
                if ch in ('\n', '\r'):
                    raise LexerError("Salto de línea en cadena")
                lexema_chars.append(ch)
                posicion += 1

            if posicion >= n or codigo_fuente[posicion] != '"':
                raise LexerError("Cadena no terminada")

            lexema = ''.join(lexema_chars)
            posicion += 1
            tokens.append(("CADENA", lexema, linea, columna))
            columna += len(lexema) + 2
            continue

        # Operadores de dos caracteres
        if c in simbolos_uno:
            if posicion + 1 < n:
                dos = c + codigo_fuente[posicion + 1]
                if dos in simbolos_dos:
                    tokens.append(("SIMBOLO", dos, linea, columna))
                    posicion += 2
                    columna += 2
                    continue

            # Operador de un carácter
            tokens.append(("SIMBOLO", c, linea, columna))
            posicion += 1
            columna += 1
            continue

        raise LexerError(f"Carácter no reconocido '{c}' en línea {linea}, columna {columna}")

    tokens.append(("EOF", "", linea, columna))
    return tokens

#            AST
class Program:
    def __init__(self, statements):
        self.statements = statements


class Block:
    def __init__(self, statements):
        self.statements = statements


class Decl:
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre


class Assign:
    def __init__(self, nombre, expr):
        self.nombre = nombre
        self.expr = expr


class If:
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch  # puede ser None


class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class BinaryOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class Num:
    def __init__(self, value):
        self.value = value


class BoolLit:
    def __init__(self, value):
        self.value = value  # True / False


class Var:
    def __init__(self, name):
        self.name = name


# ==========================
#           PARSER
# ==========================

class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def match(self, tipo, lexema=None):
        t = self.current()
        if t[0] == tipo and (lexema is None or t[1] == lexema):
            self.pos += 1
            return t
        raise ParserError(f"Error de sintaxis, se esperaba {tipo} {lexema}, pero se encontró {t}")

    def parse(self):
        stmts = []
        while self.current()[0] != "EOF":
            stmts.append(self.statement())
        return Program(stmts)

    # ---------------------- STATEMENTS ----------------------

    def statement(self):
        tok = self.current()

        # Declaración: int x; / bool ok;
        if tok[0] == "PALABRA_RESERVADA" and tok[1] in ("int", "bool"):
            tipo = tok[1]
            self.match("PALABRA_RESERVADA", tipo)
            nombre = self.match("IDENTIFICADOR")[1]
            self.match("SIMBOLO", ";")
            return Decl(tipo, nombre)

        # if
        if tok[0] == "PALABRA_RESERVADA" and tok[1] == "if":
            return self.parse_if()

        # while
        if tok[0] == "PALABRA_RESERVADA" and tok[1] == "while":
            return self.parse_while()

        # bloque { ... }
        if tok[0] == "SIMBOLO" and tok[1] == "{":
            return self.parse_block()

        # asignación
        if tok[0] == "IDENTIFICADOR":
            nombre = self.match("IDENTIFICADOR")[1]
            self.match("SIMBOLO", "=")
            expr = self.expr()
            self.match("SIMBOLO", ";")
            return Assign(nombre, expr)

        raise ParserError(f"Sentencia no reconocida: {tok}")

    def parse_block(self):
        self.match("SIMBOLO", "{")
        stmts = []
        while not (self.current()[0] == "SIMBOLO" and self.current()[1] == "}"):
            stmts.append(self.statement())
        self.match("SIMBOLO", "}")
        return Block(stmts)

    def parse_if(self):
        self.match("PALABRA_RESERVADA", "if")
        self.match("SIMBOLO", "(")
        cond = self.expr()
        self.match("SIMBOLO", ")")
        then_branch = self.statement()
        else_branch = None
        if self.current()[0] == "PALABRA_RESERVADA" and self.current()[1] == "else":
            self.match("PALABRA_RESERVADA", "else")
            else_branch = self.statement()
        return If(cond, then_branch, else_branch)

    def parse_while(self):
        self.match("PALABRA_RESERVADA", "while")
        self.match("SIMBOLO", "(")
        cond = self.expr()
        self.match("SIMBOLO", ")")
        body = self.statement()
        return While(cond, body)

    # ---------------------- EXPRESSIONS ----------------------

    # expr -> logic_or
    def expr(self):
        return self.logic_or()

    # logic_or -> logic_and ('||' logic_and)*
    def logic_or(self):
        left = self.logic_and()
        while self.current()[0] == "SIMBOLO" and self.current()[1] == "||":
            op = self.match("SIMBOLO", "||")[1]
            right = self.logic_and()
            left = BinaryOp(op, left, right)
        return left

    # logic_and -> equality ('&&' equality)*
    def logic_and(self):
        left = self.equality()
        while self.current()[0] == "SIMBOLO" and self.current()[1] == "&&":
            op = self.match("SIMBOLO", "&&")[1]
            right = self.equality()
            left = BinaryOp(op, left, right)
        return left

    # equality -> relational (('==' | '!=') relational)*
    def equality(self):
        left = self.relational()
        while self.current()[0] == "SIMBOLO" and self.current()[1] in ("==", "!="):
            op = self.match("SIMBOLO")[1]
            right = self.relational()
            left = BinaryOp(op, left, right)
        return left

    # relational -> additive (('<' | '<=' | '>' | '>=') additive)*
    def relational(self):
        left = self.additive()
        while self.current()[0] == "SIMBOLO" and self.current()[1] in ("<", "<=", ">", ">="):
            op = self.match("SIMBOLO")[1]
            right = self.additive()
            left = BinaryOp(op, left, right)
        return left

    # additive -> term (('+' | '-') term)*
    def additive(self):
        left = self.term()
        while self.current()[0] == "SIMBOLO" and self.current()[1] in ("+", "-"):
            op = self.match("SIMBOLO")[1]
            right = self.term()
            left = BinaryOp(op, left, right)
        return left

    # term -> factor (('*' | '/') factor)*
    def term(self):
        left = self.factor()
        while self.current()[0] == "SIMBOLO" and self.current()[1] in ("*", "/"):
            op = self.match("SIMBOLO")[1]
            right = self.factor()
            left = BinaryOp(op, left, right)
        return left

    # factor -> '!' factor | '(' expr ')' | NUM | true/false | IDENT
    def factor(self):
        tok = self.current()

        # not
        if tok[0] == "SIMBOLO" and tok[1] == "!":
            self.match("SIMBOLO", "!")
            expr = self.factor()
            return UnaryOp("!", expr)

        # ( expr )
        if tok[0] == "SIMBOLO" and tok[1] == "(":
            self.match("SIMBOLO", "(")
            e = self.expr()
            self.match("SIMBOLO", ")")
            return e

        # número
        if tok[0] == "NUMERO":
            value = int(tok[1])
            self.match("NUMERO")
            return Num(value)

        # true / false
        if tok[0] == "PALABRA_RESERVADA" and tok[1] in ("true", "false"):
            val = (tok[1] == "true")
            self.match("PALABRA_RESERVADA", tok[1])
            return BoolLit(val)

        # variable
        if tok[0] == "IDENTIFICADOR":
            name = tok[1]
            self.match("IDENTIFICADOR")
            return Var(name)

        raise ParserError(f"Expresión inválida: {tok}")

#       SEMANTIC ANALYZER
class SemanticError(Exception):
    pass


class SemanticAnalyzer:

    def __init__(self):
        self.symbols = {}  # nombre -> tipo ("int", "bool")

    def analyze(self, program):
        for stmt in program.statements:
            self.check_stmt(stmt)

    def check_stmt(self, stmt):
        if isinstance(stmt, Decl):
            if stmt.nombre in self.symbols:
                raise SemanticError(f"Variable '{stmt.nombre}' ya declarada")
            if stmt.tipo not in ("int", "bool"):
                raise SemanticError(f"Tipo inválido para variable '{stmt.nombre}'")
            self.symbols[stmt.nombre] = stmt.tipo

        elif isinstance(stmt, Assign):
            if stmt.nombre not in self.symbols:
                raise SemanticError(f"Variable '{stmt.nombre}' no declarada")
            tipo_var = self.symbols[stmt.nombre]
            tipo_expr = self.eval_expr(stmt.expr)
            if tipo_var != tipo_expr:
                raise SemanticError(
                    f"Tipo incompatible: variable '{stmt.nombre}' es {tipo_var} "
                    f"pero la expresión es {tipo_expr}"
                )

        elif isinstance(stmt, If):
            tipo_cond = self.eval_expr(stmt.cond)
            if tipo_cond != "bool":
                raise SemanticError("La condición de un if debe ser bool")
            self.check_stmt(stmt.then_branch)
            if stmt.else_branch is not None:
                self.check_stmt(stmt.else_branch)

        elif isinstance(stmt, While):
            tipo_cond = self.eval_expr(stmt.cond)
            if tipo_cond != "bool":
                raise SemanticError("La condición de un while debe ser bool")
            self.check_stmt(stmt.body)

        elif isinstance(stmt, Block):
            # Sin nuevos scopes: todo en el mismo diccionario
            for s in stmt.statements:
                self.check_stmt(s)

        else:
            raise SemanticError("Sentencia no válida")

    def eval_expr(self, expr):
        if isinstance(expr, Num):
            return "int"

        if isinstance(expr, BoolLit):
            return "bool"

        if isinstance(expr, Var):
            if expr.name not in self.symbols:
                raise SemanticError(f"Variable '{expr.name}' no declarada")
            return self.symbols[expr.name]

        if isinstance(expr, UnaryOp):
            t = self.eval_expr(expr.expr)
            if expr.op == "!":
                if t != "bool":
                    raise SemanticError("Operador ! requiere expresiones booleanas")
                return "bool"
            raise SemanticError(f"Operador unario no soportado: {expr.op}")

        if isinstance(expr, BinaryOp):
            left = self.eval_expr(expr.left)
            right = self.eval_expr(expr.right)
            op = expr.op

            arith_ops = {"+", "-", "*", "/"}
            rel_ops = {"<", "<=", ">", ">="}
            eq_ops = {"==", "!="}
            logic_ops = {"&&", "||"}

            if op in arith_ops:
                if left != "int" or right != "int":
                    raise SemanticError("Operaciones aritméticas requieren int")
                return "int"

            if op in rel_ops:
                if left != "int" or right != "int":
                    raise SemanticError("Operaciones relacionales requieren int")
                return "bool"

            if op in eq_ops:
                if left != right:
                    raise SemanticError("Operador de igualdad requiere tipos compatibles")
                return "bool"

            if op in logic_ops:
                if left != "bool" or right != "bool":
                    raise SemanticError("Operadores lógicos requieren bool")
                return "bool"

            raise SemanticError(f"Operador binario no soportado: {op}")

        raise SemanticError("Expresión no válida")

#     CODE GENERATOR (TAC)
class CodeGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.code = []
        self.symbols = {}

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, program):
        self.code = []
        for stmt in program.statements:
            self.gen_stmt(stmt)
        return self.code

    # --------- STATEMENTS ---------

    def gen_stmt(self, stmt):
        if isinstance(stmt, Decl):
            # Sólo registramos la variable
            self.symbols[stmt.nombre] = None

        elif isinstance(stmt, Assign):
            temp = self.gen_expr(stmt.expr)
            self.code.append(f"{stmt.nombre} = {temp}")

        elif isinstance(stmt, If):
            self.gen_if(stmt)

        elif isinstance(stmt, While):
            self.gen_while(stmt)

        elif isinstance(stmt, Block):
            for s in stmt.statements:
                self.gen_stmt(s)
        else:
            raise Exception("Sentencia no soportada en codegen")

    def gen_if(self, stmt_if):
        L_else = self.new_label()
        L_end = self.new_label()

        cond_temp = self.gen_expr(stmt_if.cond)
        self.code.append(f"if_false {cond_temp} goto {L_else}")

        # then
        self.gen_stmt(stmt_if.then_branch)
        self.code.append(f"goto {L_end}")

        # else
        self.code.append(f"{L_else}:")
        if stmt_if.else_branch is not None:
            self.gen_stmt(stmt_if.else_branch)

        self.code.append(f"{L_end}:")

    def gen_while(self, stmt_while):
        L_start = self.new_label()
        L_end = self.new_label()

        self.code.append(f"{L_start}:")
        cond_temp = self.gen_expr(stmt_while.cond)
        self.code.append(f"if_false {cond_temp} goto {L_end}")

        self.gen_stmt(stmt_while.body)
        self.code.append(f"goto {L_start}")
        self.code.append(f"{L_end}:")

    # --------- EXPRESSIONS ---------

    def gen_expr(self, expr):
        if isinstance(expr, Num):
            return str(expr.value)

        if isinstance(expr, BoolLit):
            return "1" if expr.value else "0"

        if isinstance(expr, Var):
            return expr.name

        if isinstance(expr, UnaryOp):
            v = self.gen_expr(expr.expr)
            temp = self.new_temp()
            # t = ! v
            self.code.append(f"{temp} = ! {v}")
            return temp

        if isinstance(expr, BinaryOp):
            left = self.gen_expr(expr.left)
            right = self.gen_expr(expr.right)
            temp = self.new_temp()
            self.code.append(f"{temp} = {left} {expr.op} {right}")
            return temp

        raise Exception("Expresión no soportada en codegen")

#       TAC INTERPRETER
class TACInterpreter:
    def __init__(self):
        self.memory = {}  # variables y temporales

    def value_of(self, token):
        # número literal
        if token.isdigit():
            return int(token)
        # true/false por si acaso
        if token == "true":
            return 1
        if token == "false":
            return 0
        # variable / temporal
        return self.memory.get(token, 0)

    def run(self, code):
        # 1. mapa de labels
        labels = {}
        for i, instr in enumerate(code):
            instr = instr.strip()
            if instr.endswith(":"):
                label = instr[:-1]
                labels[label] = i

        pc = 0
        n = len(code)

        while pc < n:
            instr = code[pc].strip()

            if not instr:
                pc += 1
                continue

            # label: se ignora
            if instr.endswith(":"):
                pc += 1
                continue

            # if_false cond goto Lx
            if instr.startswith("if_false"):
                parts = instr.split()
                # if_false cond goto Lx
                _, cond, _, label = parts
                cond_val = self.value_of(cond)
                if cond_val == 0:
                    pc = labels[label]
                    continue
                else:
                    pc += 1
                    continue

            # goto Lx
            if instr.startswith("goto"):
                _, label = instr.split()
                pc = labels[label]
                continue

            # asignaciones
            if "=" in instr:
                left, right = instr.split("=", 1)
                left = left.strip()
                right = right.strip()
                tokens = right.split()

                # x = 5   (una sola cosa)
                if len(tokens) == 1:
                    a = tokens[0]
                    self.memory[left] = self.value_of(a)

                # x = ! a  (unario)
                elif len(tokens) == 2:
                    op, a = tokens
                    a_val = self.value_of(a)
                    if op == "!":
                        self.memory[left] = 0 if a_val != 0 else 1
                    else:
                        raise Exception(f"Operador unario TAC no soportado: {op}")

                # x = a op b
                elif len(tokens) == 3:
                    a, op, b = tokens
                    av = self.value_of(a)
                    bv = self.value_of(b)

                    if op == "+":
                        self.memory[left] = av + bv
                    elif op == "-":
                        self.memory[left] = av - bv
                    elif op == "*":
                        self.memory[left] = av * bv
                    elif op == "/":
                        self.memory[left] = av // bv

                    elif op == "<":
                        self.memory[left] = 1 if av < bv else 0
                    elif op == "<=":
                        self.memory[left] = 1 if av <= bv else 0
                    elif op == ">":
                        self.memory[left] = 1 if av > bv else 0
                    elif op == ">=":
                        self.memory[left] = 1 if av >= bv else 0
                    elif op == "==":
                        self.memory[left] = 1 if av == bv else 0
                    elif op == "!=":
                        self.memory[left] = 1 if av != bv else 0
                    elif op == "&&":
                        self.memory[left] = 1 if (av != 0 and bv != 0) else 0
                    elif op == "||":
                        self.memory[left] = 1 if (av != 0 or bv != 0) else 0
                    else:
                        raise Exception(f"Operador TAC no soportado: {op}")
                else:
                    raise Exception(f"Instrucción TAC inválida: {instr}")

                pc += 1
                continue

            # Si llegó aquí, no reconocimos la instrucción
            raise Exception(f"Instrucción TAC desconocida: {instr}")

        return self.memory

#      PIPELINE COMPLETO
if __name__ == "__main__":
    codigo = """
    int x;
    int y;
    bool ok;

    x = 0;
    y = 5;
    ok = true;

    while (x < y && ok) {
        x = x + 1;
        if (x == 3) {
            ok = false;
        } else {
            ok = true;
        }
    }
    """

    print("===== CÓDIGO FUENTE =====")
    print(codigo)

    # 1. LÉXICO
    tokens = lexer(codigo)

    print("===== TOKENS =====")
    for t in tokens:
        print(t)

    # 2. PARSER
    parser = Parser(tokens)
    ast = parser.parse()

    # 3. SEMÁNTICO
    sem = SemanticAnalyzer()
    try:
        sem.analyze(ast)
        print("\nANÁLISIS SEMÁNTICO COMPLETADO")
        print("Tabla de símbolos:", sem.symbols)
    except Exception as e:
        print("\nERROR SEMÁNTICO:", e)
        raise SystemExit()

    # 4. CODEGEN
    gen = CodeGenerator()
    tac = gen.generate(ast)

    print("\n===== TAC GENERADO =====")
    for i in tac:
        print(i)

    # 5. EJECUTAR TAC
    vm = TACInterpreter()
    mem = vm.run(tac)

    print("\n===== MEMORIA FINAL =====")
    for k, v in mem.items():
        print(f"{k} = {v}")
