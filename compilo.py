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
| PIDENTIFIER "=" exp ";"                                        -> p_assignation
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

PIDENTIFIER : "this."/[a-zA-Z][a-zA-Z0-9]*/

IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/

NULL : "NULL"

OPBIN : /[+\-*>]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", 
start="cls")

tab = "    "
g = "{"
d = "}"

op = {'+' : 'add', '-' : 'sub'}

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

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_class(cls):




    return f"""{cls.children[0]} :
    push rbp
    mov rsp, rbp
    {asm_bcom(cls.children[3])}
    """

def asm_com(c):
    if c.data == "assignation":
        if c.children[1].data == "exp_nombre" or c.children[1].data == "exp_var":
            E1 = asm_exp(c.children[1])
            return f"""
            {E1}
            mov [{c.children[0].value}], rax 
            """
        elif c.children[1].data == "exp_appel":
            pass
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
        mov rdi, [rbx + {8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{v}], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)
    return moule

def vars_exp(e):
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    else:
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R

def vars_com(c):
    if c.data == "assignation":
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

def vars_prg(p):
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    E = vars_exp(p.children[2])
    return L | C | E

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
class A{
    A(a,b,c){
        this.c = this.a + 37 + a + b+ c;
    }
}
""")

print(ast)
print(pp_cls(ast))


"""
print(asm_class(ast))"""

"""asm = asm_prg(ast)

f = open("ouf.asm", "w")
f.write(asm)
f.close()"""
