EdgeRouter 4
============

My home lab ISP is AT&T fiber which includes there standard GW. I have bypassed
this with an EdgeRouter 4 from Ubiquiti.

.. note:: AT&T assigns a /60 for home use.

IPv6
----

The following uses the CLI; SSH to ER4.

#. Configure IPv6 for WAN int eth0.0 and eth1

   .. code-block:: bash

      ssh vince@192.168.1.1

      configure

      edit interfaces ethernet eth0 vif 0

      set dhcpv6-pd pd 0 prefix-length /60
      set dhcpv6-pd pd 0 interface eth1 host-address ::1
      set dhcpv6-pd pd 0 interface eth1 prefix-id :0
      set dhcpv6-pd pd 0 interface eth1 service slaac

      commit ; save ; exit

#. Configure IPv6 for WAN int eth0.0 and eth1 vlan 122

   .. code-block:: bash

      ssh vince@192.168.1.1

      configure

      edit interfaces ethernet eth0 vif 0

      set dhcpv6-pd pd 0 interface eth1.122 host-address ::1
      set dhcpv6-pd pd 0 interface eth1.122 prefix-id :1
      set dhcpv6-pd pd 0 interface eth1.122 service slaac

      commit ; save ; exit

BGP
---

The following uses the CLI; SSH to ER4.

#. Configure BGP for use with OCP MetalLB

   .. code-block:: bash

      ssh vince@192.168.1.1                                  
                                                             
      configure

      set protocols bgp 64512
      set protocols bgp 64512 peer-group ovn_ocp
      set protocols bgp 64512 peer-group ovn_ocp remote-as 64512
      set protocols bgp 64512 peer-group ovn_ocp soft-reconfiguration inbound
      set protocols bgp 64512 neighbor 192.168.132.11 peer-group ovn_ocp
      set protocols bgp 64512 neighbor 192.168.132.12 peer-group ovn_ocp
      set protocols bgp 64512 neighbor 192.168.132.13 peer-group ovn_ocp

      commit ; save ; exit

#. Show BGP

   .. code-block:: bash

      ssh vince@192.168.1.1

      show ip bgp
      show ip bgp summary
      show ip bgp neighbors 192.168.132.11 advertised-routes
      show ip bgp neighbors 192.168.132.11 received-routes
