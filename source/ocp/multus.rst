Additional OCP Networks (Multus)
================================

Demonstrate how to add interfaces for deployed containers. For a deeper
understanding see the official documentation:
`Multiple networks <https://docs.openshift.com/container-platform/4.12/networking/multiple_networks/understanding-multiple-networks.html>`_

I found the following helpful as well:
`CNI Plugins <https://www.cni.dev/plugins/current/>`_

.. important:: At this time you can NOT create a service with this additional
   interface. Only the primary CNI interface will be used.

.. note:: I'm only focusing on MACVLAN, as I think this is the most common use
   case. There are other options and if I run across the need I will add them.

MACVLAN w/ Network DHCP
-----------------------

The DHCP CNI plugin uses the networks DHCP server to assign IP addr's to the
assigned interfaces.

#. Update the network operator with a "dhcp-shim". When using network
   attachment definitions this "shim" is required for DHCP to properly work.

   .. code-block:: bash

      oc edit networks.operator.openshift.io cluster

   Add the following to the "spec:" section

   .. code-block:: yaml

      additionalNetworks:
      - name: dhcp-shim
        namespace: default
        type: Raw
        rawCNIConfig: |-
          {
            "name": "dhcp-shim",
            "cniVersion": "0.3.1",
            "type": "bridge",
            "ipam": {
              "type": "dhcp"
            }
          }

#. Create the following Network Attachment Definition yaml file for the
   project.

   .. code-block:: yaml
      :emphasize-lines: 4,5,15

      apiVersion: k8s.cni.cncf.io/v1
      kind: NetworkAttachmentDefinition
      metadata:
        name: macvlan-dhcp
        namespace: httpd
      spec:
        config: |-
          {
            "cniVersion": "0.3.1",
            "name": "macvlan-dhcp",
            "type": "macvlan",
            "master": "enp9s0",
            "mode": "passthru",
            "ipam": {
              "type": "dhcp"
            }
          }

   .. code-block:: bash

      oc create -f macvlan-dhcp.yaml

#. Add the annotation to the deployment.

   .. code-block:: yaml
      :emphasize-lines: 5

      spec:
        template:
          metadata:
            annotations:
              k8s.v1.cni.cncf.io/networks: macvlan-dhcp

MACVLAN w/ Whereabouts
----------------------

The Whereabouts CNI plugin allows the dynamic assignment of an IP address to an
additional network without the use of a network DHCP server.

#. Update the network operator with a "whereabouts-shim". When using network
   attachment definitions this "shim" is required for whereabouts to properly
   work.

   .. code-block:: bash

      oc edit networks.operator.openshift.io cluster

   Add the following to the "spec:" section

   .. code-block:: yaml

      additionalNetworks:
      - name: whereabouts-shim
        namespace: default
        type: Raw
        rawCNIConfig: |-
          {
            "name": "whereabouts-shim",
            "cniVersion": "0.3.1",
            "type": "bridge",
            "ipam": {
              "type": "whereabouts"
            }
          }

#. Create the following Network Attachment Definition yaml file for the
   project.

   .. code-block:: yaml
      :emphasize-lines: 4,5,15

      apiVersion: k8s.cni.cncf.io/v1
      kind: NetworkAttachmentDefinition
      metadata:
        name: macvlan-whereabouts
        namespace: httpd
      spec:
        config: |-
          {
            "cniVersion": "0.3.1",
            "name": "macvlan-whereabouts",
            "type": "macvlan",
            "master": "enp9s0",
            "mode": "passthru",
            "ipam": {
              "type": "whereabouts",
              "range": "192.168.122.0/24",
              "range_start": "192.168.122.225",
              "range_end": "192.168.122.245",
              "gateway": "192.168.122.1",
              "routes": [
                { "dst": "0.0.0.0/0" }
              ]
            }
          }

#. Add the annotation to the deployment.

   .. code-block:: yaml
      :emphasize-lines: 5

      spec:
        template:
          metadata:
            annotations:
              k8s.v1.cni.cncf.io/networks: macvlan-whereabouts

MACVLAN w/ Static IP
--------------------

Statically allocate an IP for the container.

.. attention:: If the deployment has more than one pod, all the pods will be
   assigned the same IP.

#. Create the following Network Attachment Definition yaml file for the
   project.

   .. code-block:: yaml
      :emphasize-lines: 4,5,15

      apiVersion: k8s.cni.cncf.io/v1
      kind: NetworkAttachmentDefinition
      metadata:
        name: macvlan-static
        namespace: httpd
      spec:
        config: |-
          {
            "cniVersion": "0.3.1",
            "name": "macvlan-static",
            "type": "macvlan",
            "master": "enp9s0",
            "mode": "passthru",
            "ipam": {
              "type": "static",
              "addresses": [
                {
                "address": "192.168.122.245/24",
                "gateway": "192.168.122.1"
                }
              ],
              "routes": [
                { "dst": "0.0.0.0/0" }
              ]
            }
          }

#. Add the annotation to the deployment.

   .. code-block:: yaml
      :emphasize-lines: 5

      spec:
        template:
          metadata:
            annotations:
              k8s.v1.cni.cncf.io/networks: macvlan-static

