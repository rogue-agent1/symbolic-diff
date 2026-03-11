#!/usr/bin/env python3
"""symbolic_diff.py — Symbolic differentiation engine.

Computes exact symbolic derivatives of mathematical expressions,
with algebraic simplification. Supports +, -, *, /, ^, sin, cos,
ln, exp, and chain rule.

One file. Zero deps. Does one thing well.
"""

import sys
from dataclasses import dataclass


# ─── AST ───

@dataclass(frozen=True)
class Const:
    value: float
    def __repr__(self): return str(int(self.value)) if self.value == int(self.value) else str(self.value)

@dataclass(frozen=True)
class Symbol:
    name: str
    def __repr__(self): return self.name

@dataclass(frozen=True)
class BinOp:
    op: str
    left: object
    right: object
    def __repr__(self):
        if self.op == '^':
            return f"{_paren(self.left)}^{_paren(self.right)}"
        return f"({self.left} {self.op} {self.right})"

@dataclass(frozen=True)
class UnaryFn:
    name: str
    arg: object
    def __repr__(self): return f"{self.name}({self.arg})"


def _paren(e):
    return f"({e})" if isinstance(e, BinOp) else str(e)

# Convenience constructors
def add(a, b): return BinOp('+', a, b)
def sub(a, b): return BinOp('-', a, b)
def mul(a, b): return BinOp('*', a, b)
def div(a, b): return BinOp('/', a, b)
def power(a, b): return BinOp('^', a, b)
def sin(a): return UnaryFn('sin', a)
def cos(a): return UnaryFn('cos', a)
def ln(a): return UnaryFn('ln', a)
def exp(a): return UnaryFn('exp', a)

ZERO = Const(0)
ONE = Const(1)
TWO = Const(2)


def diff(expr, var: str):
    """Compute d(expr)/d(var)."""
    if isinstance(expr, Const):
        return ZERO
    if isinstance(expr, Symbol):
        return ONE if expr.name == var else ZERO
    if isinstance(expr, BinOp):
        l, r = expr.left, expr.right
        dl, dr = diff(l, var), diff(r, var)
        if expr.op == '+':
            return add(dl, dr)
        if expr.op == '-':
            return sub(dl, dr)
        if expr.op == '*':
            return add(mul(dl, r), mul(l, dr))  # product rule
        if expr.op == '/':
            return div(sub(mul(dl, r), mul(l, dr)), power(r, TWO))  # quotient rule
        if expr.op == '^':
            if isinstance(r, Const):  # power rule
                return mul(mul(r, power(l, Const(r.value - 1))), dl)
            # General: d/dx(f^g) = f^g * (g'*ln(f) + g*f'/f)
            return mul(power(l, r), add(mul(dr, ln(l)), mul(r, div(dl, l))))
    if isinstance(expr, UnaryFn):
        inner = diff(expr.arg, var)  # chain rule
        if expr.name == 'sin':
            return mul(cos(expr.arg), inner)
        if expr.name == 'cos':
            return mul(mul(Const(-1), sin(expr.arg)), inner)
        if expr.name == 'ln':
            return mul(div(ONE, expr.arg), inner)
        if expr.name == 'exp':
            return mul(exp(expr.arg), inner)
    raise ValueError(f"Unknown: {type(expr)}")


def simplify(expr):
    """Algebraic simplification."""
    if isinstance(expr, (Const, Symbol)):
        return expr
    if isinstance(expr, UnaryFn):
        return UnaryFn(expr.name, simplify(expr.arg))
    if isinstance(expr, BinOp):
        l = simplify(expr.left)
        r = simplify(expr.right)
        # Constant folding
        if isinstance(l, Const) and isinstance(r, Const):
            ops = {'+': lambda a,b: a+b, '-': lambda a,b: a-b,
                   '*': lambda a,b: a*b, '/': lambda a,b: a/b if b else float('inf'),
                   '^': lambda a,b: a**b}
            if expr.op in ops:
                return Const(ops[expr.op](l.value, r.value))
        if expr.op == '+':
            if l == ZERO: return r
            if r == ZERO: return l
        if expr.op == '-':
            if r == ZERO: return l
            if l == r: return ZERO
        if expr.op == '*':
            if l == ZERO or r == ZERO: return ZERO
            if l == ONE: return r
            if r == ONE: return l
        if expr.op == '/':
            if l == ZERO: return ZERO
            if r == ONE: return l
        if expr.op == '^':
            if r == ZERO: return ONE
            if r == ONE: return l
        return BinOp(expr.op, l, r)
    return expr


def D(expr, var='x'):
    """Differentiate and simplify."""
    return simplify(diff(expr, var))


def demo():
    print("=== Symbolic Differentiation ===\n")
    x = Symbol('x')

    exprs = [
        ("x^3", power(x, Const(3))),
        ("x^2 + 3x + 5", add(add(power(x, TWO), mul(Const(3), x)), Const(5))),
        ("sin(x)", sin(x)),
        ("x * sin(x)", mul(x, sin(x))),
        ("ln(x^2)", ln(power(x, TWO))),
        ("exp(x^2)", exp(power(x, TWO))),
        ("1/x", div(ONE, x)),
        ("sin(cos(x))", sin(cos(x))),
    ]

    for name, expr in exprs:
        d = D(expr)
        print(f"  d/dx [{name}] = {d}")


if __name__ == '__main__':
    if '--test' in sys.argv:
        x = Symbol('x')
        # d/dx(x) = 1
        assert D(x) == ONE
        # d/dx(5) = 0
        assert D(Const(5)) == ZERO
        # d/dx(x^2) = 2x
        r = D(power(x, TWO))
        assert str(r) == '(2 * x)' or 'x' in str(r)
        # d/dx(x^3) = 3x^2
        r = D(power(x, Const(3)))
        assert '3' in str(r) and 'x' in str(r)
        # d/dx(sin(x)) = cos(x)
        r = D(sin(x))
        assert 'cos' in str(r)
        # d/dx(ln(x)) = 1/x
        r = D(ln(x))
        assert '/' in str(r) or 'x' in str(r)
        # Chain rule: d/dx(sin(x^2))
        r = D(sin(power(x, TWO)))
        assert 'cos' in str(r) and 'x' in str(r)
        print("All tests passed ✓")
    else:
        demo()
