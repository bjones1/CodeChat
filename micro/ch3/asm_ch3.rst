##################################################################################
Part x: PIC24 assembly
##################################################################################

**********************************************************************************
Chapter x: An introduction to PIC24 assembly
**********************************************************************************
 
.. toctree::
   :maxdepth: 5

   mptst_word

.. |datasheets| replace::
    ../../datasheets

Exploring an assembly-language program
=================================================================================

Let's begin by looking at the heart of a simple assembly-language program. In :doc:`asm_template` section :ref:`asm_template_code`, we have:

.. include:: asm_template.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

.. todo: Point to MPLAB IDE video tutorials; figure out how to nicely link to a file to be opened by an external applicaiton.

Load :download:`asm_template.mcp` into the Microchip IDE, then run the program. Answer the following questions:

#. What value does W0 contain?
#. What value does memory location ``0x0800`` contain?

This brief snippet of code illustrates several important concepts. First, working registers such as ``W0`` above provide temporary storage locations; although the processor contains sixteen (``W0`` through ``W15``), ``W15`` is reserved for use with the stack. Second, user memory begins at location ``0x0800``, based on the PIC24's `data memory map`_.

.. _`data memory map`: |datasheets|/24H_FRM/Section_03._Data Memory-PIC24H_FRM_(70237A)

