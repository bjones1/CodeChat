; ch3/another_mov
; =======================================================================
; This program illustrates the use of the ``mov memory_address, Wdest`` instruction. Unlike :doc:`asm_template`, most of the explanation has been removed to focus on the core of the program in the :ref:`another_mov_code` section.
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
    mov #__SP_init, w15
    mov #__SPLIM_init,W0   
    mov W0, SPLIM

; .. _another_mov_code:
;
; User code
; -----------------------------------------------------------------------

; .. begin_clip
    mov #0x1234, W0     ; line (1)
    mov W0, 0x0800      ; line (2)
    mov 0x0800, W1      ; line (3)
; .. end_clip

done:
    goto done
