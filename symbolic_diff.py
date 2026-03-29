#!/usr/bin/env python3
"""symbolic_diff - Symbolic differentiation of mathematical expressions."""
import sys

class Expr:
    pass
class Num(Expr):
    def __init__(self, v): self.v = v
    def __repr__(self): return str(self.v)
class Var(Expr):
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
class BinOp(Expr):
    def __init__(self, op, l, r): self.op = op; self.l = l; self.r = r
    def __repr__(self): return f"({self.l} {self.op} {self.r})"
class Func(Expr):
    def __init__(self, name, arg): self.name = name; self.arg = arg
    def __repr__(self): return f"{self.name}({self.arg})"

def diff(expr, var):
    if isinstance(expr, Num):
        return Num(0)
    if isinstance(expr, Var):
        return Num(1) if expr.name == var else Num(0)
    if isinstance(expr, BinOp):
        dl, dr = diff(expr.l, var), diff(expr.r, var)
        if expr.op == "+": return BinOp("+", dl, dr)
        if expr.op == "-": return BinOp("-", dl, dr)
        if expr.op == "*": return BinOp("+", BinOp("*", dl, expr.r), BinOp("*", expr.l, dr))
        if expr.op == "/":
            return BinOp("/", BinOp("-", BinOp("*", dl, expr.r), BinOp("*", expr.l, dr)), BinOp("*", expr.r, expr.r))
        if expr.op == "^":
            # x^n => n*x^(n-1)*dx
            return BinOp("*", BinOp("*", expr.r, BinOp("^", expr.l, BinOp("-", expr.r, Num(1)))), diff(expr.l, var))
    if isinstance(expr, Func):
        inner = diff(expr.arg, var)
        if expr.name == "sin": return BinOp("*", Func("cos", expr.arg), inner)
        if expr.name == "cos": return BinOp("*", BinOp("*", Num(-1), Func("sin", expr.arg)), inner)
        if expr.name == "exp": return BinOp("*", Func("exp", expr.arg), inner)
        if expr.name == "ln": return BinOp("*", BinOp("/", Num(1), expr.arg), inner)
    return Num(0)

def simplify(expr):
    if isinstance(expr, BinOp):
        l, r = simplify(expr.l), simplify(expr.r)
        if expr.op == "+":
            if isinstance(l, Num) and l.v == 0: return r
            if isinstance(r, Num) and r.v == 0: return l
            if isinstance(l, Num) and isinstance(r, Num): return Num(l.v + r.v)
        if expr.op == "*":
            if isinstance(l, Num) and l.v == 0: return Num(0)
            if isinstance(r, Num) and r.v == 0: return Num(0)
            if isinstance(l, Num) and l.v == 1: return r
            if isinstance(r, Num) and r.v == 1: return l
            if isinstance(l, Num) and isinstance(r, Num): return Num(l.v * r.v)
        if expr.op == "-":
            if isinstance(r, Num) and r.v == 0: return l
            if isinstance(l, Num) and isinstance(r, Num): return Num(l.v - r.v)
        return BinOp(expr.op, l, r)
    return expr

def evaluate(expr, env):
    import math as m
    if isinstance(expr, Num): return expr.v
    if isinstance(expr, Var): return env[expr.name]
    if isinstance(expr, BinOp):
        l, r = evaluate(expr.l, env), evaluate(expr.r, env)
        if expr.op == "+": return l + r
        if expr.op == "-": return l - r
        if expr.op == "*": return l * r
        if expr.op == "/": return l / r
        if expr.op == "^": return l ** r
    if isinstance(expr, Func):
        a = evaluate(expr.arg, env)
        return {"sin": m.sin, "cos": m.cos, "exp": m.exp, "ln": m.log}[expr.name](a)

def test():
    import math
    # d/dx(x^2) = 2x
    x2 = BinOp("^", Var("x"), Num(2))
    dx2 = simplify(diff(x2, "x"))
    val = evaluate(dx2, {"x": 3})
    assert abs(val - 6.0) < 0.01
    # d/dx(sin(x)) = cos(x)
    sinx = Func("sin", Var("x"))
    dsinx = simplify(diff(sinx, "x"))
    val2 = evaluate(dsinx, {"x": 0})
    assert abs(val2 - 1.0) < 0.01  # cos(0) = 1
    # d/dx(x + 5) = 1
    xp5 = BinOp("+", Var("x"), Num(5))
    dxp5 = simplify(diff(xp5, "x"))
    assert isinstance(dxp5, Num) and dxp5.v == 1
    print("OK: symbolic_diff")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: symbolic_diff.py test")
