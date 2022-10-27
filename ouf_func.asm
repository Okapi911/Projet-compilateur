extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
x : dq 0

section .text


        f:
            push rbp
            mov rbp, rsp
            mov rsp, [rbp-8]
            
            mov rax, [y]

            mov rsp, rax
            mov rsp, rbp
            pop rbp
            ret
        

global main
main :
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    
        mov rbx, [argv]
        mov rdi, [rbx + 8]
        xor rax, rax
        call atoi
        mov [x], rax
        
    
    
        push x
        call f
        
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret