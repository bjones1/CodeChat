; ch3/000_move.s
; =======================================================================
; A short assembly-language program. See :doc:`900_asm_template.s` for more explanation of the syntax; this document focuses only on the :ref:`000_move_code`.
;
; License
; -----------------------------------------------------------------------
; | Copyright (c) 2012 Bryan A. Jones, Robert B. Reese, J. W. Bruce ("AUTHORS")
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
; HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
;
; THE "AUTHORS" SPECIFICALLY DISCLAIM ANY WARRANTIES,
; INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
; AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
; ON AN "AS IS" BASIS, AND THE "AUTHORS" HAVE NO OBLIGATION TO
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

.text
__reset:

; .. _000_move_code:
;
; Core code
; -----------------------------------------------------------------------
; Here's the core of the program.

; .. begin_clip
    mov #0x1234, W0     ; line (1)
    mov W0, 0x0800      ; line (2)
; .. end_clip


; Finishing up
; -----------------------------------------------------------------------
done:
    goto done
