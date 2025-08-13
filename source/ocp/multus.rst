Additional OCP Networks (Multus)
================================

Demonstrate how to add interfaces for deployed containers. For a deeper
understanding see the official documentation:
`Multiple networks <https://docs.redhat.com/en/documentation/openshift_container_platform/4.19/html/multiple_networks/understanding-multiple-networks>`_

I found the following helpful as well:
`CNI Plugins <https://www.cni.dev/plugins/current/>`_

.. important:: You can NOT use a ClusterIP service with these endpoints. Only
   the default Network IP can be exposed with a Route.

   For external access use NodePort and LoadBalancer service to expose the
   endpoint.

User Defined Networks
---------------------

Two new CRDs:

- Namespace scoped UserDefinedNetwork (UDN):
  Tenant owners who want to create a network that isolates their namespace
  from other namespaces.

- Cluster scoped ClusterUserDefinedNetwork (CUDN):
  Cluster administrator who want to join multiple namespaces as part of the
  same network.

Each of these CRDs has a field called **topology** which supports three
options:

- Layer3: OVN-Kubernetes will create a layer3 type logical network topology.
  Can be created as primary or secondary network roles for a pod.

- Layer2: OVN-Kubernetes will create a layer2 type logical network topology.
  Can be created as primary or secondary network roles for a pod.

- Localnet: OVN-Kubernetes will create a localnet type logical network
  topology. Can be created only as a secondary network role for a pod.

Each of these CRDs has a field called **role** which supports two options:

- Primary:
  The network will act as the primary network for the pod and all default
  traffic will pass through this interface.

- Secondary:
  The network will act as only a secondary network for the pod and only pod
  traffic that is part of the secondary network may be routed through this
  interface.

Namespace Scope
~~~~~~~~~~~~~~~

.. important:: Choose the topology and role that fits your needs. In my
   examples I'm using a **Primary Layer3** interface.

#. Create the namespace with the **mandatory label**.

   .. code-block:: yaml
      :emphasize-lines: 5,7

      cat << EOF | oc create -f -
      apiVersion: v1
      kind: Namespace
      metadata:
        name: udn1
        labels:
          k8s.ovn.org/primary-user-defined-network: ""
      EOF

#. Create a user defined network.

   .. code-block:: yaml
      :emphasize-lines: 3,5,6,8-10,12,13

      cat << EOF | oc create -f -
      apiVersion: k8s.ovn.org/v1
      kind: UserDefinedNetwork
      metadata:
        name: udn1
        namespace: udn1
      spec:
        topology: Layer3
        layer3:
          role: Primary
          subnets:
          - cidr: 10.100.0.0/16
            hostSubnet: 24
      EOF

Cluster Scope
~~~~~~~~~~~~~

.. important:: Choose the topology and role that fits your needs. In my
   examples I'm using a **Primary Layer3** interface.

#. Create one or more namespace's with the **mandatory label**.

   .. code-block:: yaml
      :emphasize-lines: 5,7,12,14

      cat << EOF | oc create -f -
      apiVersion: v1
      kind: Namespace
      metadata:
        name: udn1
        labels:
          k8s.ovn.org/primary-user-defined-network: ""
      ---
      apiVersion: v1
      kind: Namespace
      metadata:
        name: udn2
        labels:
          k8s.ovn.org/primary-user-defined-network: ""
      EOF

#. Create **Cluster** User Defined Network

   .. code-block:: yaml
      :emphasize-lines: 3,5,11,13-15,17,18

      cat << EOF | oc create -f -
      apiVersion: k8s.ovn.org/v1
      kind: ClusterUserDefinedNetwork
      metadata:
        name: cudn1
      spec:
        namespaceSelector:
          matchExpressions:
          - key: kubernetes.io/metadata.name
            operator: In
            values: ["udn1", "udn2"]
        network:
          topology: Layer3
          layer3:
            role: Primary
            subnets:
            - cidr: 10.200.0.0/16
              hostSubnet: 24
      EOF

Localnet Topology
~~~~~~~~~~~~~~~~~

.. warning:: **Unfinished - Work in Progress**

.. important:: For Localnet the **Role** must be **Secondary**.

#. Localnet

   .. code-block:: yaml
      :emphasize-lines: 3,5,11,13-15

      cat << EOF | oc create -f -
      apiVersion: k8s.ovn.org/v1
      kind: ClusterUserDefinedNetwork
      metadata:
        name: localnet1
      spec:
        namespaceSelector:
          matchExpressions:
          - key: kubernetes.io/metadata.name
            operator: In
            values: ["udn1", "udn2"]
        network:
          topology: Localnet
          localnet:
            role: Secondary
            physicalNetworkName: enp9s0
      EOF

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

      cat << EOF | oc create -f -
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

#. Add the annotation to the deployment.

   .. code-block:: bash

      oc patch deployment <deployment_name> -n <name_space> \
        --type merge --patch '{"spec": {"template": {"metadata": {"annotations": {"k8s.v1.cni.cncf.io/networks": "macvlan-dhcp"}}}}}'

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

      cat << EOF | oc create -f -
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

#. Add the annotation to the deployment.

   .. code-block:: bash

      oc patch deployment <deployment_name> -n <name_space> \
        --type merge --patch '{"spec": {"template": {"metadata": {"annotations": {"k8s.v1.cni.cncf.io/networks": "macvlan-whereabouts"}}}}}'

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

      cat << EOF | oc create -f -
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

#. Add the annotation to the deployment.

   .. code-block:: bash

      oc patch deployment <deployment_name> -n <name_space> \
        --type merge --patch '{"spec": {"template": {"metadata": {"annotations": {"k8s.v1.cni.cncf.io/networks": "macvlan-static"}}}}}'
