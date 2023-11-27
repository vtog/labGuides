vi Notes
========

Remove trailing white space from within file

.. code-block:: bash

   :%s/\s\+$//e

Remove trailing white space from cli

.. code-block:: bash

   sed -i 's/\s\+$//' <file_name>

