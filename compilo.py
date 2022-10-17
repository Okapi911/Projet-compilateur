import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                                             -> exp_nombre
| IDENTIFIER                                                    -> exp_var
| exp OPBIN exp                                                 -> exp_opbin
| "(" exp ")"                                                   -> exp_par
| name "(" var_list ")"                                         -> call

com : IDENTIFIER "=" exp ";"                                    -> assignation
| "if" "(" exp ")" "{" bcom "}"                                 -> if
| "if" "(" exp ")" "{" bcom "}" "else" "{" bcom "}"             -> if_else
| "while" "(" exp ")" "{" bcom "}"                              -> while
| "print" "(" exp ")" ";"                                       -> print

bcom : (com)*

func : name "(" var_list ")" "{" bcom  ("return" exp ";")? "}"

prg : "main" "(" var_list ")" "{" bcom  "return" exp ";" "}"

name : IDENTIFIER

var_list :                                                      -> vide
| IDENTIFIER ("," IDENTIFIER)*                                  -> aumoinsune

IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/

OPBIN : /[+\-*>]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", 
start="func")

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
    else:
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
    elif e.data == "exp_par":
        return f"{tabulation}({pp_exp(e.children[0])})"
    elif e.data == "call":
        return f"{tabulation}{pp_name(e.children[0])}({pp_varlist(e.children[1])})"
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

def pp_bcom(bc, ntab = 0):
    return "\n".join([pp_com(c, ntab) for c in bc.children])

def pp_varlist(l):
    return ", ".join([var.value for var in l.children])

def pp_prg(p):
    g = "{"
    d = "}"
    return f"main ({pp_varlist(p.children[0])}) {g} \n{pp_bcom(p.children[1], 1)} \n    return {pp_exp(p.children[2])}; \n{d}"

def pp_name(n):
    return f"{n.children[0]}"

def pp_func(f):
    g = "{"
    d = "}"
    if (len(f.children)==4):
        return f"{pp_name(f.children[0])} ({pp_varlist(f.children[1])}) {g} \n{pp_bcom(f.children[2], 1)} \n    return {pp_exp(f.children[3])}; \n{d}"
    else :
        return f"{pp_name(f.children[0])} ({pp_varlist(f.children[1])}) {g} \n{pp_bcom(f.children[2], 1)} \n{d}"
#ast = grammaire.parse("a = a + 1;")
#ast = grammaire.parse("main (x, y) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} else {a = y;} return a;}")
#ast = grammaire.parse("main (x, y, z) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} return a;}")
#ast = grammaire.parse("main (x, y) { x = x + y; return x;} ")

ast = grammaire.parse("""f(x,y){
    while(x){
        x = f(y);
        y=y+1;
    }
    return f(x);
} """
)

pp = pp_func(ast)
print(pp)

"""asm = asm_prg(ast)
f = open("ouf.asm", "w")
f.write(asm)
f.close()"""