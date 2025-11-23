from AST import *

class SemanticError(Exception):
    pass

class SemanticAnalyzer:

    def __init__(self):
        self.symbols = {}

    def analyze(self, program):
        for stmt in program.statements:
            self.check(stmt)

    def check(self, node):

        if isinstance(node, Decl):
            if node.nombre in self.symbols:
                raise SemanticError(f"Variable '{node.nombre}' already declared.")
            self.symbols[node.nombre] = node.tipo

        elif isinstance(node, Assign):
            if node.nombre not in self.symbols:
                raise SemanticError(f"Variable '{node.nombre}' not declared.")
            tipo_expr = self.eval_expr(node.expr)
            tipo_var = self.symbols[node.nombre]
            if tipo_expr != tipo_var:
                raise SemanticError(f"Type mismatch: {node.nombre} is {tipo_var} but expression is {tipo_expr}")

        elif isinstance(node, If):
            tipo_cond = self.eval_expr(node.cond)
            if tipo_cond != "bool":
                raise SemanticError("Condition in 'if' must be boolean.")
            for s in node.then_block.statements:
                self.check(s)
            if node.else_block:
                for s in node.else_block.statements:
                    self.check(s)

        elif isinstance(node, While):
            tipo_cond = self.eval_expr(node.cond)
            if tipo_cond != "bool":
                raise SemanticError("Condition in 'while' must be boolean.")
            for s in node.body.statements:
                self.check(s)

        elif isinstance(node, Block):
            for s in node.statements:
                self.check(s)

    # -------------------- Expression Checking --------------------

    def eval_expr(self, expr):

        if isinstance(expr, Num):
            return "int"

        if isinstance(expr, BoolLit):
            return "bool"

        if isinstance(expr, Var):
            if expr.name not in self.symbols:
                raise SemanticError(f"Variable '{expr.name}' not declared.")
            return self.symbols[expr.name]

        if isinstance(expr, UnaryOp):
            t = self.eval_expr(expr.expr)
            if expr.op == "!" and t != "bool":
                raise SemanticError("Operator ! expects boolean")
            return t

        if isinstance(expr, BinaryOp):
            left = self.eval_expr(expr.left)
            right = self.eval_expr(expr.right)

            if expr.op in ("+", "-", "*", "/"):
                if left == right == "int":
                    return "int"
                raise SemanticError("Arithmetic operators require int")

            if expr.op in ("<", "<=", ">", ">=", "==", "!="):
                if left != right:
                    raise SemanticError("Comparison requires same type")
                return "bool"

            if expr.op in ("&&", "||"):
                if left == right == "bool":
                    return "bool"
                raise SemanticError("Logical operators require bool")

        raise SemanticError("Invalid expression")