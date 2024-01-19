KVM Install Notes
=================

#. Tagging on the **Guest**. Create the following file.

   .. note:: In this example a **bridge** interface needs to be created on the
      **host** first. The network is configured with trunked ports.

   .. code-block:: xml

      <network>
        <name>br-enp3s0f0</name>
        <forward mode="bridge"/>
        <bridge name="br-enp3s0f0"/>
      </network>

   .. attention:: When creating the VM a single network interface is added. Be
      sure to add the VLAN interfaces to the **guest** after booting.

   .. warning:: Adding VLAN interfaces to the **host** will prevent the
      **guest** from seeing the VLAN.

#. Tagging on the **Host**. Create the following file.

   .. note:: In this example there are two VLANs, 122 & 132. Both **VLAN**
      intefaces need to be created on the **host** first. The network is
      configured with trunked ports.

   .. code-block:: xml

      <network>
        <name>macvtap-net</name>
        <forward mode="bridge">
          <interface dev="enp3s0f0.122"/>
          <interface dev="enp3s0f0.132"/>
        </forward>
      </network>

   .. attention:: When creating the VM add two network interfaces. Each will be
      on their respective VLAN.

#. Run the following commands to create the new network. This procedure is the
   same regardless of tagging option choosen in previous steps.

   .. code-block:: bash

      sudo virsh net-define <name>.xml
      sudo virsh net-autostart <name>
      sudo virsh net-start <name>

#. Default network (Forward mode = open). Default virtual bridge for
   non-trunked interfaces.

   .. code-block:: xml

      <network>
        <name>default</name>
        <forward mode='open'/>
        <bridge name='virbr0' stp='on' delay='0'/>
        <mtu size='9000'/>
        <mac address='52:54:00:7b:e0:da'/>
        <domain name='lab.local' localOnly='yes'/>
        <dns>
          <host ip='192.168.122.1'>
            <hostname>gateway</hostname>
          </host>
        </dns>
        <ip address='192.168.122.1' netmask='255.255.255.0'>
          <dhcp>
            <range start='192.168.122.200' end='192.168.122.249'/>
            <host mac='52:54:00:ea:5f:8b' ip='192.168.122.8'/>
            <host mac='52:54:00:1e:58:c8' ip='192.168.122.9'/>
            <host mac='52:54:00:f4:16:20' ip='192.168.122.20'/>
            <host mac='52:54:00:f4:16:21' ip='192.168.122.21'/>
            <host mac='52:54:00:f4:16:22' ip='192.168.122.22'/>
            <host mac='52:54:00:f4:16:23' ip='192.168.122.23'/>
            <host mac='52:54:00:f4:16:24' ip='192.168.122.24'/>
            <host mac='52:54:00:f4:16:25' ip='192.168.122.25'/>
            <host mac='52:54:00:f4:16:26' ip='192.168.122.26'/>
            <host mac='52:54:00:f4:16:27' ip='192.168.122.27'/>
            <host mac='52:54:00:f4:16:28' ip='192.168.122.28'/>
            <host mac='52:54:00:f4:16:29' ip='192.168.122.29'/>
            <host mac='52:54:00:f4:16:30' ip='192.168.122.30'/>
            <host mac='52:54:00:f4:16:31' ip='192.168.122.31'/>
            <host mac='52:54:00:f4:16:32' ip='192.168.122.32'/>
            <host mac='52:54:00:f4:16:33' ip='192.168.122.33'/>
            <host mac='52:54:00:f4:16:34' ip='192.168.122.34'/>
            <host mac='52:54:00:f4:16:35' ip='192.168.122.35'/>
            <host mac='52:54:00:f4:16:36' ip='192.168.122.36'/>
            <host mac='52:54:00:f4:16:37' ip='192.168.122.37'/>
            <host mac='52:54:00:f4:16:38' ip='192.168.122.38'/>
            <host mac='52:54:00:f4:16:39' ip='192.168.122.39'/>
            <host mac='52:54:00:f4:16:40' ip='192.168.122.40'/>
            <host mac='52:54:00:f4:16:41' ip='192.168.122.41'/>
            <host mac='52:54:00:f4:16:42' ip='192.168.122.42'/>
            <host mac='52:54:00:f4:16:43' ip='192.168.122.43'/>
            <host mac='52:54:00:f4:16:44' ip='192.168.122.46'/>
            <host mac='52:54:00:f4:16:45' ip='192.168.122.45'/>
            <host mac='52:54:00:f4:16:46' ip='192.168.122.46'/>
            <host mac='52:54:00:f4:16:47' ip='192.168.122.47'/>
            <host mac='52:54:00:f4:16:48' ip='192.168.122.48'/>
            <host mac='52:54:00:f4:16:49' ip='192.168.122.49'/>
            <host mac='52:54:00:f4:16:50' ip='192.168.122.50'/>
          </dhcp>
        </ip>
      </network>
