extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
NULL : dq 0
DECL_VARS



section .text
global main

DECL_CLS

FUNC

main :
    push rbp
    mov rbp, rsp
    mov [argc], rdi
    mov [argv], rsi
    INIT_VARS
    BODY
    RETURN

    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret