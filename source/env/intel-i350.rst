Enable SR-IOV on Intel I350
===========================

I bought this card on eBay and it turns out different manufacturer's disable the
SR-IOV feature. The following procedure will enabled it.

.. warning:: Do this at your own risk! No guarantee it wont brick your NIC.

#. Find your ethernet controllers

   .. code-block:: bash

      sudo lshw -c network -businfo

   .. image:: ./images/lspci-ethernet.png

#. Check your controllers capabilities

   .. code-block:: bash

      sudo lspci -vs 0000:03:00.0

   .. image:: ./images/eth-capabilities.png

   .. attention:: In this example SR-IOV is enabled. No need to make any changes.

#. Check the offset bit

   .. code-block:: bash

      sudo ethtool --eeprom-dump enp3s0f0 offset 0x004a length 1

   .. note:: If SR-IOV is enabled this should be set to something other than
      zero my card was set to "F0" (Disabled).

#. Modify the offset bit based on the number supported VF's. The i350 supports
   up to 8. I set mine to 7 based another card that was configured with 7.

   .. code-block:: bash

      sudo ethtool --change-eeprom enp3s0f0 magic 0x15218086 offset 0x4a length 1 value 0xF7

   .. warning:: If done wrong this could brick your interface.

#. Reboot and check total allowable VF's. Should now show 7 for each interface.

   .. code-block:: bash

      cat /sys/class/net/enp3s0f0/device/sriov_totalvfs
      cat /sys/class/net/enp3s0f1/device/sriov_totalvfs

