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
       search:
       - lab.local
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
       search:
       - lab.local
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
       search:
       - lab.local
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

   <host mac='52:54:00:f4:16:10' ip='192.168.122.10'/>
   <host mac='52:54:00:f4:16:11' ip='192.168.122.11'/>
   <host mac='52:54:00:f4:16:12' ip='192.168.122.12'/>
   <host mac='52:54:00:f4:16:13' ip='192.168.122.13'/>
   <host mac='52:54:00:f4:16:14' ip='192.168.122.14'/>
   <host mac='52:54:00:f4:16:15' ip='192.168.122.15'/>
   <host mac='52:54:00:f4:16:16' ip='192.168.122.16'/>
   <host mac='52:54:00:f4:16:17' ip='192.168.122.17'/>
   <host mac='52:54:00:f4:16:18' ip='192.168.122.18'/>
   <host mac='52:54:00:f4:16:19' ip='192.168.122.19'/>
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

