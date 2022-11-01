extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
a : dq 0
b : dq 0
c : dq 0
d : dq 0

section .text
global main


f:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*1
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [a], rax
        
    
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
    mov [b], rax
        
    
    
    
    mov rax, [b]
    push rax 
                    
    call f
    add rsp, 8*1
                
    mov [c], rax 
        

    
    
    mov rax, 4
    push rax 
                    
    call f
    add rsp, 8*1
                
    mov [d], rax 
        
    
    mov rax, [d]

    push rax
    mov rax, [c]

    pop rbx
    add rax, rbx
        
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret