extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
NULL : dq 0
x : dq 0
a : dq 0



section .text
global main




f:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*1
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [x], rax
        
    
    
    mov rax, [x]
    mov rdi, fmt
    mov rsi, rax
    call printf
        
    
    
    mov rax, [x]
    push rax
    
    mov rax, 1
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
        
    
    
                
                    mov rax, [a]
                    push rax 

                    
                call f
                add rsp, 8*1
                

    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret