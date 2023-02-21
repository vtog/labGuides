Enable SR-IOV on RHEL/KVM
=========================

For lab purposed I purchased an old Intel I350 SRIOV capable card. The steps
will guide you through configuring the VF's and passing them to KVM.

#. Discover hardware capabilities and confirm SRIOV support

   .. code-block:: bash

      sudo lshw -c network -businfo

   .. image:: ./images/sriov-devices.png

   .. code-block:: bash

      sudo lspci -vs 0000:03:00.0

   .. image:: ./images/sriov-capable.png

#. Discover number of allowable VF's for each interface.

   .. code-block:: bash

      cat /sys/class/net/enp3s0f0/device/sriov_totalvfs
      cat /sys/class/net/enp3s0f1/device/sriov_totalvfs

#. Enable VF's. In my case I have two interfaces and in the previous step I
   discoverd that each support up to 7 VF's.

   .. code-block:: bash

      echo 7 | sudo tee /sys/class/net/enp3s0f0/device/sriov_numvfs
      echo 7 | sudo tee /sys/class/net/enp3s0f1/device/sriov_numvfs

   .. attention:: These changes will be lost upon reboot. Make them permanent
      by adding the lines to "/etc/rc.d/rc.local". You can remove "sudo" from
      each line. Be sure to make "rc.local" executable.

#. Verify VF's are available.

   .. code-block:: bash

      sudo lshw -c network -businfo

   .. image:: ./images/sriov-verify.png

#. MAC addresses change between reboots. If needed you can configure a static
   MAC address for each VF. I used the previous information for the last three
   octets.

   .. code-block:: bash

      sudo ip link set enp3s0f0 vf 0 mac 52:54:00:03:10:00
      sudo ip link set enp3s0f0 vf 1 mac 52:54:00:03:10:04
      sudo ip link set enp3s0f0 vf 2 mac 52:54:00:03:11:00
      sudo ip link set enp3s0f0 vf 3 mac 52:54:00:03:11:04
      sudo ip link set enp3s0f0 vf 4 mac 52:54:00:03:12:00
      sudo ip link set enp3s0f0 vf 5 mac 52:54:00:03:12:04
      sudo ip link set enp3s0f0 vf 6 mac 52:54:00:03:13:00

      sudo ip link set enp3s0f1 vf 0 mac 52:54:00:03:10:01
      sudo ip link set enp3s0f1 vf 1 mac 52:54:00:03:10:05
      sudo ip link set enp3s0f1 vf 2 mac 52:54:00:03:11:01
      sudo ip link set enp3s0f1 vf 3 mac 52:54:00:03:11:05
      sudo ip link set enp3s0f1 vf 4 mac 52:54:00:03:12:01
      sudo ip link set enp3s0f1 vf 5 mac 52:54:00:03:12:05
      sudo ip link set enp3s0f1 vf 6 mac 52:54:00:03:13:01

   .. attention:: These changes will be lost upon reboot. Make them permanent
      by adding the lines to "/etc/rc.d/rc.local". You can remove "sudo" from
      each line. Be sure to make "rc.local" executable.

#. Verify new MAC address's

   .. code-block:: bash

      ip link show enp3s0f0
      ip link show enp3s0f1

.. important:: For OCP VM instructions see 
   `Enable SR-IOV on OCP VM <../ocp/sriov.html>`_
