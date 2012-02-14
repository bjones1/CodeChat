; ch3/asm_template.s
; ===============================================================================================
; The program presents a template for writing assembly language programs for the ARM Cortex-M3 and discusses all the relevant syntax.
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
; First, we define four sections: for the Stack_, the `Interrupt vector table`_, `Global data`_, and Code_.

        ; The linker requires this public_ label by default_.
        PUBLIC  __iar_program_start
        ; If any data is defined, the linker requires this routine.
        PUBLIC  __iar_zero_init3

; Stack
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        
        ; This section contains RAM for the stack, which is allocated in the linker script.
        ;; (a)    (b)    (c)  (d)
        SECTION CSTACK : DATA (3)
        ; (a) The SECTION_ directive declares a separate section of this program to contain the stack.
        ; (b) Name the section ``CSTACK``, to agree with the `IAR build tools`_' naming of the stack.
        ; (c) Specify the memory type, which places this section in RAM.
        ; (d) Align the stack to :math:`2^3` or 8-byte boundaries, per ARM's recommendation_.

; Interrupt vector table
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        
        ; This section_ defines a interrupt vector table_ (IVT) containing a minimal set of interrupt vectors: an initial value for the stack and an entry point for the code.
	;; (a)      (b)    (c) (d)
        SECTION .intvec : CODE (2)
        ; (a) Declare a separate section of this program to contain the interrupt vectors.
        ; (b) Name the section ``.intvec``, to agree with the `IAR build tools`_' naming of the IVT.
        ; (c) Specify the memory type, which places this section in ROM.
        ; (d) Align the table to :math:`2^2` or 4-byte boundaries, the size of an address in 32-bit memory space.
	;
        ; The DATA_ directive defines data (the IVT) within a section of code.
        DATA
        ; This label tells the debugger_ where the IVT is located.
__vector_table:
        ; Word 0 is the reset value for the stack pointer, per the table_. The stack grows downward_, so this address gives the end of the stack. The `DCD`_ directive places a 32-bit constant in memory. The `SFE`_ operator determines the constant to place by computing the address of the end of the CSTACK section.
        DCD SFE(CSTACK)
        ; Word 1 is the entry point_ for this program. Note that the IAR assembler automatically sets bit 1 of all label references, per the spec_ for the IVT.
        DCD __iar_program_start

; Global data
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        
        ; This section allocates storage for global variables used in the program.
	;; (a)   (b)    (c) (d)
        SECTION .noinit : DATA (0)
        ; (a) Declare a separate section_ of this program to contain the data for the program.
        ; (b) Name the section ``.noinit``, to agree with the `IAR build tools`_' naming of uninitialized data.
        ; (c) Specify the memory type, which places this section in RAM.
        ; (d) Align the table to :math:`2^2` or 4-byte boundaries, so that 32-bit variables will be aligned by default.
        ;
        ; The ``DS8``, ``DS16``, and ``DS32`` directives_ allocate space (given by the number following the directive) for all variables. Be careful with alignment within the section: defining a single 8-bit value followed by a 16- or 32-bit value will misalign the second value! To avoid this, first define all 32-bit values, then all 16-bit values, then all 8-bit values.
u32_a:  DS32 1
        
; Code
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        
        ; This section contains the code for the program.
	;; (a)    (b)    (c) (d)
        SECTION .text : CODE (2)
        ; (a) Declare a separate section_ of this program to contain the code for the program.
        ; (b) Name the section ``.text``, to agree with the `IAR build tools`_' naming of the code.
        ; (c) Specify the memory type, which places this section in ROM.
        ; (d) Align the table to :math:`2^2` or 4-byte boundaries, per the TODO.
	;
        ; The THUMB_ directive instructs the asssembler to generate Thumb or Thumb-2 instructions, the only instruction set supported_ by the Cortex-M3.
        THUMB

; Code start
; ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        
; This label defines the beginning of the program, as referenced by the `Interrupt vector table`_.
__iar_program_start:
; By default, the debugger will run to this label, per the IAR IDE->Project Options->Debugger, Setup tab, Run to checkbox and edit box.
main:

; User code
; -----------------------------------------------------------------------------------------------
; Place all user code here. The code below provides an example.
        ; Place a constant in ``R0``.
        ldr R0, =0x12345678
        ; Place the address of ``u32_a`` in ``R1``.
        ldr R1, =u32_a
        ; Store the constant into ``u32_a``.
        str R0, [R1]

; Termination
; -----------------------------------------------------------------------------------------------
; Though it's not called, this label must exist.
__iar_zero_init3:

; This infinite loop gives the processor something to do when the user code finishes. Otherwise, it would execute whatever random instrutions happened to lie after the user code!
done:
        B done

        ; The END_ directive tells the assembler that this is the end of the module. Omitting this produces an error.
        END

; .. This list gives hyperlinks referenced in the comments above.
;
; .. _public: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=64
; .. _default: ../../documents/EWARM_IDEGuide.ENU.pdf#page=195
; .. _section: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=69
; .. _`IAR build tools`: ../../documents/EWARM_DevelopmentGuide.ENU.pdf#page=406
; .. _recommendation: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=647
; .. _DATA: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=66
; .. _debugger: ../../documents/EWARM_DevelopmentGuide.ENU.pdf#page=64
; .. _table: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=634
; .. _downward: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=643
; .. _DCD: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=91
; .. _SFE: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=54
; .. _point: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=633
; .. _spec: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=635
; .. _directives: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=91
; .. _THUMB: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=66
; .. _supported: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=33
; .. _END: ../../documents/EWARM_AssemblerReference.ENU.pdf#page=61
