Helpful Commands
================

I'm always searching for ways to do the following:

vi command to remove trailing white space in file:

.. code-block:: bash

   :%s/\s\+$//e

sed command to remove trailing white space in file:

.. code-block:: bash

   sed -i -e 's/\s\+$//' <file_name>

Search file for entry starting with some name and delete line. In my example
I'm searching the "~/.ssh/known_hosts" file for lines that start with "host51"
and deleting that line.

.. code-block:: bash

   sed -i -e '/^host51/d' ~/.ssh/known_hosts
