Additional OCP Networks (Multus)
================================

Demonstrate how to add interfaces for deployed containers. For a deeper
understanding see the official documentation:
`Multiple networks <https://docs.redhat.com/en/documentation/openshift_container_platform/4.19/html/multiple_networks/understanding-multiple-networks>`_

I found the following helpful as well:
`CNI Plugins <https://www.cni.dev/plugins/current/>`_

.. important:: At this time you can NOT create a service with this additional
   endpoint. Only the default Network IP / endpoint will be used.

User Defined Networks
---------------------

Network Attached Definitions
----------------------------

.. note:: I'm only focusing on MACVLAN, as I think this is the most common use
   case. There are other options and if I run across the need I will add them.

.. attention:: Do not use DHCP with IPVLAN. This will not work as interfaces
   share the MAC address with the host interface.

MACVLAN w/ Network DHCP
~~~~~~~~~~~~~~~~~~~~~~~

The DHCP CNI plugin uses the networks DHCP server to assign IP addr's to the
assigned interfaces.

#. Update the network operator with a "dhcp-shim".

   .. important:: When using network attachment definitions this "shim" is
      required for DHCP to properly work.

   A. Create the yaml patch

      .. code-block:: yaml

         cat << EOF > ./net-op-cluster-PATCH.yaml
         spec:
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
         EOF

   #. Apply the patch

      .. code-block:: bash

         oc patch networks.operator.openshift.io cluster --type merge \
           --patch-file ./net-op-cluster-PATCH.yaml

   #. Verify changes

      .. code-block:: bash

         oc get network-attachment-definitions -n default

#. Create the following Network Attachment Definition yaml file for the
   project / namespace.

   .. code-block:: yaml
      :emphasize-lines: 5,6,16

      cat << EOF > ./macvlan-dhcp.yaml
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
      EOF

   .. code-block:: bash

      oc create -f ./macvlan-dhcp.yaml

#. Add the annotation to the deployment.

   .. code-block:: bash

      oc patch deployment <deployment_name> -n <name_space> \
        --type merge -p '{"spec": {"template": {"metadata": {"annotations": \
        {"k8s.v1.cni.cncf.io/networks": "macvlan-dhcp"}}}}}'

MACVLAN w/ Whereabouts
~~~~~~~~~~~~~~~~~~~~~~

The Whereabouts CNI plugin allows the dynamic assignment of an IP address to an
additional network without the use of a network DHCP server.

#. Update the network operator with a "whereabouts-shim".

   .. important:: When using network attachment definitions this "shim" is
      required for whereabouts to properly work.

   A. Create the yaml patch

      .. code-block:: yaml

         cat << EOF > ./net-op-cluster-PATCH.yaml
         spec:
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
         EOF

   #. Apply the patch

      .. code-block:: bash

         oc patch networks.operator.openshift.io cluster --type merge \
           --patch-file ./net-op-cluster-PATCH.yaml

   #. Verify changes

      .. code-block:: bash

         oc get network-attachment-definitions -n default

#. Create the following Network Attachment Definition yaml file for the
   project.

   .. code-block:: yaml
      :emphasize-lines: 5,6,16

      cat << EOF > ./macvlan-whereabouts.yaml
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
      EOF

   .. code-block:: bash

      oc create -f ./macvlan-whereabouts.yaml

#. Add the annotation to the deployment.

   .. code-block:: bash

      oc patch deployment <deployment_name> -n <name_space> \
        --type merge -p '{"spec": {"template": {"metadata": {"annotations": \
        {"k8s.v1.cni.cncf.io/networks": "macvlan-whereabouts"}}}}}'

#. Check all ip reservations

   .. code-block:: bash

      oc get overlappingrangeipreservations.whereabouts.cni.cncf.io -A

MACVLAN w/ Static IP
~~~~~~~~~~~~~~~~~~~~

Statically allocate an IP for the container.

.. attention:: If the deployment has more than one pod, all the pods will be
   assigned the same IP.

#. Create the following Network Attachment Definition yaml file for the
   project.

   .. code-block:: yaml
      :emphasize-lines: 5,6,16

      cat << EOF > ./macvlan-static.yaml
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
      EOF

   .. code-block:: bash

      oc create -f ./macvlan-static.yaml

#. Add the annotation to the deployment.

   .. code-block:: bash

      oc patch deployment <deployment_name> -n <name_space> \
        --type merge -p '{"spec": {"template": {"metadata": {"annotations": \
        {"k8s.v1.cni.cncf.io/networks": "macvlan-static"}}}}}'
