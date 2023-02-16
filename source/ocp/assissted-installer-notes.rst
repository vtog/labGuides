Assissted Install Notes
=======================

The following are notes on deploying OCP with the console AI.

#. AI console simple network config

   .. code-block:: yaml

      dns-resolver:
        config:
          server:
          - 192.168.122.1
      interfaces:
      - name: enp1s0
        ipv4:
          address:
          - ip: 192.168.122.21
            prefix-length: 24
          dhcp: false
          enabled: true
        ipv6:
          enabled: false    
        state: up
        type: ethernet
        mtu: 9000
      routes:
        config:
        - destination: 0.0.0.0/0
          next-hop-address: 192.168.122.1
          next-hop-interface: enp1s0
          table-id: 254

#. AI console bonded network config

   .. code-block:: yaml

      dns-resolver:
        config:
          server:
          - 192.168.122.1
      interfaces:
      - name: bond0
        ipv4:
          address:
          - ip: 192.168.122.21
            prefix-length: 24
          dhcp: false
          enabled: true
        ipv6:
          enabled: false
        link-aggregation:
          mode: active-backup
          port:
          - enp1s0
          - enp1s1
        state: up
        type: bond
        mtu: 9000
      routes:
        config:
        - destination: 0.0.0.0/0
          next-hop-address: 192.168.122.1
          next-hop-interface: bond0
          table-id: 254

#. AI console bonded-vlan network config

   .. code-block:: yaml

      dns-resolver:
        config:
          server:
          - 192.168.122.1
      interfaces:
      - name: bond0
        link-aggregation:
          mode: active-backup
          port:
          - enp1s0
          - enp1s1
        state: up
        type: bond
        mtu: 9000
      - name: bond0.302
        ipv4:
          address:
          - ip: 192.168.122.21
            prefix-length: 24
          dhcp: false
          enabled: true
        ipv6:
          enabled: false
        state: up
        type: vlan
        vlan:
          base-iface: bond0
          id: 302
      routes:
        config:
        - destination: 0.0.0.0/0
          next-hop-address: 192.168.122.1
          next-hop-interface: bond0.302
          table-id: 254

#. KVM MAC/IP mappings

   .. code-block:: yaml

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

