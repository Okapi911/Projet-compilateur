from contextlib import nullcontext
import lark

grammaire = lark.Lark(r"""
%import common.SIGNED_NUMBER
OPBIN : /[+\-*>]/
exp : SIGNED_NUMBER                 -> exp_nombre
| IDENTIFIER                        -> exp_var
| exp OPBIN exp                     -> exp_opbin
| "(" exp ")"                       -> exp_par
com : IDENTIFIER "=" exp ";"        -> assignation
| "if" "(" exp ")" "{" bcom "}"     -> if
| "while" "(" exp ")" "{" bcom "}"  -> while
| "print" "(" exp ")"               -> print
bcom : (com)*
var_list :                          -> vide
| IDENTIFIER ("," IDENTIFIER)*      -> aumoinsune
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/
prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}"
%import common.WS
%ignore WS
""",
start = "prg")

def pp_exp(e):
    if e.data == "exp_nombre" :
        s = e.children[0].value
        return s
    elif e.data == "exp_var" :
        s = e.children[0].value
        return s
    elif e.data == "exp_par" :
        return f" ({pp_exp(e.children[0])})"
    else :
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def vars_exp(e):
    if e.data == "exp_nombre" :
        return set()
    elif e.data == "exp_var" :
        return { e.children[0].value }
    elif e.data == "exp_par" :
        return vars_exp(e.children[0])
    else :
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R

op = {'+' : 'add', '-' : 'sub'}

def asm_exp(e):
    if e.data == "exp_nombre" :
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var" :
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par" :
        return asm_exp(e.children[0])
    else :
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        """

def pp_com(c):
    if c.data == "assignation" :
        return f"{c.children[0].value} = {pp_exp(c.children[1])}"
    elif c.data == "if" :
        x = f"\n\t{pp_bcom(c.children[1])}\n\t"
        return f"if ({pp_exp(c.children[0])})  {{{x}}}"
    elif c.data == "while" :
        x = f"\n\t{pp_bcom(c.children[1])}\n"
        return f"while ({pp_exp(c.children[0])})  {{{x}}}"
    elif c.data == "print" :
        return f"print({pp_exp(c.children[0])})"

def vars_com(c):
    if c.data == "assignation" :
        L = { c.children[0].value }
        R = vars_exp(c.children[1])
        return L | R
    elif c.data == "if" :
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return B | E
    elif c.data == "while" :
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return B | E
    elif c.data == "print" :
        return vars_exp(c.children[0])

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_com(c):
    if c.data == "assignation" :
        E = asm_exp(c.children[1])
        return f"""
        {E}
        mov [{c.children[0].value}], rax
        """
    elif c.data == "if" :
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E}
        cmp rax, 0
        jz fin{n}
        {C}
        fin{n} : nop
        """
    elif c.data == "while" :
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        debut{n} : {E}
        cmp rax, 0
        jz fin{n}
        {C}
        jmp debut{n}
        fin{n} : nop
        """
    elif c.data == "print" :
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """

def pp_bcom(bc, compt = 1):
    return "\n\t".join([pp_com(c) for c in bc.children])

def vars_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | vars_com(c)
    return S

def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])

def pp_prg(p):
    L = pp_vl(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main ( %s ) {\n\t%s\n\treturn(%s);\n}" %(L, C, R)

def vars_prg(p):
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    E = vars_exp(p.children[2])
    return (L | C | E)

def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    E = asm_exp(p.children[2])
    moule = moule.replace("RETURN", E)
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    s = ""
    for i in range(len(p.children[0].children)):
        v = p.children[0].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx +{8*(i+1)}]
        xor rax, rax
        call atoi
        mov[{v}], rax
        """
        s = s+e
    moule = moule.replace("INIT_VARS", s)
    return moule

def pp_vl(vl):
    if vl.data == "aumoinsune" :
        return ", ".join([pp_id(v) for v in vl.children])
    elif vl.data == "vide" :
        return ""

def pp_id(i):
    return i.value

ast = grammaire.parse("""main (x, y) {
    while(x){
        x = x-1;
        y=y+1;
    }
    return (y);
    }""")
print(ast, "\n\n")
print(pp_prg(ast), "\n\n")
print(vars_prg(ast), "\n\n")
asm = asm_prg(ast)
f = open("ouf.asm", "w")
f.write(asm)
f.close()
