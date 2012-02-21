Exploring an assembly-language program
=================================================================================
Let's begin by looking at the heart of a simple assembly-language program. In :doc:`../ch3/asm_template.s` section :ref:`asm_template_code`, we have:

.. include:: ../ch3/asm_template.s.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

.. todo: Point to IDE video tutorials; figure out how to nicely link to a file to be opened by an external applicaiton.

Follow the video tutorial below to load ``ch3/ch3.eww`` into the IAR IDE, select the ``asm_template`` project, then run the program in the simulator.

.. topic:: Exercise

   #. What value does R0 contain?
   #. What value does R1 contain?
   #. What is the address of u32_a?
   #. What value does u32_a contain?

.. sidebar:: Registers ``R13`` through ``R15``

   These registers_ have specific names and uses:

   ========  ======  =======================
   Register  Name    Use
   ========  ======  =======================
   ``R13``   ``SP``  Stack pointer
   ``R14``   ``LR``  Link register
   ``R15``   ``PC``  Program counter
   ========  ======  =======================

This brief snippet of code illustrates several important concepts. First, registers such as ``R0`` used in line (1) above provide temporary storage locations; the processor contains sixteen registers_ (``R0`` through ``R15``), but reservers the last three for specific uses (see the sidebar). Second, the |LDR|_ (load register) instruction in lines (1)-(2) above loads a value (a contant, such as ``0x12345678`` or an address, the location of ``u32_a`` in memory) into a register. Likewise, |STR|_ (store register) instruction stores the value in ``R``\t to the address in ``R``\n. Finally, note that all data is 32 bits (8 hexadecimal digits) wide; because the ARM is a 32-bit processor, this is the most natural size of data for it to work on.

.. _registers: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=46
.. |LDR| replace:: ``LDR R``\t, label
.. _LDR: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=289
.. |STR| replace:: ``STR R``\t, ``[R``\n]
.. _STR: ../../documents/DDI0403D_arm_architecture_v7m_reference_manual_errata_markup_1_0.pdf#page=473

.. topic:: Exercise

   #. Add a one-line comment before each of the lines above to describe what they do.

Instruction encoding and limitations
=================================================================================
The code in the previous section used two instructions to place a number (``0x12345678``) into the variable u32_a. This seems inefficient; the :doc:`../ch3/one_instruction.s` program, section :ref:`one_instruction_code`, proposes a single-instruction solution. Assemble it.

.. topic:: Exercise

  #. What error does the assembler report?

To explain this error, let's examine how an assembly language intstruction becomes the bits which compose a machine-language instruction. We'll begin by looking at the machine code generated for the previous program.


Here's a summary of the data copying instructions introduced so far.

===============================   ============================
Input                             Output
===============================   ============================
``mov #number, Wdest``
``mov memory_address, Wdest``     ``mov Wsource, memory_address``
===============================   ============================

Input instructions bring data in to the working registers, while output intructions push data out from working registers to memory.

Three steps for assembly language programs
=================================================================================
.. sidebar:: Simplicity versus efficiency

   | The approach taken in this book is to introduce the smallest possible portion of the PIC24 instruction set which covers all the capabilities of the PIC24. In particular, the ``mov Wsource1, Wsource2, Wdest`` instruction used in this document is but one of several other forms of the instruction:
   |
   |   ``add f, {WREG}``
   |   ``add Wsource, #5_bit_number, Wdest``
   |   ``add Wsource_dest, #10_bit_number``

   Follow the links above for more information on these forms of the add intruction.

.. todo:
   The links in the add instructions above

Compile and run :doc:`../ch3/three_steps.s`; the code in section :ref:`three_steps_code` is:

.. include:: /ch3/three_steps.s.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

Exercise:

#. What value does ``0x0800`` contain? Explain the behavior of the ``add`` instruction by replacing the question marks: W? = W? + W?.

