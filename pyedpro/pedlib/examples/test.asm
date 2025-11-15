; -----------------------------------------------------------------------------
; string_token -- See if string one is a token of string two
;  IN:    RSI = string one token
;         RDI = string two payload
; OUT:    Carry flag set if same

string_token:
    push rsi
    push rdi
    push rbx
    push rax

%if 0
    ;push rsi
    ;mov  rsi, rdi
    ;call mon_debug_dump_mem
    ;pop rsi
%endif

; string_token_more:
    mov al, [rsi]    		   ; String contents
    mov  bl, [rdi]
    test al, al    		       ; End of first string?
    jz  string_token_same
    test bl, bl    		       ; End of second string?
    jz string_token_not_same
    cmp  al, bl
    jne  string_token_not_same
    inc  rsi
    inc  rdi
    jmp  string_token_more

'''  string_token_same:
    pop  rax
    pop  rbx
    pop  rdi
    pop  rsi
    clc
    ret
'''
 string_token_not_same:
    pop rax
    pop rbx
    pop rdi
    pop rsi
    stc
    ret

