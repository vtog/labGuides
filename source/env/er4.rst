EdgeRouter 4
============

My home lab ISP is AT&T fiber which includes there standard GW. I have bypassed
this with an EdgeRouter 4 from Ubiquiti.

.. note:: AT&T assigns a /60 for home use.

IPv6
----

#. Configure IPv6 for vlan 1 (cli)

   .. code-block:: bash

      ssh vince@192.168.1.1

      configure

      edit interfaces ethernet eth0 vif 0

      set dhcpv6-pd pd 0 prefix-length /60
      set dhcpv6-pd pd 0 interface eth1 host-address ::1
      set dhcpv6-pd pd 0 interface eth1 prefix-id :0
      set dhcpv6-pd pd 0 interface eth1 service slaac

      commit
      save

#. Configure IPv6 for vlan 122 (cli)

   .. code-block:: bash

      ssh vince@192.168.1.1

      configure

      edit interfaces ethernet eth0 vif 0

      set dhcpv6-pd pd 0 interface eth1.122 host-address ::1
      set dhcpv6-pd pd 0 interface eth1.122 prefix-id :1
      set dhcpv6-pd pd 0 interface eth1.122 service slaac

      commit
      save

