;
; Just check out MPLAB

		.include "p24Hxxxx.inc"

       .global __reset          ;The label for the first line of code. 

         .bss            ;unitialized data section
; These start at location 0x0800 because 0-0x07FF reserved for SFRs
i:       .space 2        ;Allocating space (in bytes) to variable.
j:       .space 2        ;Allocating space (in bytes) to variable.
k:       .space 2        ;Allocating space (in bytes) to variable.


; Code Section in Program Memory
; ==============================

         .text           ;Start of Code section
__reset:                 ; first instruction located at __reset label
        mov #__SP_init, w15       ;Initalize the Stack Pointer
        mov #__SPLIM_init,W0   
        mov W0, SPLIM             ;Initialize the stack limit register
; __SP_init set by linker to be after allocated data      

; User Code starts here.

; .. begin_clip
label:
    ; ::
    ;
    ;  u16_a = u16_b + u16_c
    ;   W0      W1      W2
    ;
    ; Input
    mov u16_b, W1
    mov u16_c, W2
    ; Process
    add W1, W2, W0
    ; Output
    mov u15_a, W0
; .. end_clip

done:
    goto     done

.end
