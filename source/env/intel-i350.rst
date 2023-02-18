Enable SR-IOV on Intel I350
===========================

I bought this card on eBay and it turns out different manufacturer's disable the
SR-IOV feature. The following procedure will enabled it.

.. warning:: Do this at your own risk! No guarantee it wont brick your NIC.

#. Find your ethernet controllers

   .. code-block:: bash

      sudo lspci | grep Ethernet

   .. image:: ./images/lspci-ethernet.png

#. Check your controllers capabilities

   .. code-block:: bash

      sudo lspci -v | less

      # Search for "0000:03:00.0"

   .. image:: ./images/eth-capabilities.png

   .. important:: In this example SR-IOV is enabled. No need to make any changes.

#. Check the offset bit

   .. code-block:: bash

      sudo ethtool --eeprom-dump enp3s0f0 offset 0x004a length 1

   .. note:: If SR-IOV is enabled this should be set to "01" my card was set to "F0".

#. Modify the offset bit to "1"

   .. code-block:: bash

      sudo ethtool --change-eeprom enp3s0f0 magic 0x15218086 offset 0x4a length 1 value 0x01

   .. warning:: If done wrong this could brick your interface.

