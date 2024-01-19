Assisted Install Notes
=======================

Prerequisites
-------------

Before starting have a naming and IP plan. The following is based on static IP.

- Cluster name; ex. ocp1
- Base domain; ex. lab.local
- Have each Nodes primary interface Name and MAC Address.
- Static IP

  - Each node an assigned IP
  - API VIP (assigned to the DNS Record)
  - Ingress VIP (assigned to the DNS Record)

- DNS Records

  - api.ocp1.lab.local.
  - api-int.ocp1.lab.local.
  - \*.apps.ocp1.lab.local.
  - "A" records for each host/node
  - "PTR" records for each host/node

Method of Procedure
-------------------

#. Connect to https://console.redhat.com/openshift/overview and authenticate.

#. Select "Create Cluster"

   .. image:: ./images/console-redhat.png

#. Click the "Datacenter" tab and click "Create Cluster". This starts the
   Assisted Intaller.

   .. image:: ./images/create-cluster.png

#. **Cluster details**

   - Cluster name
   - Base domain
   - OpenShift version
   - Hosts' network configuration

   .. important:: Be sure to select "StaticIP, bridges, and bonds". This option
      allows for a custom network config with the deployment.

   .. image:: ./images/cluster-details.png

   Click "Next" when ready.

#. **Static network configurations**

   A. Select "YAML view" and click "Start from scratch".

      .. image:: ./images/cluster-network.png

   #. For each host add the Network(yaml), MAC address and Interface name.

      .. note:: Several examples are included below, :ref:`Static Network
         Examples <netconf>`

      .. attention:: Each interface in use should be defined here.

      .. image:: ./images/cluster-network-config.png

   #. Click "Next" when ready.

#. **Operators**

   - Leave the defaults (Nothing selected)
   - Click "Next".

   .. image:: ./images/cluster-operators.png

#. **Host discovery**

   A. Click "Add hosts"

      .. image:: ./images/cluster-addhosts.png

      - Set Provisioning type = "Full image file - Download a self-contained ISO"

      - Add the "SSH public key"

      - If required set "proxy settings"

        .. image:: ./images/cluster-addhosts2.png

      - Click "Generate Discovery ISO" when ready.

   #. Download Discovery ISO

   #. Boot hosts from ISO

   #. Wait for hosts to be discovered.

      .. note:: At least three hosts are required to move forward.

      .. image:: ./images/cluster-hosts.png

   #. If needed adjust Hostname and Role.

      .. image:: ./images/cluster-hosts-disovered.png

   #. Click "Next".

#. **Storage**

   - If needed adjust hosts target storage device for install.
   - Click "Next".

#. **Networking**

   - Add "API IP"
   - Add "Ingress IP"
   - Click "Next"

   .. image:: ./images/cluster-networking.png

#. **Review and create**

   - Review Cluster summary
   - Click "Install cluster"
   - You can view the progress by watching the "Host inventory" and clicking
     "View cluster events"

   .. image:: ./images/cluster-install.png

   .. important:: Be sure to "Download kubeconfig" and Save "kubeadmin Password"

      .. image:: ./images/cluster-access.png

.. _netconf:

Static Network Examples
-----------------------

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