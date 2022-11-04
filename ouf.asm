extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
vec1 : dq 0
a : dq 0
y : dq 0
x : dq 0
b : dq 0
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
    

Point :
    push rbp
    mov rbp, rsp

    
    mov rax, [rbp+16]
    mov [f], rax
        
    mov rax, [rbp+24]
    mov [s], rax
        
    mov [rbp-8], rdi
    sub rsp, 16
        

    
            
    mov rax, [x]

    mov rdx, rax
    mov rax, [rbp-8]
    mov [rax + 8], rdx 
            

            
    mov rax, [y]

    mov rdx, rax
    mov rax, [rbp-8]
    mov [rax + 0], rdx 
            
    
    mov rsp, rbp
    pop rbp
    ret
    


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
    mov [A], rax
        
    
    lea r9, [rbp - 16]
    mov [vec1], r9
    
    sub rsp, 16
    lea rax, [rbp - 16]
    mov rdi, rax
                
    mov rax, 2
    push rax
                
    mov rax, 1
    push rax
                
    call Point
                

    lea r9, [rbp - 32]
    mov [vec1], r9
    
    sub rsp, 16
    lea rax, [rbp - 32]
    mov rdi, rax
                
    mov rax, 20
    push rax
                
    mov rax, 10
    push rax
                
    call Vecteur
                
    
    mov rax, [rbp - 16]

    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret