##################################################################################
Part x: PIC24 assembly
##################################################################################

**********************************************************************************
Chapter x: An introduction to PIC24 assembly
**********************************************************************************
 
.. toctree::
   :maxdepth: 5

   asm_template
   another_mov
   three_steps
   mptst_word

This document takes a hands-on, breadth-first approach to introducing assembly langauge. Rather than explain all concepts before they're used, this document enables you to experiment with then to find out what really works, then reinforces thae hands-on intuition you've developed with a minimal amount of explanation. Perform the exercises, or you'll lose much of the available learning.

Exploring an assembly-language program
=================================================================================

Let's begin by looking at the heart of a simple assembly-language program. In :doc:`asm_template` section :ref:`asm_template_code`, we have:

.. include:: asm_template.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

.. todo: Point to MPLAB IDE video tutorials; figure out how to nicely link to a file to be opened by an external applicaiton.

.. sidebar:: More on ``mov``

   See the `programmer's reference manual`_ for more information on what the `mov #number, Wdest`_ and `mov Wsource, memory_address`_ instructions.

.. _`data memory map`: ../../documents/24H_FRM/Section_03._Data_Memory-PIC24H_FRM_(70237A).pdf#page=3
.. _`programmer's reference manual`: ../../documents/16-bit_MCU_and_DSC_Programmer's_Reference_Manual_(70157F).pdf
.. _`mov #literal, Wdest`: ../../documents/16-bit_MCU_and_DSC_Programmer's_Reference_Manual_(70157F).pdf#page=284
.. _`mov Wsource, memory_address`: ../../documents/16-bit_MCU_and_DSC_Programmer's_Reference_Manual_(70157F).pdf#page=282

Load ``ch3/asm_template.mcp`` into the Microchip IDE, then run the program.

Exercise:

#. What value does W0 contain?
#. What value does memory location ``0x0800`` contain?

This brief snippet of code illustrates several important concepts. First, working registers such as ``W0`` above provide temporary storage locations; although the processor contains sixteen (``W0`` through ``W15``), ``W15`` is reserved for use with the stack. Second, user memory, termed "X Data RAM" in the PIC24's `data memory map`_, begins at location ``0x0800``. This explains the second operand in line (2) above. Third, the ``mov`` (move) instruction is a misnomer: even after executing line (2), the value ``0x1234`` assigned to ``W0`` in line (1) remains there after executing line (2) -- it's copied, not moved. Finally, note that all data is 16 bits (4 hexadecimal digist) wide; because the PIC24 is a 16-bit processor, this is the most natural size of data for it to work on.

Another ``mov``
=================================================================================
Let's explore the use of another ``mov`` instruction. Compile and run :doc:`another_mov`; the code in section :ref:`another_mov_code` is:

.. include:: another_mov.rst
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

Input instructions bring data in to the working registers, while output intructions push data out from working registers to memory. What's missing is the ability to process data once we've input it and before we've output the results.

Three steps for assembly language programs
=================================================================================
Compile and run :doc:`three_steps`; the code in section :ref:`three_steps_code` is:

.. include:: three_steps.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip
