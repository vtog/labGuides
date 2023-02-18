Enable SR-IOV on RHEL/KVM
=========================

For lab purposed I purchased an old Intel I350 SRIOV capable card. The steps
will guide you through configuring the VF's and passing them to KVM.

#. Discover hardware capabilities and confirm SRIOV support

   .. code-block:: bash

      sudo lshw -c network -businfo
      sudo lspci -vs 0000:03:00.0

#. Discover number of allowable VF's for each interface.

   .. code-block:: bash

      cat /sys/class/net/enp3s0f0/device/sriov_totalvfs
      cat /sys/class/net/enp3s0f1/device/sriov_totalvfs

#. Enable VF's. In my case I have two interfaces that support up to 7 VF's each.

   .. code-block:: bash

      sudo echo 7 > /sys/class/net/enp3s0f0/device/sriov_numvfs
      sudo echo 7 > /sys/class/net/enp3s0f1/device/sriov_numvfs

   .. important:: These changes will be lost upon reboot. Make them permanent
      by adding the lines to "/etc/rc.d/rc.local". Be sure to make "rc.local"
      executable.

#. Verify VF's are available.

   .. code-block:: bash

      lspci | grep Virtual

#. MAC addresses change between reboots. If needed you can configure a static
   MAC address for each VF.

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

   .. important:: These changes will be lost upon reboot. Make them permanent
      by adding the lines to "/etc/rc.d/rc.local". Be sure to make "rc.local"
      executable.

#. Verify new MAC address's

   .. code-block:: bash

      ip link show enp3s0f0
      ip link show enp3s0f1

