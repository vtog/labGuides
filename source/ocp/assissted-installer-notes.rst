Assissted Install Notes
=======================

The following are static network configurations when manually configuring
"Static IP, bridges, and bonds".

.. code-block:: yaml
   :caption: Ethernet Network Example
   :emphasize-lines: 2, 3, 5, 10, 17, 21, 22

   interfaces:
   - name: enp1s0
     type: ethernet
     state: up
     mtu: 9000
     ipv4:
       enabled: true
       dhcp: false
       address:
       - ip: 192.168.122.21
         prefix-length: 24
     ipv6:
       enabled: false
   dns-resolver:
     config:
       server:
       - 192.168.1.72
   routes:
     config:
     - destination: 0.0.0.0/0
       next-hop-address: 192.168.122.1
       next-hop-interface: enp1s0
       table-id: 254

.. code-block:: yaml
   :caption: VLAN-TAG Network Example
   :emphasize-lines: 2, 3, 5, 6, 7, 10, 11, 16, 23, 27, 28

   interfaces:
   - name: enp1s0
     type: ethernet
     state: up
     mtu: 9000
   - name: enp1s0.122
     type: vlan
     state: up
     vlan:
       base-iface: enp1s0
       id: 122
     ipv4:
       enabled: true
       dhcp: false
       address:
       - ip: 192.168.122.21
         prefix-length: 24
     ipv6:
       enabled: false
   dns-resolver:
     config:
       server:
       - 192.168.1.72
   routes:
     config:
     - destination: 0.0.0.0/0
       next-hop-address: 192.168.122.1
       next-hop-interface: enp1s0.122
       table-id: 254

.. code-block:: yaml
   :caption: Bond with VLAN-TAG Network Example
   :emphasize-lines: 2, 3, 5, 6, 7, 9, 10, 11, 16, 17, 18, 19, 22, 23, 28, 35, 39, 40

   interfaces:
   - name: enp1s0
     type: ethernet
     state: up
     mtu: 9000
   - name: enp1s1
     type: ethernet
     state: up
     mtu: 9000
   - name: bond0
     type: bond
     state: up
     link-aggregation:
       mode: active-backup
       port:
       - enp1s0
       - enp1s1
   - name: bond0.122
     type: vlan
     state: up
     vlan:
       base-iface: bond0
       id: 122
     ipv4:
       enabled: true
       dhcp: false
       address:
       - ip: 192.168.122.21
         prefix-length: 24
     ipv6:
       enabled: false
   dns-resolver:
     config:
       server:
       - 192.168.1.72
   routes:
     config:
     - destination: 0.0.0.0/0
       next-hop-address: 192.168.122.1
       next-hop-interface: bond0.122
       table-id: 254

.. code-block:: yaml
   :caption: KVM MAC/IP Mappings

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
   <host mac='52:54:00:f4:16:44' ip='192.168.122.44'/>
   <host mac='52:54:00:f4:16:45' ip='192.168.122.45'/>
   <host mac='52:54:00:f4:16:46' ip='192.168.122.46'/>
   <host mac='52:54:00:f4:16:47' ip='192.168.122.47'/>
   <host mac='52:54:00:f4:16:48' ip='192.168.122.48'/>
   <host mac='52:54:00:f4:16:49' ip='192.168.122.49'/>

