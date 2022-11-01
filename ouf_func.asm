extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
x : dq 0
s : dq 0
a : dq 0
d : dq 0
c : dq 0

section .text
global main


f:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*2
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [x], rax
        
    mov rax, [rbp+24]
    mov [a], rax
        
    
    debut1 : mov rax, [x]

    cmp rax, 0
    jz fin1
    
    
    mov rax, [a]

    push rax
    mov rax, [a]

    pop rbx
    imul rax, rbx
        
    mov [a], rax 
        

    
    mov rax, 1

    push rax
    mov rax, [x]

    pop rbx
    sub rax, rbx
        
    mov [x], rax 
        
    jmp debut1
    fin1 : nop
        
    mov rax, [a]

    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    

main :
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    
    mov rbx, [argv]
    mov rdi, [rbx + 8]
    xor rax, rax
    call atoi
    mov [d], rax
        
    mov rbx, [argv]
    mov rdi, [rbx + 16]
    xor rax, rax
    call atoi
    mov [s], rax
        
    
    
    
    mov rax, [s]
    push rax 
            
    mov rax, [d]
    push rax 
            
    call f
    add rsp, 8*2
        
    mov [c], rax 
        
    mov rax, [c]

    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret