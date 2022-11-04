extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
i : dq 0
e : dq 0
x : dq 0
c : dq 0
h : dq 0
f : dq 0
y : dq 0
g : dq 0
prout : dq 0
d : dq 0
b : dq 0
a : dq 0
temp : dq 0
vect : dq 0



section .text
global main


Vecteur :
    push rbp
    mov rbp, rsp

    
    mov rax, [rbp+16]
    mov [x], rax
        
    mov rax, [rbp+24]
    mov [y], rax
        
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
    push rax
    
    
    
    mov rax, [h]
    push rax
    
    mov rax, [g]
    pop rbx
    add rax, rbx
        
    push rax
    
    
    mov rax, [f]
    push rax
    
    
    
    
    mov rax, [e]
    push rax
    
    mov rax, [d]
    pop rbx
    add rax, rbx
        
    push rax
    
    mov rax, [c]
    pop rbx
    add rax, rbx
        
    push rax
    
    
    mov rax, [b]
    push rax
    
    mov rax, [a]
    pop rbx
    add rax, rbx
        
    pop rbx
    add rax, rbx
        
    pop rbx
    add rax, rbx
        
    pop rbx
    add rax, rbx
        
    pop rbx
    add rax, rbx
        
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
    push rax
    
    mov rax, [a]
    pop rbx
    imul rax, rbx
        
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
        
    
    
    
    mov rax, 9
    push rax 
                    
    mov rax, 8
    push rax 
                    
    mov rax, 7
    push rax 
                    
    mov rax, 6
    push rax 
                    
    mov rax, 5
    push rax 
                    
    mov rax, [prout]
    push rax 
                    
    mov rax, 3
    push rax 
                    
    mov rax, 2
    push rax 
                    
    mov rax, 1
    push rax 
                    
    call somme
    add rsp, 8*9
                
    mov [c], rax 
                

    
    
    mov rax, 12
    push rax 
                    
    call carre
    add rsp, 8*1
                
    mov [d], rax 
                

    lea r9, [rbp - 16]
    mov [vect], r9
    
    sub rsp, 16
    lea rax, [rbp - 16]
    mov rdi, rax
                
    mov rax, 2
    push rax
                
    mov rax, 1
    push rax
                
    call Vecteur
                
    
    
    mov rax, [rbp - 16]
    push rax
    
    
    mov rax, [rbp - 8]
    push rax
    
    
    mov rax, [d]
    push rax
    
    mov rax, [c]
    pop rbx
    add rax, rbx
        
    pop rbx
    add rax, rbx
        
    pop rbx
    add rax, rbx
        

    mov rsp, rbp
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret