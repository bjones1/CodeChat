##################################################################################
Part x: PIC24 assembly
##################################################################################

**********************************************************************************
Chapter x: An introduction to PIC24 assembly
**********************************************************************************
 
.. toctree::
   :maxdepth: 5

   mptst_word

Exploring an assembly-language program
=================================================================================

Let's begin by looking at the heart of a simple assembly-language program. In :doc:`asm_template` section :ref:`asm_template_code`, we have:

.. include:: asm_template.rst
   :start-after: .. begin_clip
   :end-before: .. end_clip

.. todo: Point to MPLAB IDE video tutorials

Load :download:`asm_template.mcp` into the Microchip IDE, then run the program. Answer the following questions:

#. What value does W0 contain?
#. What value does memory location ``0x0800`` contain?

In this brie