Exploring an assembly-language program
=================================================================================
.. sidebar:: More on ``mov``

   See the `programmer's reference manual`_ for more information on what the `mov #number, Wdest`_ and `mov Wsource, memory_address`_ instructions.

.. _`data memory map`: ../../documents/24H_FRM/Section_03._Data_Memory-PIC24H_FRM_(70237A).pdf#page=3
.. _`programmer's reference manual`: ../../documents/16-bit_MCU_and_DSC_Programmer's_Reference_Manual_(70157F).pdf
.. _`mov #number, Wdest`: ../../documents/16-bit_MCU_and_DSC_Programmer's_Reference_Manual_(70157F).pdf#page=284
.. _`mov Wsource, memory_address`: ../../documents/16-bit_MCU_and_DSC_Programmer's_Reference_Manual_(70157F).pdf#page=282

Let's begin by looking at the heart of a simple assembly-language program. In :doc:`../ch3/asm_template.s` section :ref:`asm_template_code`, we have:

.. include:: ../ch3/asm_template.s.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

.. todo: Point to MPLAB IDE video tutorials; figure out how to nicely link to a file to be opened by an external applicaiton.

Load ``ch3/asm_template.mcp`` into the Microchip IDE, then run the program.

Exercise:

#. What value does W0 contain?
#. What value does memory location ``0x0800`` contain?

This brief snippet of code illustrates several important concepts. First, working registers such as ``W0`` above provide temporary storage locations; although the processor contains sixteen (``W0`` through ``W15``), ``W15`` is reserved for use with the stack. Second, user memory, termed "X Data RAM" in the PIC24's `data memory map`_, begins at location ``0x0800``. This explains the second operand in line (2) above. Third, the ``mov`` (move) instruction is a misnomer: even after executing line (2), the value ``0x1234`` assigned to ``W0`` in line (1) remains there after executing line (2) -- it's copied, not moved. Finally, note that all data is 16 bits (4 hexadecimal digits) wide; because the PIC24 is a 16-bit processor, this is the most natural size of data for it to work on.

Instruction encoding and limitations
=================================================================================
The code in the previous section used two instructions to place a number (``0x1234``) in memory location ``0x0800``. The :doc:`../ch3/move_num_to_mem.s` program, section :ref:`move_num_to_mem_code`, proposes just this. Compile it.

Exercise:

#. What error does the assembler report?

To explain this error, let's examine how an assembly language intstruction becomes the bits which compose a machine-language instruction.

Another ``mov``
=================================================================================
Let's explore the use of another ``mov`` instruction by adding line (3) below. Compile and run :doc:`../ch3/another_mov.s`; the code in section :ref:`another_mov_code` is:

.. include:: /ch3/another_mov.s.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

Exercise:

#. What value does W1 contain?

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

