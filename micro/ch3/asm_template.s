; asm_template
; =======================================================================
; This program provides a template for writing a program in PIC24 assembly. To use this template, replace the `User code`_ section with your code.
;
; License
; -----------------------------------------------------------------------
; | Copyright (c) 2012 Bryan A. Jones, ("AUTHOR")
; | All rights reserved.
; | (B. A. Jones, bjones AT ece.msstate.edu, Mississippi State University)
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
; Please maintain this header in its entirety when copying/modifying
; these files.
;
;
; Preliminaries
; -----------------------------------------------------------------------
; First, we need to tell the assembler about all the special function registers specific to the chip we're using.
.include "p24Hxxxx.inc"

; Next, the linker will automatically jump to the label ``__reset``; we need to make this label globally visible so the linker can find it. By default, labels are visible only to the current file.
.global __reset

; Variables
; -----------------------------------------------------------------------
; Now, we set aside space for any variables we need. The ``.bss`` directive refers to uninitialized memory, the correct location for our variables. These variables will begin at address ``0x0800``, since special function registers occupy addresses ``0x0000`` to ``0x07FF``.
.bss

; Here, we name each variable and specify its size in bytes. The variable below isn't directly used in the code, but does provide an example (for template use) of setting aside space in which to store user data.
u16_a:  .space 2

; Code setup
; -----------------------------------------------------------------------
; Before we can write code, we notify the assembler to place the following instructions in program memory, which begins at ``0x0200``.
.text

; As notied in the Preliminaries_, we must label the beginning of our program ``__reset``.
__reset:

; Before writing any other code, we first set up the stack; see :ref:`xxx` for more information.
    mov #__SP_init, w15
    mov #__SPLIM_init,W0   
    mov W0, SPLIM


; .. _asm_template_code:
;
; User code
; -----------------------------------------------------------------------
; At last, we're ready to write code. Let's begin by executing two lines of assembly, the observing the results.

; .. begin_clip
    mov #0x1234, W0
    mov W0, 0x0800
; .. end_clip

; Finishing up
; -----------------------------------------------------------------------
; After our user code finishes, the processor still needs something to do. Have it run in an infinite loop, rather than executing whatever unknown instructions which happen to follow our program.
done:
    goto done
