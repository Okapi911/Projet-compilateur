extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
7 : dq 0
a : dq 0
6 : dq 0
h : dq 0
2 : dq 0
g : dq 0
e : dq 0
5 : dq 0
8 : dq 0
i : dq 0
temp : dq 0
f : dq 0
3 : dq 0
prout : dq 0
12 : dq 0
1 : dq 0
c : dq 0
d : dq 0
9 : dq 0
b : dq 0



section .text
global main




somme:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*9
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [a], rax
        
    mov rax, [rbp+24]
    mov [b], rax
        
    mov rax, [rbp+32]
    mov [c], rax
        
    mov rax, [rbp+40]
    mov [d], rax
        
    mov rax, [rbp+48]
    mov [e], rax
        
    mov rax, [rbp+56]
    mov [f], rax
        
    mov rax, [rbp+64]
    mov [g], rax
        
    mov rax, [rbp+72]
    mov [h], rax
        
    mov rax, [rbp+80]
    mov [i], rax
        
    
    
    
    
    mov rax, [i]
    mov r8, rax
    
    
    
    mov rax, [h]
    mov r8, rax
    
    
    
    mov rax, [g]
    mov r8, rax
    
    mov rax, [f]
    add rax, r8
        
    mov r8, rax
    
    mov rax, [e]
    add rax, r8
        
    add rax, r8
        
    mov r8, rax
    
    mov rax, [d]
    add rax, r8
        
    add rax, r8
        
    mov r8, rax
    
    
    
    mov rax, [c]
    mov r8, rax
    
    mov rax, [b]
    add rax, r8
        
    mov r8, rax
    
    mov rax, [a]
    add rax, r8
        
    add rax, r8
        
    mov [temp], rax 
            
    
    mov rax, [temp]
    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    

carre:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*1
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [a], rax
        
    
    
    
    mov rax, [a]
    mov r8, rax
    
    mov rax, [a]
    imul rax, r8
        
    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    

main :
    push rbp
    mov rbp, rsp
    mov [argc], rdi
    mov [argv], rsi
    
    mov rbx, [argv]
    mov rdi, [rbx + 8]
    xor rax, rax
    call atoi
    mov [prout], rax
        
    

    
    
    mov rax, [d]
    mov r8, rax
    
    mov rax, [c]
    add rax, r8
        

    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret