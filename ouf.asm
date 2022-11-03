extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
a : dq 0
pt : dq 0
tree.y : dq 0
pt.y : dq 0
y : dq 0
b : dq 0
pt.x : dq 0
tree.x : dq 0
distanceAOrigine : dq 0
x : dq 0

section .text
global main


Point:
    push rbp
    mov rbp, rsp
    
    sub rsp, 8*2
    
    push rdi
    push rsi
    
    
    mov rax, [rbp+16]
    mov [x], rax
        
    mov rax, [rbp+24]
    mov [y], rax
        
    
            mov rax, [x]

            mov [tree.x], rax 
            

            mov rax, [y]

            mov [tree.y], rax 
            
    pop rsi
    pop rdi
    mov rsp, rbp
    pop rbp
    ret
    
get_x:
    mov rax, [tree.x]
    ret
    
get_y:
    mov rax, [tree.y]
    ret
    
    

main :
    push rbp
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
            
    call Point
    add rsp, 8*2
                
        mov [pt], rax 
        

        
        
    call get_y
    mov [pt.y], rax
    mov rax, [pt.y]
        push rax
        
        
    call get_y
    mov [pt.y], rax
    mov rax, [pt.y]
        push rax
        
        
    call get_x
    mov [pt.x], rax
    mov rax, [pt.x]
        push rax
        
    call get_x
    mov [pt.x], rax
    mov rax, [pt.x]
        pop rbx
        imul rax, rbx
        
        pop rbx
        add rax, rbx
        
        pop rbx
        imul rax, rbx
        
        mov [distanceAOrigine], rax 
        
    mov rax, [distanceAOrigine]

    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret