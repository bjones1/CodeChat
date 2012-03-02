; ch3/asm_template.s
; ===============================================================================================
; This program presents a template for writing assembly language programs for the ARM Cortex-M3. See :doc:`asm_template_explained.s` for a detailed explanation of this program.
;
; License
; -----------------------------------------------------------------------------------------------
; | Copyright (c) 2012 Bryan A. Jones, Robert B. Reese, and J. W. Bruce ("AUTHORS")
; | All rights reserved.
; | (B. A. Jones, bjones AT ece.msstate.edu, Mississippi State University)
; | (R. Reese, reese_AT_ece.msstate.edu, Mississippi State University)
; | (J. W. Bruce, jwbruce_AT_ece.msstate.edu, Mississippi State University)
;
; Permission to use, copy, modify, and distribute this software and its
; documentation for any purpose, without fee, and without written agreement is
; hereby granted, provided that the above copyright notice, the following
; two paragraphs and the authors appear in all copies of this software.
;
; IN NO EVENT SHALL THE "AUTHORS" BE LIABLE TO ANY PARTY FOR
; DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
; OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE "AUTHORS"
; HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
;
; THE "AUTHORS" SPECIFICALLY DISCLAIMS ANY WARRANTIES,
; INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
; AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
; ON AN "AS IS" BASIS, AND THE "AUTHORS" HAS NO OBLIGATION TO
; PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
;
; Please maintain this header in its entirety when copying or modifying
; these files.
;
; Setup
; -----------------------------------------------------------------------------------------------
        PUBLIC  __iar_program_start, __iar_zero_init3

        ; Stack
        SECTION CSTACK : DATA (3)

        ; Interrupt vector table
        SECTION .intvec : CODE (2)
        DATA
__vector_table:
        DCD SFE(CSTACK)
        DCD __iar_program_start

        ; Global data
        SECTION .noinit : DATA (0)
u32_a:  DS32 1
        
        ; Code
        SECTION .text : CODE (2)
        THUMB
__iar_program_start:
main:

; .. _asm_template_code:
;
; User code
; -----------------------------------------------------------------------------------------------
; Place all user code here. The code below provides an example.
; .. begin_clip
        ldr R0, =0x12345678   ; Line (1)
        ldr R1, =u32_a        ; Line (2)
        str R0, [R1]          ; Line (3)
; .. end_clip

; Termination
; -----------------------------------------------------------------------------------------------
__iar_zero_init3:
done:
        B done

        END
