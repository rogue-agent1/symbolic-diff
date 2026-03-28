#!/usr/bin/env python3
"""Symbolic differentiation engine."""
def diff(expr,var):
    if isinstance(expr,(int,float)): return 0
    if isinstance(expr,str): return 1 if expr==var else 0
    op=expr[0]
    if op=="+": return simplify(("+",diff(expr[1],var),diff(expr[2],var)))
    if op=="-": return simplify(("-",diff(expr[1],var),diff(expr[2],var)))
    if op=="*": return simplify(("+",("*",diff(expr[1],var),expr[2]),("*",expr[1],diff(expr[2],var))))
    if op=="/":
        return simplify(("/",("-",("*",diff(expr[1],var),expr[2]),("*",expr[1],diff(expr[2],var))),("*",expr[2],expr[2])))
    if op=="^" and isinstance(expr[2],(int,float)):
        return simplify(("*",("*",expr[2],("^",expr[1],expr[2]-1)),diff(expr[1],var)))
    if op=="sin": return simplify(("*",("cos",expr[1]),diff(expr[1],var)))
    if op=="cos": return simplify(("*",("-",0,("sin",expr[1])),diff(expr[1],var)))
    if op=="exp": return simplify(("*",("exp",expr[1]),diff(expr[1],var)))
    if op=="ln": return simplify(("/",diff(expr[1],var),expr[1]))
    return ("diff",expr,var)
def simplify(expr):
    if not isinstance(expr,tuple): return expr
    if expr[0]=="+" and expr[1]==0: return expr[2]
    if expr[0]=="+" and expr[2]==0: return expr[1]
    if expr[0]=="*" and expr[1]==0: return 0
    if expr[0]=="*" and expr[2]==0: return 0
    if expr[0]=="*" and expr[1]==1: return expr[2]
    if expr[0]=="*" and expr[2]==1: return expr[1]
    if expr[0]=="^" and expr[2]==0: return 1
    if expr[0]=="^" and expr[2]==1: return expr[1]
    if isinstance(expr[1],(int,float)) and len(expr)>2 and isinstance(expr[2],(int,float)):
        if expr[0]=="+": return expr[1]+expr[2]
        if expr[0]=="-": return expr[1]-expr[2]
        if expr[0]=="*": return expr[1]*expr[2]
    return expr
def to_str(expr):
    if isinstance(expr,(int,float)): return str(expr)
    if isinstance(expr,str): return expr
    op=expr[0]
    if op in ("+","-","*","/","^"): return f"({to_str(expr[1])} {op} {to_str(expr[2])})"
    if len(expr)==2: return f"{op}({to_str(expr[1])})"
    return str(expr)
if __name__=="__main__":
    x="x"
    e1=("+",("*",3,("^",x,2)),("*",2,x))
    d1=diff(e1,x);print(f"d/dx[3x^2+2x] = {to_str(d1)}")
    e2=("sin",("*",2,x))
    d2=diff(e2,x);print(f"d/dx[sin(2x)] = {to_str(d2)}")
    e3=("exp",("^",x,2))
    d3=diff(e3,x);print(f"d/dx[exp(x^2)] = {to_str(d3)}")
    print("Symbolic diff OK")
