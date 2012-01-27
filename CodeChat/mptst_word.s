; mptst_word
; ==========
; This is an introductory PIC24 assembly language program, illustrating the syntax needed to write a simple program.
;
; Preliminaries
; =============
; First, we need to tell the assembler about all the special function registers specific to the chip we're using.
.include "p24Hxxxx.inc"

; Next, the linker will automatically jump to the label ``__reset``; we need to make this label globally visible so the linker can find it. By default, labels are visible only to the current file.
.global __reset

; Variables
; =========
; Now, we set aside space for any variables we need. The ``.bss`` directive refers to uninitialized memory, the correct location for our variables. These variables will begin at address ``0x0800``, since special function registers occupy addresses ``0x0000`` to ``0x07FF``.
.bss

; Here, we name each variable and specify its size in bytes.
i:       .space 2
j:       .space 2
k:       .space 2

; Code setup
; ==========
; Before we can write code, we notify the assembler to place the following instructions in program memory, which begins at ``0x0200``.
         .text

; As notied in the Preliminaries_, we must label the beginning of our program ``__reset``.
__reset:

; Before writing any other code, we first set up the stack; see :ref:`xxx` for more information.
        mov #__SP_init, w15
        mov #__SPLIM_init,W0   
        mov W0, SPLIM


; .. _mptst_word_code:
;
; User code
; =========
; At last, we're ready to write code. We'll use an (almost) three step process. After giving a line of `C` code to translate, we'll first specify a register assignment in comments below and possibly above the line of `C`. Next, data will be input from memory into working registers, then processed within these registers, then output from these registers back to memory. Here's an example:

; .. begin_clip
    ; \0. Register assignment
    ;;  u16_a = u16_b + u16_c
    ;;   W0      W1      W2
    ; \1. Input
    mov u16_b, W1
    mov u16_c, W2
    ; \2. Process
    add W1, W2, W0
    ; \3. Output
    mov u15_a, W0
; .. end_clip

; Finishing up
; ============
; After our user code finishes, the processor still needs something to do. Have it run in an infinite loop, rather than executing whatever unknown instructions which happen to follow our program.
done:
    goto done

; This tells the assembler that the program is finished.
.end
