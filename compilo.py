from tokenize import Token
import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                                             -> exp_nombre
| IDENTIFIER                                                    -> exp_var
| exp OPBIN exp                                                 -> exp_opbin
| "(" exp ")"                                                   -> exp_par
| name "(" args_list ")"                                        -> call

com : IDENTIFIER "=" exp ";"                                    -> assignation
| "if" "(" exp ")" "{" bcom "}"                                 -> if
| "if" "(" exp ")" "{" bcom "}" "else" "{" bcom "}"             -> if_else
| "while" "(" exp ")" "{" bcom "}"                              -> while
| "print" "(" exp ")" ";"                                       -> print

args_list :                                                     -> vide
| args ("," args)*                                              -> aumoinsun

args : SIGNED_NUMBER                                            -> int_arg
| var_list                                                      -> var_arg

bcom : (com)*

func : name "(" var_list ")" "{" bcom ("return" exp ";")? "}"

prg : bfunc "main" "(" var_list ")" "{" bcom  "return" exp ";" "}"    -> prg

bfunc : (func)*

name : IDENTIFIER

var_list :                                                      -> vide
| IDENTIFIER ("," IDENTIFIER)*                                  -> aumoinsune

IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/

OPBIN : /[+\-*>]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", 
start="prg")

tab = "    "
g = "{"
d = "}"

op = {'+' : 'add', '-' : 'sub', '*' : 'imul', '/' : 'idiv'}

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
    else:

            s=""
            for i in range(len(e.children[1].children)):
                if(e.children[1].children[len(e.children[1].children)-1-i].data == "var_arg"):
                    temp=f"""
    mov rax, [{e.children[1].children[len(e.children[1].children)-1-i].children[0].children[0].value}]
    push rax 
                    """
                else:
                    temp=f"""
    mov rax, {e.children[1].children[len(e.children[1].children)-1-i].children[0].value}
    push rax 
                    """
                s=s+temp
            return f"""
    {s}
    call {e.children[0].children[0]}
    add rsp, 8*{len(e.children[1].children)}
                """

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_com(c):
    if c.data == "assignation":
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

def asm_func(f):
    C = asm_bcom(f.children[2])
    nbre_child=len(f.children)
    if nbre_child==4:
        E = asm_exp(f.children[3])
        s = ""
        for i in range(len(f.children[1].children)):
            v = f.children[1].children[i].value
            e = f"""
    mov rax, [rbp+{8+8*(i+1)}]
    mov [{v}], rax
        """
            s = s + e
        return f"""
{f.children[0].children[0].value}:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*{len(f.children[1].children)}
    
    push rdi
    push rsi
    
    {s}
    {C}
    {E}
    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    """
    else:
        s = ""
        for i in range(len(f.children[1].children)):
            v = f.children[1].children[i].value
            e = f"""
    mov rax, [rbp+{8+8*(i+1)}]
    mov [{v}], rax
        """
            s = s + e
        return f"""
{f.children[0].children[0].value}:
    push rbp
    mov rbp, rsp
    sub rsp, 8*{len(f.children[1].children)}
    push rdi
    push rsi
    {s}
    {C}
    nop
    xor rax, rax
    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    """

def asm_bfunc(bf):
    return "\n".join([asm_func(f) for f in bf.children])

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
    f=f"""{asm_bfunc(p.children[0])}"""
    moule = moule.replace("FUNC", f)
    return moule

def vars_exp(e):
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "call":
        return vars_argl(e.children[1])
    else:
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R

def vars_argl(al):
    if al.data == "vide":
        return set()
    else :
        S = set()
        for a in al.children:
            S = S | vars_arg(a)
    return S

def vars_arg(a):
    if a.data == "int_arg":
        return set ()
    else :
        return set([v.value for v in a.children[0].children])

def vars_func(f):
    L = set([v.value for v in f.children[1].children])
    M  = vars_bcom(f.children[2])
    R = set()
    if len(f.children)==4:
        R = vars_exp(f.children[3])
    return L|M|R

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

def vars_bfunc(bf):
    S = set()
    for f in bf.children:
        S = S | vars_func(f)
    return S

def vars_prg(p):
    F = vars_bfunc(p.children[0])
    L = set([t.value for t in p.children[1].children])
    C = vars_bcom(p.children[2])
    E = vars_exp(p.children[3])
    return L | C | E | F

def pp_exp(e, ntab = 0):
    tabulation = ntab * tab
    if e.data == "exp_nombre":
        return tabulation + e.children[0].value
    elif e.data == "exp_var":
        return tabulation + e.children[0].value
    elif e.data == "exp_par":
        return f"{tabulation}({pp_exp(e.children[0])})"
    elif e.data == "call":
        return f"{tabulation}{pp_name(e.children[0])}({pp_argsList(e.children[1])})"
    else:
        return f"{tabulation}{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def pp_argsList(al):
    if al.data == "vide":
        return f""
    else:
        return ", ".join([pp_arg(a) for a in al.children])

def pp_arg(a):
    if a.data == "int_arg":
        return a.children[0].value
    elif a.data == "var_arg":
        return pp_varlist(a.children[0])


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

def pp_bcom(bc, ntab = 0):
    return "\n".join([pp_com(c, ntab) for c in bc.children])

def pp_varlist(l):
    return ", ".join([var.value for var in l.children])

def pp_prg(p):
    g = "{"
    d = "}"
    return f"{pp_bfunc(p.children[0])} \n\nmain ({pp_varlist(p.children[1])}) {g} \n{pp_bcom(p.children[2], 1)} \n    return {pp_exp(p.children[3])}; \n{d}"

def pp_bfunc(bf, ntab = 0):
    return "\n\n".join([pp_func(f, ntab) for f in bf.children])

def pp_func(f, ntab = 0):
    tabulation = ntab * tab
    g = "{"
    d = "}"
    nbre_child=len(f.children)
    if nbre_child==3:
        if(pp_bcom(f.children[2])!=""):
            return f"{pp_name(f.children[0])} ({pp_varlist(f.children[1])}) {g} \n{pp_bcom(f.children[2], ntab+1)} \n{tabulation}{d}"
        else:
            return f"{pp_name(f.children[0])} ({pp_varlist(f.children[1])}) {g} \n{tabulation}{d}"
    else:
        if(pp_bcom(f.children[2])!=""):
            return f"{pp_name(f.children[0])} ({pp_varlist(f.children[1])}) {g} \n{pp_bcom(f.children[2], ntab+1)} \n{tabulation}{tab}return {pp_exp(f.children[3])}; \n{tabulation}{d}"
        else:
            return f"{pp_name(f.children[0])} ({pp_varlist(f.children[1])}) {g} \n{tabulation}{tab}return {pp_exp(f.children[3])}; \n{tabulation}{d}"

def pp_name(n):
    return f"{n.children[0]}"

#ast = grammaire.parse("a = a + 1;")
#ast = grammaire.parse("main (x, y) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} else {a = y;} return a;}")
#ast = grammaire.parse("main (x, y, z) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} return a;}")
#ast = grammaire.parse("main (x, y) { x = x + y; return x;} ")

ast = grammaire.parse("""
    somme(a, b, c, d, e, f, g, h, i){
        temp = a+b+c+d+e+f+g+h+i;
        return temp;
    }
    
    carre(a){
        return a*a;
    }
    
    main(prout){
        c=somme(1,2,3,prout,5,6,7,8,9);
        d=carre(12);
        return c+d;
    }
"""
)

"""print(ast)

pp = pp_prg(ast)
print('\n'+pp)"""

asm = asm_prg(ast)
f = open("ouf_func.asm", "w")
f.write(asm)
f.close()
