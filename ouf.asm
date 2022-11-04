extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
b : dq 0
a : dq 0



section .text
global main




somme:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*2
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [a], rax
        
    mov rax, [rbp+24]
    mov [b], rax
        
    
    
    
    mov rax, [b]
    push rax
    
    mov rax, [a]
    pop rbx
    add rax, rbx
        
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
    mov [a], rax
        
    mov rbx, [argv]
    mov rdi, [rbx + 16]
    xor rax, rax
    call atoi
    mov [b], rax
        
    
    
    
    mov rax, [b]
    push rax 
                    
    mov rax, [a]
    push rax 
                    
    call somme
    add rsp, 8*2
                

    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret