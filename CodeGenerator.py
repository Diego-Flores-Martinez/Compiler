from AST import *

class CodeGenerator:

    def __init__(self):
        self.code = []
        self.temp = 0
        self.label = 0

    def new_temp(self):
        self.temp += 1
        return f"t{self.temp}"

    def new_label(self):
        self.label += 1
        return f"L{self.label}"

    def generate(self, program):
        for stmt in program.statements:
            self.gen_stmt(stmt)
        return self.code

    # -------- Statements --------

    def gen_stmt(self, stmt):

        if isinstance(stmt, Decl):
            return

        if isinstance(stmt, Assign):
            val = self.gen_expr(stmt.expr)
            self.code.append(f"{stmt.nombre} = {val}")
            return

        if isinstance(stmt, If):
            cond = self.gen_expr(stmt.cond)
            else_lbl = self.new_label()
            end_lbl = self.new_label()

            self.code.append(f"if_false {cond} goto {else_lbl}")

            for s in stmt.then_block.statements:
                self.gen_stmt(s)

            self.code.append(f"goto {end_lbl}")

            self.code.append(f"{else_lbl}:")

            if stmt.else_block:
                for s in stmt.else_block.statements:
                    self.gen_stmt(s)

            self.code.append(f"{end_lbl}:")
            return

        if isinstance(stmt, While):
            start = self.new_label()
            end = self.new_label()

            self.code.append(f"{start}:")
            cond = self.gen_expr(stmt.cond)
            self.code.append(f"if_false {cond} goto {end}")

            for s in stmt.body.statements:
                self.gen_stmt(s)

            self.code.append(f"goto {start}")
            self.code.append(f"{end}:")
            return

        if isinstance(stmt, Block):
            for s in stmt.statements:
                self.gen_stmt(s)

    # -------- Expressions --------

    def gen_expr(self, expr):

        if isinstance(expr, Num):
            return str(expr.value)

        if isinstance(expr, BoolLit):
            return "1" if expr.value else "0"

        if isinstance(expr, Var):
            return expr.name

        if isinstance(expr, UnaryOp):
            val = self.gen_expr(expr.expr)
            t = self.new_temp()
            self.code.append(f"{t} = ! {val}")
            return t

        if isinstance(expr, BinaryOp):
            left = self.gen_expr(expr.left)
            right = self.gen_expr(expr.right)
            t = self.new_temp()
            self.code.append(f"{t} = {left} {expr.op} {right}")
            return t

        raise Exception("Unhandled expression")