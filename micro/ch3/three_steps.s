; ch3/three_steps
; =======================================================================
; This program illustrates the three step process for writing fragments of assembly langauge code. Unlike :doc:`asm_template`, most of the explanation has been removed to focus on the core of the program in the :ref:`three_steps_code` section.
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
.include "p24Hxxxx.inc"
.global __reset

; Variables
; -----------------------------------------------------------------------
.bss
u16_a:  .space 2

; Code setup
; -----------------------------------------------------------------------
.text
__reset:
    mov #__SP_init, W15
    mov #__SPLIM_init, W0   
    mov W0, SPLIM

; .. _three_steps_code:
;
; User code
; -----------------------------------------------------------------------

; .. begin_clip
    ; \1. Input
    mov #0x1234, W0     ; line (1)
    mov #0x8765, W1      ; line (2)
    ; \2. Process
    add W0, W1, W2
    ; \3. Output
    mov W2, 0x0800      ; line (3)
; .. end_clip

done:
    goto done
