from http.client import FORBIDDEN
from logging.handlers import SYSLOG_UDP_PORT
import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                                             -> exp_nombre
| IDENTIFIER                                                    -> exp_var
| PIDENTIFIER                                                   -> exp_pvar
| exp OPBIN exp                                                 -> exp_opbin
| "(" exp ")"                                                   -> exp_par
| IDENTIFIER "(" var_list ")"                                   -> exp_appel
| NULL                                                          -> exp_null

com : IDENTIFIER "=" exp ";"                                    -> assignation
| PIDENTIFIER "=" exp ";"                                       -> p_assignation
| "if" "(" exp ")" "{" bcom "}"                                 -> if
| "if" "(" exp ")" "{" bcom "}" "else" "{" bcom "}"             -> if_else
| "while" "(" exp ")" "{" bcom "}"                              -> while
| "print" "(" exp ")" ";"                                       -> print

bcom : (com)*

bcls : (cls)*

prg : bcls "main" "(" var_list ")" "{" bcom  "return" exp ";" "}"

cls : "class" IDENTIFIER "{" IDENTIFIER "(" var_list ")" "{" bcom "}" "}"                   -> declaration_class

var_list :                                                      -> vide
| IDENTIFIER ("," IDENTIFIER)*                                  -> aumoinsune

PIDENTIFIER : IDENTIFIER "." IDENTIFIER

name : IDENTIFIER

IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/

NULL : "NULL"

OPBIN : /[+\-*>]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", 
start="prg")

tab = "    "
g = "{"
d = "}"

op = {'+' : 'add', '-' : 'sub', '*' : 'imul'}

def asm_exp(e):
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "exp_opbin":
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        """
    elif e.data == "exp_null":
        return f"""
    mov rax, NULL
    """
    elif e.data == "exp_appel":
        s=""
        for i in range(len(e.children[1].children)):
            temp=f"""
    mov rax, [{e.children[1].children[len(e.children[1].children)-1-i].value}]
    push rax 
            """
            s=s+temp
        return f"""
    {s}
    call {e.children[0]}
    add rsp, 8*{len(e.children[1].children)}
                """
    elif e.data == "exp_pvar":
        temp = e.children[0].value.split(".")
        return f"""
    call get_{temp[1]}
    mov [{e.children[0].value}], rax
    mov rax, [{e.children[0].value}]"""

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_class(cls):
    C = asm_bcom(cls.children[3])
    s = ""
    for i in range(len(cls.children[2].children)):
        v = cls.children[2].children[i].value
        e = f"""
    mov rax, [rbp+{8+8*(i+1)}]
    mov [{v}], rax
        """
        s = s + e
    t = ""
    temp = cls.children[3].children[1].children[0].split(".")
    for i in range(len(cls.children[2].children)):
        w = f"""
get_{cls.children[2].children[i].value}:
    mov rax, [{temp[0]}.{cls.children[2].children[i].value}]
    ret
    """
        t=t+w
    return f"""
{cls.children[0].value}:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*{len(cls.children[2].children)}
    
    push rdi
    push rsi
    
    {s}
    {C}
    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    {t}
    """

def asm_bclass(bcls):
    return "\n".join([asm_class(cls) for cls in bcls.children])

def asm_com(c):
    if c.data == "assignation":
        E1 = asm_exp(c.children[1])
        return f"""
        {E1}
        mov [{c.children[0].value}], rax 
        """
        
    elif c.data == "p_assignation":
        E1 = asm_exp(c.children[1])
        return f"""
            {E1}
            mov [{c.children[0].value}], rax 
            """
    elif c.data == "if":
        E1 = asm_exp(c.children[0])
        C1 = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E1}
        cmp rax, 0
        jz fin{n}
        {C1}
        fin{n} : nop
        """
    elif c.data == "while":
        E1 = asm_exp(c.children[0])
        C1 = asm_bcom(c.children[1])
        n = next()
        return f"""
        debut{n} : {E1}
        cmp rax, 0
        jz fin{n}
        {C1}
        jmp debut{n}
        fin{n} : nop
        """
    elif c.data == "print":
        E1 = asm_exp(c.children[0])
        return f"""
        {E1}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """

def asm_bcom(bc):
    return "\n".join([asm_com(c) for c in bc.children])

def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    
    C = asm_bcom(p.children[2])
    moule = moule.replace("BODY", C)
    
    E = asm_exp(p.children[3])
    moule = moule.replace("RETURN", E)

    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)

    s = ""
    for i in range(len(p.children[1].children)):
        v = p.children[1].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + {8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{v}], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)
    cls=f"""{asm_bclass(p.children[0])}"""
    moule = moule.replace("CLASS", cls)
    return moule

def vars_exp(e):
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_pvar":
        return {e.children[0].value}
    elif e.data == "exp_appel":
        L = set([t.value for t in e.children[1].children])
        return L
    elif e.data == "exp_null":
        pass
    else:
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R

def vars_com(c):
    if c.data == "assignation":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
    if c.data == "p_assignation":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
    elif c.data == "if":
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return E | B
    elif c.data == "while":
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return E | B
    elif c.data == "print":
        return vars_exp(c.children[0])

def vars_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | vars_com(c)
    return S

def vars_class(cls):
    L = set([v.value for v in cls.children[2].children])
    M  = vars_bcom(cls.children[3])
    return L | M

def vars_bclass(bcls):
    S = set()
    for cls in bcls.children:
        S = S | vars_class(cls)
    return S

def vars_prg(p):
    CLA = vars_bclass(p.children[0])
    L = set([t.value for t in p.children[1].children])
    C = vars_bcom(p.children[2])
    E = vars_exp(p.children[3])
    return L | C | E | CLA

def pp_exp(e, ntab = 0):
    tabulation = ntab * tab
    if e.data == "exp_nombre":
        return tabulation + e.children[0].value
    elif e.data == "exp_var":
        return tabulation + e.children[0].value
    elif e.data == "exp_pvar":
        return tabulation + e.children[0].value
    elif e.data == "exp_par":
        return f"{tabulation}({pp_exp(e.children[0])})"
    elif e.data == "exp_null":
        return "NULL"
    elif e.data == "exp_appel":
        return f"{e.children[0].value}({pp_varlist(e.children[1])})"
    else:
        return f"{tabulation}{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def pp_com(c, ntab = 0):
    tabulation = ntab * tab
    if c.data == "assignation":
        return f"{tabulation}{c.children[0].value} = {pp_exp(c.children[1])};"

    elif c.data == "if":
        x = f"\n{pp_bcom(c.children[1], ntab + 1)}"
        return f"{tabulation}if ({pp_exp(c.children[0])}) {g}{x} \n{tabulation}{d} "

    elif c.data =="if_else":
        x = f"\n{pp_bcom(c.children[1], ntab + 1)}"
        y = f"\n{pp_bcom(c.children[2], ntab + 1)}"
        return f"{tabulation}if ({pp_exp(c.children[0])}) {g}{x} \n{tabulation}{d} else {g}{y}\n{tabulation}{d}"

    elif c.data == "while":
        x = f"\n{pp_bcom(c.children[1], ntab + 1)}"
        return f"{tabulation}while ({pp_exp(c.children[0])}) {g}{x} \n{tabulation}{d} "
        
    elif c.data == "print":
        return f"{tabulation}print({pp_exp(c.children[0])});"
    
    elif c.data == "p_assignation":

        return f"{tabulation}{c.children[0].value} = {pp_exp(c.children[1])};"

def pp_bcom(bc, ntab = 0):
    return "\n".join([pp_com(c, ntab) for c in bc.children])

def pp_varlist(l):
    return ", ".join([var.value for var in l.children])

def pp_cls(c, ntab = 0):
    if c.children[0] != c.children[1]:
        raise Exception
    return f"class {c.children[0]} {g} \n{tab}{c.children[1]}({pp_varlist(c.children[2])}) {g} \n{pp_bcom(c.children[3], ntab + 2)} \n{tab}{d} \n{d}"

def pp_bcls(bcls, ntab = 0):
    return "\n\n".join([pp_cls(c, ntab) for c in bcls.children])

def pp_prg(p):
    g = "{"
    d = "}"
    return f"{pp_bcls(p.children[0])} \n\nmain ({pp_varlist(p.children[1])}) {g} \n{pp_bcom(p.children[2], 1)} \n    return {pp_exp(p.children[3])}; \n{d}"

#ast = grammaire.parse("a = a + 1;")
#ast = grammaire.parse("main (x, y) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} else {a = y;} return a;}")
#ast = grammaire.parse("main (x, y, z) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} return a;}")
#ast = grammaire.parse("main (x, y) { x = x + y; return x;} ")

ast = grammaire.parse("""
class Point{
    Point(x,y){
        tree.x = x;
        tree.y = y;
    }
}
main(a,b){
    pt = Point(a,b);
    distanceAOrigine = pt.x*pt.x+pt.y*pt.y;
    return distanceAOrigine;
}
""")

"""print(ast)
print(pp_prg(ast))"""


"""
print(asm_class(ast))"""

asm = asm_prg(ast)

f = open("ouf.asm", "w")
f.write(asm)
f.close()
