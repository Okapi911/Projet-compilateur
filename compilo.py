from http.client import FORBIDDEN
from logging.handlers import SYSLOG_UDP_PORT
import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                                             -> exp_nombre
| IDENTIFIER                                                    -> exp_var
| PIDENTIFIER                                                   -> exp_pvar
| exp OPBIN exp                                                 -> exp_opbin
| "(" exp ")"                                                   -> exp_par
| IDENTIFIER "(" var_list ")"                                   -> exp_appel_class
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
| (IDENTIFIER|PIDENTIFIER|SIGNED_NUMBER) ("," (IDENTIFIER|PIDENTIFIER|SIGNED_NUMBER))*            -> aumoinsune

PIDENTIFIER : (/[a-zA-Z][a-zA-Z0-9]*/".")+ /[a-zA-Z][a-zA-Z0-9]*/

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

op = {'+' : 'add', '-' : 'sub'}

def asm_exp(e):
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_pvar":

        nom = e.children[0].value
        if "this" in nom:
            attribut = nom.split(".")[1]
            nomClass = find_cls(attribut)
            decalage = len(attributs[nomClass]) - attributs[nomClass].index(nom) - 1
            return f"""mov rax, [rax + {8 * decalage}]"""
        
        return f"mov rax, [rbp - {give_address_attribute(e.children[0].value)}]\n"

    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "exp_opbin":
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        mov r8, rax
        {E1}
        {op[e.children[1].value]} rax, r8
        """
    elif e.data == "exp_appel_class":
        s = f"""
            sub rsp, {sizePerClass[e.children[0].value]}


            lea rax, [rbp - {objectsCreated[-1][1]}]
            mov rdi, rax
            """
        for v in reversed(e.children[1].children):
            if v.type == "SIGNED_NUMBER":
                E = f"""
            mov rax, {v}
            push rax
            """
            else:
                E = f"""
            mov rax, [{v}]
            push rax
            """
            s = s + E
        return s

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt


def asm_com(c):
    if c.data == "assignation":
        if c.children[1].data == "exp_nombre" or c.children[1].data == "exp_var" or c.children[1].data == "exp_opbin":
            E1 = asm_exp(c.children[1])
            return f"""
            {E1}
            mov [{c.children[0].value}], rax 
            """
        elif c.children[1].data == "exp_appel_class":
            place = find_place(c.children[1].children[0])
            objectsCreated.append((c.children[0].value, place))
            return f"""
            lea r9, [rbp - {objectsCreated[-1][1]}]
            mov [{objectsCreated[-1][0]}], r9
            {asm_exp(c.children[1])}
            call {c.children[1].children[0]}
            """
        else:
            return ""
    elif c.data == "p_assignation":
        E1 = asm_exp(c.children[1])

        if "this" in c.children[0].value:

            attribut = c.children[0].value.split(".")[1]
            nomClass = find_cls(attribut)
            decalage = len(attributs[nomClass]) - attributs[nomClass].index(c.children[0].value) - 1

            return f"""
            {E1}

            mov rdx, rax
            mov rax, [rbp-8]
            mov [rax + {8 * decalage}], rdx 
            """
        else:
            return f"""
            {E1}
            mov [rbp - {give_address_attribute(c.children[0])}], rax 
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

def asm_cls(cls):

    s = f""""""

    for i in range(len(cls.children[2].children)):
        v = cls.children[2].children[i].value
        e = f"""
        mov rax, [rbp+{8*(i+2)}]
        mov [{v}], rax
        """
        s = s + e

    s = s + f"""
        mov [rbp-8], rdi
        sub rsp, 16
        """

    return f"""{cls.children[0]} :
    push rbp
    mov rbp, rsp

    {s}

    {asm_bcom(cls.children[3])}

    mov rsp, rbp
    pop rbp
    ret
    """

def asm_bcls(bcls):
    return "\n".join([asm_cls(c) for c in bcls.children])

def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    
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

    CLS = asm_bcls(p.children[0])
    moule = moule.replace("DECL_CLS", CLS)

    C = asm_bcom(p.children[2])
    moule = moule.replace("BODY", C)

    E = asm_exp(p.children[3])
    moule = moule.replace("RETURN", E)

    return moule

varsPerClass = {}
attributs = {}
sizePerClass = {}
objectsCreated = []

def vars_exp(e):
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
    elif e.data == "exp_pvar":
        variable = (e.children[0].value + "").replace(".", "$")
        #return {variable}
        return set()
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_opbin":
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R
    
def vars_cls(cls):
    
    VL = set([t.value for t in cls.children[2].children])
    BC = vars_bcom(cls.children[3])

    varsPerClass[cls.children[0].value] = VL | BC
    
    attributs[cls.children[0].value] = [var for var in varsPerClass[cls.children[0].value] if "this" in var]
    for k in attributs.keys():
        attributs[k] = sorted(attributs[k])
    sizePerClass[cls.children[0].value] = 8 * len(attributs[cls.children[0].value])

def vars_bcls(bcls):
    for cls in bcls.children:
        vars_cls(cls)
"""
def vars_call_cls(call, var_name):
    var_to_adapt = varsPerClass[call.children[0]]
    return set([v for v in var_to_adapt if "." not in v]) | {var_name.value}
    #return set([v.replace("this", var_name).replace(".", "$") for v in var_to_adapt]) | {var_name.value}
    #return {var_name.value}"""
    
def vars_com(c):

    if c.data == "assignation":
        if c.children[1].data == "exp_appel_class":
            #return vars_call_cls(c.children[1], c.children[0])
            return {c.children[0]}
        else:
            R = vars_exp(c.children[1])
            return {c.children[0].value} | R

    elif c.data == "p_assignation":
        R = vars_exp(c.children[1])
        if "this" in c.children[0]:
            return {c.children[0].value} | R
        else:
            return R

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

    vars_bcls(p.children[0])
    BCLS = set()
    for cls in varsPerClass:
        BCLS = BCLS | set([v for v in varsPerClass[cls] if not "." in v])

    L = set([t.value for t in p.children[1].children])
    C = vars_bcom(p.children[2])
    E = vars_exp(p.children[3])
    return L | C | E | BCLS

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
    elif e.data == "exp_opbin":
        return f"{tabulation}{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
    elif e.data == "exp_appel_class":
        return f"{e.children[0].value}({pp_varlist(e.children[1])})"

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

def find_cls(attribut):
    nom = f"""this.{attribut}"""
    for cls in attributs:
        if nom in attributs[cls]:
            return cls

def find_place(cls):
    if len(objectsCreated) == 0:
        return sizePerClass[cls]
    else:
        return objectsCreated[-1][1] + sizePerClass[cls]

#element de la forme aaa.bbb
def give_address_attribute(element):

    objet = element.split(".")[0]
    attribut = element.split(".")[1]

    classe = find_cls(attribut)

    for obj in objectsCreated:
        if obj[0] == objet:
            place_memoire = obj[1]
            break

    numero_attribut = attributs[classe].index(f"this.{attribut}")
    return place_memoire - 8*(len(attributs[classe]) - numero_attribut - 1)



#ast = grammaire.parse("a = a + 1;")
#ast = grammaire.parse("main (x, y) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} else {a = y;} return a;}")
#ast = grammaire.parse("main (x, y, z) {if(x>y) {while (x>5) {x = x - 1; print(x);} a = x;} return a;}")
#ast = grammaire.parse("main (x, y) { x = x + y; return x;} ")


ast = grammaire.parse("""
class Vecteur{
    Vecteur(f, s){
        this.first = f;
        this.second = s;
    }
}

main(A){
    vec1 = Vecteur(1000,2000);
    vec1.first = 500 + vec1.second;
    return vec1.first;
}

""")


#print(pp_prg(ast))
#print(asm_class(ast))

asm = asm_prg(ast)
print(sizePerClass)
print(objectsCreated)
print(attributs)
print(varsPerClass)


f = open("class4.asm", "w")
f.write(asm)
f.close()
