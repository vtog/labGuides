Assissted Install Notes
=======================

Using the following simple templates to get started with AI. These can be
dropped in via the UI.

#. Static network configuration

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

#. MAC / IP mappings

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
     <host mac='52:54:00:f4:16:31' ip='192.168.122.31'/>
     <host mac='52:54:00:f4:16:32' ip='192.168.122.32'/>
     <host mac='52:54:00:f4:16:33' ip='192.168.122.33'/>
     <host mac='52:54:00:f4:16:34' ip='192.168.122.34'/>
     <host mac='52:54:00:f4:16:35' ip='192.168.122.35'/>
     <host mac='52:54:00:f4:16:36' ip='192.168.122.36'/>
     <host mac='52:54:00:f4:16:37' ip='192.168.122.37'/>
     <host mac='52:54:00:f4:16:38' ip='192.168.122.38'/>
     <host mac='52:54:00:f4:16:39' ip='192.168.122.39'/>

