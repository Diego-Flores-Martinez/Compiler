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
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block

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
        self.value = value

class Var:
    def __init__(self, name):
        self.name = name