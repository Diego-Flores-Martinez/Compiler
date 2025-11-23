from AST import *

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
        raise ParserError(f"Syntax error at token {t}")

    def parse(self):
        stmts = []
        while self.current()[0] != "EOF":
            stmts.append(self.statement())
        return Program(stmts)

    # -------------------- STATEMENTS --------------------

    def statement(self):
        tok = self.current()

        if tok[0] == "PALABRA_RESERVADA" and tok[1] in ("int", "bool"):
            return self.declaration()

        if tok[0] == "PALABRA_RESERVADA" and tok[1] == "if":
            return self.if_statement()

        if tok[0] == "PALABRA_RESERVADA" and tok[1] == "while":
            return self.while_statement()

        if tok[0] == "SIMBOLO" and tok[1] == "{":
            return self.block()

        if tok[0] == "IDENTIFICADOR":
            return self.assignment()

        raise ParserError(f"Unknown statement: {tok}")

    def declaration(self):
        tipo = self.match("PALABRA_RESERVADA")[1]
        nombre = self.match("IDENTIFICADOR")[1]
        self.match("SIMBOLO", ";")
        return Decl(tipo, nombre)

    def assignment(self):
        nombre = self.match("IDENTIFICADOR")[1]
        self.match("SIMBOLO", "=")
        expr = self.expr()
        self.match("SIMBOLO", ";")
        return Assign(nombre, expr)

    def block(self):
        self.match("SIMBOLO", "{")
        stmts = []
        while self.current()[1] != "}":
            stmts.append(self.statement())
        self.match("SIMBOLO", "}")
        return Block(stmts)

    def if_statement(self):
        self.match("PALABRA_RESERVADA", "if")
        self.match("SIMBOLO", "(")
        cond = self.expr()
        self.match("SIMBOLO", ")")
        then_block = self.block()

        else_block = None
        if self.current()[0] == "PALABRA_RESERVADA" and self.current()[1] == "else":
            self.match("PALABRA_RESERVADA", "else")
            else_block = self.block()

        return If(cond, then_block, else_block)

    def while_statement(self):
        self.match("PALABRA_RESERVADA", "while")
        self.match("SIMBOLO", "(")
        cond = self.expr()
        self.match("SIMBOLO", ")")
        body = self.block()
        return While(cond, body)

    # ------------------- EXPRESSIONS -------------------

    def expr(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.current()[1] == "||":
            op = self.match("SIMBOLO")[1]
            right = self.logical_and()
            node = BinaryOp(op, node, right)
        return node

    def logical_and(self):
        node = self.equality()
        while self.current()[1] == "&&":
            op = self.match("SIMBOLO")[1]
            right = self.equality()
            node = BinaryOp(op, node, right)
        return node

    def equality(self):
        node = self.relational()
        while self.current()[1] in ("==", "!="):
            op = self.match("SIMBOLO")[1]
            right = self.relational()
            node = BinaryOp(op, node, right)
        return node

    def relational(self):
        node = self.add()
        while self.current()[1] in ("<", "<=", ">", ">="):
            op = self.match("SIMBOLO")[1]
            right = self.add()
            node = BinaryOp(op, node, right)
        return node

    def add(self):
        node = self.term()
        while self.current()[1] in ("+", "-"):
            op = self.match("SIMBOLO")[1]
            right = self.term()
            node = BinaryOp(op, node, right)
        return node

    def term(self):
        node = self.factor()
        while self.current()[1] in ("*", "/"):
            op = self.match("SIMBOLO")[1]
            right = self.factor()
            node = BinaryOp(op, node, right)
        return node

    def factor(self):
        tok = self.current()

        if tok[1] == "!":
            self.match("SIMBOLO", "!")
            return UnaryOp("!", self.factor())

        if tok[0] == "NUMERO":
            val = int(self.match("NUMERO")[1])
            return Num(val)

        if tok[0] == "PALABRA_RESERVADA" and tok[1] in ("true", "false"):
            val = tok[1] == "true"
            self.match("PALABRA_RESERVADA")
            return BoolLit(val)

        if tok[0] == "IDENTIFICADOR":
            name = self.match("IDENTIFICADOR")[1]
            return Var(name)

        if tok[1] == "(":
            self.match("SIMBOLO", "(")
            node = self.expr()
            self.match("SIMBOLO", ")")
            return node

        raise ParserError(f"Unexpected token in expression: {tok}")