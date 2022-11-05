from http.client import FORBIDDEN
from logging.handlers import SYSLOG_UDP_PORT
from tokenize import Token
import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                                             -> exp_nombre
| IDENTIFIER                                                    -> exp_var
| PIDENTIFIER                                                   -> exp_pvar
| exp OPBIN exp                                                 -> exp_opbin
| "(" exp ")"                                                   -> exp_par
| "type("exp")"                                                 -> exp_type
| NULL                                                          -> exp_null
| IDENTIFIER "(" var_list ")"                                        -> exp_call


com : IDENTIFIER "=" exp ";"                                    -> assignation
| PIDENTIFIER "=" exp ";"                                       -> p_assignation
| "if" "(" exp ")" "{" bcom "}"                                 -> if
| "if" "(" exp ")" "{" bcom "}" "else" "{" bcom "}"             -> if_else
| "while" "(" exp ")" "{" bcom "}"                              -> while
| "print" "(" exp ")" ";"                                       -> print
| IDENTIFIER "(" var_list ")" ";"                               -> com_call

bcom : (com)*

bcls : (cls)*

prg : bcls bfunc "main" "(" var_list ")" "{" bcom  "return" exp ";" "}"

cls : "class" IDENTIFIER "{" IDENTIFIER "(" var_list ")" "{" bcom "}" "}"                   -> declaration_class

func : IDENTIFIER "(" var_list ")" "{" bcom ("return" exp ";")? "}"

bfunc : (func)*

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

op = {'+' : 'add', '-' : 'sub', '*' : 'imul', '/' : 'idiv'}

def get_type(e):
    if type(e) == lark.lexer.Token:
        if e.type == "SIGNED_NUMBER":
            return 0
    else:
        if e.data == "exp_nombre":
            return 0
        elif e.data == "exp_var":
            return typeVar[e.children[0].value]
        elif e.data == "exp_pvar":
            return typeVar[e.children[0].value.split(".")[-1]]
        elif e.data == "exp_par":
            return get_type(e.children[0])
        elif e.data == "exp_null":
            return -1
        elif e.data == "exp_opbin":
            return get_type(e.children[0])
        elif e.data == "exp_call":
            if e.children[0].value in listClass:
                return typeObjects[e.children[0]]
            else:
                return typeFunctions[e.children[0]]
        elif e.data == "exp_type":
            return 1

def asm_pvar(e):

    if type(e) == lark.lexer.Token:
        nom = e
    else:
        nom = e.children[0].value

    att_pvar = nom.split(".")
    size_pvar = len(att_pvar)

    if "this" in nom:
        print(nom)

        attribut = nom.split(".")[1]
        nomClass = find_cls(attribut)
        decalage = len(attributs[nomClass]) - attributs[nomClass].index(nom) - 1
        return f"""    mov rax, [rax + {8 * decalage}]"""

    else:
        debut = f"""{att_pvar[0]}"""

        s = f"""
            mov rax, [{debut}]
        """

        for i in range(1, size_pvar):

            classe = find_cls(att_pvar[i])
            decalage = len(attributs[classe]) - attributs[classe].index(f"""this.{att_pvar[i]}""") - 1
            e = f"""
            lea r8, [rax]
            mov rax, [r8+ {8 * decalage}]  
            """
            s = s+e
        return s

def asm_exp(e):
    
    if e.data == "exp_nombre":
        return f"""
    mov rax, {e.children[0].value}"""
    
    elif e.data == "exp_var":
        return f"""
    mov rax, [{e.children[0].value}]"""
    
    elif e.data == "exp_pvar":
        return asm_pvar(e)

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
    elif e.data == "exp_type":
        return f"""
    mov rax, {get_type(e.children[0])}    
    """
    elif e.data == "exp_call":

        nom = e.children[0].value

        if nom in listClass:
            s = f"""
                sub rsp, {sizePerClass[e.children[0].value]}


                lea rax, [rbp - {objectsCreated[-1][1]}]
                mov rdi, rax
                """
            arg= 0
            for v in reversed(e.children[1].children):
                arg += 1

                if v.type == "SIGNED_NUMBER":

                    E = f"""
                    mov rax, {v}
                    push rax
                    """
                elif v.type == "PIDENTIFIER":
                    PVAR = asm_pvar(v)
                    E = f"""
                    {PVAR}
                    push rax
                    """
                else:
                    E = f"""
                    mov rax, [{v}]
                    push rax
                    """
                s = s + E

            return s

        elif nom in listFunctions :
            s=""
            for i in range(len(e.children[1].children)):
                if(e.children[1].children[len(e.children[1].children)-1-i].type == "SIGNED_NUMBER"):
                    temp=f"""
                    mov rax, {e.children[1].children[len(e.children[1].children)-1-i]}
                    push rax 

                    """
                elif (e.children[1].children[len(e.children[1].children)-1-i].type == "PIDENTIFIER"):
                    PVAR = asm_pvar(e.children[1].children[len(e.children[1].children)-1-i])
                    temp=f"""
                    {PVAR}
                    push rax 
                    """
                
                else:
                    temp=f"""
                    mov rax, [{e.children[1].children[len(e.children[1].children)-1-i]}]
                    push rax 

                    """
                s=s+temp

            return f"""
                {s}
                call {e.children[0].value}
                add rsp, 8*{len(e.children[1].children)}
                """
        return s

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt


def asm_com(c):

    if c.data == "assignation":
        if c.children[1].data == "exp_call":


            if(c.children[1].children[0] in listClass):
                typeVar[c.children[0].value] = get_type(c.children[1])

                place = find_place(c.children[1].children[0])
                objectsCreated.append((c.children[0].value, place))

                return f"""
    lea r9, [rbp - {objectsCreated[-1][1]}]
    mov [{objectsCreated[-1][0]}], r9
    {asm_exp(c.children[1])}
    call {c.children[1].children[0]}
                """
            else:
                E1 = asm_exp(c.children[1])
                return f"""
    {E1}
    mov [{c.children[0].value}], rax 
                """
        else:
            E1 = asm_exp(c.children[1])
            return f"""
    {E1}
    mov [{c.children[0].value}], rax 
            """
            
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
    
    elif c.data == "if_else":
        E1 = asm_exp(c.children[0])
        C1 = asm_bcom(c.children[1])
        C2 = asm_bcom(c.children[2])
        n1 = next()
        n2 = next()
        return f"""
    {E1}
    cmp rax, 0
    jz else{n1}
    {C1}
    jmp fin{n2}
    else{n1} :
    {C2}
    fin{n2} : nop
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
    
    elif c.data == "com_call":
        nom = c.children[0]
        if nom in listFunctions :
            s=""
            for i in range(len(c.children[1].children)):
                if(c.children[1].children[len(c.children[1].children)-1-i].type == "SIGNED_NUMBER"):
                    temp=f"""
                    mov rax, {c.children[1].children[len(c.children[1].children)-1-i]}
                    push rax 

                    """
                elif (c.children[1].children[len(c.children[1].children)-1-i].type == "PIDENTIFIER"):
                    temp=f"""
                    mov rax, [rbp - {give_address_attribute(c.children[1].children[len(c.children[1].children)-1-i])}]
                    push rax 
                    """
                
                else:
                    temp=f"""
                    mov rax, [{c.children[1].children[len(c.children[1].children)-1-i]}]
                    push rax 

                    """
                s=s+temp

            return f"""
                {s}
                call {c.children[0].value}
                add rsp, 8*{len(c.children[1].children)}
                """
        else:
            s=""
        return s

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

    return f"""
{cls.children[0]} :
    push rbp
    mov rbp, rsp

    {s}

    {asm_bcom(cls.children[3])}
    
    mov rsp, rbp
    pop rbp
    ret
    """
    
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
{f.children[0].value}:
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
{f.children[0].value}:
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

def asm_bcls(bcls):
    return "\n".join([asm_cls(c) for c in bcls.children])

def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)

    s = ""
    for i in range(len(p.children[2].children)):
        v = p.children[2].children[i].value
        typeVar[v] = 0
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

    f=f"""{asm_bfunc(p.children[1])}"""
    moule = moule.replace("FUNC", f)

    C = asm_bcom(p.children[3])
    moule = moule.replace("BODY", C)

    E = asm_exp(p.children[4])
    moule = moule.replace("RETURN", E)


    return moule

varsPerClass = {}
attributs = {}
argument_constructeur = {}

sizePerClass = {}
objectsCreated = []

listFunctions = []
listClass = []

typeObjects = {"SIGNED_NUMBER" : 0}
typeVar = {}

typeReturnFunctions = {}
def vars_exp(e):
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_var":
        return {e.children[0].value}
    elif e.data == "exp_pvar":
        variable = (e.children[0].value + "").replace(".", "$")
        return set()
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_opbin":
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R
    elif e.data == "exp_call":
        L = set([t.value for t in e.children[1].children if not "." in t and t.type != "SIGNED_NUMBER"])
        return L
    elif e.data == "exp_type":
        return vars_exp(e.children[0])
        
    
def vars_cls(cls):
    listClass.append(cls.children[0].value)
    typeObjects[cls.children[0].value] = len(typeObjects.keys())

    L = [t.value for t in cls.children[2].children]
    argument_constructeur[cls.children[0].value] = L

    VL = set(L)
    BC = vars_bcom(cls.children[3])

    varsPerClass[cls.children[0].value] = VL | BC
    
    attributs[cls.children[0].value] = [var for var in varsPerClass[cls.children[0].value] if "this" in var]
    for k in attributs.keys():
        attributs[k] = sorted(attributs[k])
    sizePerClass[cls.children[0].value] = 8 * len(attributs[cls.children[0].value])

def vars_bcls(bcls):
    for cls in bcls.children:
        vars_cls(cls)

def vars_func(f):
    listFunctions.append(f.children[0].value)
    L = set([v.value for v in f.children[1].children])
    M  = vars_bcom(f.children[2])
    R = set()
    if len(f.children)==4:
        R = vars_exp(f.children[3])
    return L|M|R

def vars_com(c):
    if c.data == "assignation":
        if c.children[1].data == "exp_call":
            nom = c.children[1].children[0].value
            L = vars_exp(c.children[1])
            return {c.children[0].value} | L

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
    
    elif c.data == "if_else":
        B = vars_bcom(c.children[1])
        B2 = vars_bcom(c.children[2])
        E = vars_exp(c.children[0])
        return E | B | B2

    elif c.data == "while":
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return E | B

    elif c.data == "print":
        return vars_exp(c.children[0])
    
    elif c.data == "com_call":
        L = set([v.value for v in c.children[1].children if not "." in v and v.type != "SIGNED_NUMBER"])
        return L

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
    vars_bcls(p.children[0])
    F = vars_bfunc(p.children[1])

    BCLS = set()
    for cls in varsPerClass:
        BCLS = BCLS | set([v for v in varsPerClass[cls] if not "." in v])

    L = set([t.value for t in p.children[2].children])

    C = vars_bcom(p.children[3])
    E = vars_exp(p.children[4])

    return L | C | E | BCLS | F

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
    elif e.data == "exp_call":
        return f"{e.children[0].value}({pp_varlist(e.children[1])})"
    elif e.data == "exp_type":
        return f"type({pp_exp(e.children[0])})"


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
    
    elif c.data == "com_call":
        return f"{tabulation}{c.children[0].value} ({pp_varlist(c.children[1])});"

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
    if(pp_bcom(p.children[3])!=""):
        return f"{pp_bcls(p.children[0])} \n\n{pp_bfunc(p.children[1])} \n\nmain ({pp_varlist(p.children[2])}) {g} \n{pp_bcom(p.children[3], 1)} \n    return {pp_exp(p.children[4])}; \n{d}"
    else:
        return f"{pp_bcls(p.children[0])} \n\n{pp_bfunc(p.children[1])} \n\nmain ({pp_varlist(p.children[2])}) {g} \n    return {pp_exp(p.children[4])}; \n{d}"

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

    

def pp_bfunc(bf, ntab = 0):
    return "\n\n".join([pp_func(f, ntab) for f in bf.children])

def pp_func(f, ntab = 0):
    tabulation = ntab * tab
    g = "{"
    d = "}"
    nbre_child=len(f.children)
    if nbre_child==3:
        if(pp_bcom(f.children[2])!=""):
            return f"{f.children[0]} ({pp_varlist(f.children[1])}) {g} \n{pp_bcom(f.children[2], ntab+1)} \n{tabulation}{d}"
        else:
            return f"{f.children[0]} ({pp_varlist(f.children[1])}) {g} \n{tabulation}{d}"
    else:
        if(pp_bcom(f.children[2])!=""):
            return f"{f.children[0]} ({pp_varlist(f.children[1])}) {g} \n{pp_bcom(f.children[2], ntab+1)} \n{tabulation}{tab}return {pp_exp(f.children[3])}; \n{tabulation}{d}"
        else:
            return f"{f.children[0]} ({pp_varlist(f.children[1])}) {g} \n{tabulation}{tab}return {pp_exp(f.children[3])}; \n{tabulation}{d}"


ast = grammaire.parse("""
class Point{
    Point(coord1, coord2){
        this.x = coord1;
        this.y = coord2;
    }
}
class Rectangle{
    Rectangle(point1, point2, point3, point4){
        this.p1 = point1;
        this.p2 = point2;
        this.p3 = point3;
        this.p4 = point4;
    }
}
perimetre(rectangle){
    d1 = rectangle.p2.x - rectangle.p1.x;
    d2 = rectangle.p4.y - rectangle.p1.y;
    return (2*d1) + (2*d2);
}
aire(rectangle){
    d1 = rectangle.p2.x - rectangle.p1.x;
    d2 = rectangle.p4.y - rectangle.p1.y;
    return d1*d2;
}
somme(a, b){
    return a+b;
}
main(){
    p1 = Point(0, 0);
    p2 = Point(3, 0);
    p3 = Point(2, 7);
    p4 = Point(0, 7);
    p3 = Point(3, 7);
    r = Rectangle(p1, p2, p3, p4);

    typeObjetR = type(r);

    if (r.p1.x){
        b = somme(r.p4.y, 50);
    }else {
        b = aire(r);
    }

    return b;
}
""")

print(pp_prg(ast))


asm = asm_prg(ast)
print()
print(typeObjects)
print(typeVar)
print()

f = open("ouf.asm", "w")

f.write(asm)
f.close()
