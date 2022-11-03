extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
vec1 : dq 0
f : dq 0
s : dq 0
A : dq 0



section .text
global main

Vecteur :
    push rbp
    mov rbp, rsp

    
        mov rax, [rbp+16]
        mov [f], rax
        
        mov rax, [rbp+24]
        mov [s], rax
        
        mov [rbp-8], rdi
        sub rsp, 16
        

    
            mov rax, [f]


            mov rdx, rax
            mov rax, [rbp-8]
            mov [rax + 8], rdx 
            

            mov rax, [s]


            mov rdx, rax
            mov rax, [rbp-8]
            mov [rax + 0], rdx 
            

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
        mov [A], rax
        
    
            lea r9, [rbp - 16]
            mov [vec1], r9
            
            sub rsp, 16


            lea rax, [rbp - 16]
            mov rdi, rax
            
            mov rax, 2000
            push rax
            
            mov rax, 1000
            push rax
            
            call Vecteur
            

            
        mov rax, [rbp - 16]

        mov r8, rax
        mov rax, 500

        add rax, r8
        
            mov [rbp - 8], rax 
            
    mov rax, [rbp - 8]


    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret