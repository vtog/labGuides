Metal LB
========

Quick examples on configuring this operator. I'm assuming the operator is
installed.

#. From the OCP Console select :menuselection:`Operators --> OperatorHub`. In
   the search box type "metallb".

   .. image:: ./images/metallb-operatorhub.png

#. Click Install. Leave defaults and Click Install again.

   .. image:: ./images/metallb-install.png

   .. image:: ./images/metallb-install2.png

#. After operator installation completes, click "View Operator".

#. Click "Create instance" to create the Metal LB instance.

   .. image:: ./images/metallb-instance.png

#. Accept the defaults and click “Create” at the bottom of the page.

   .. image:: ./images/metallb-instance2.png

L2
--

.. tip:: To expose the VIP with a service see:
   `Quick App Deployment <./openshift-day2.html#quick-app-deployment-route>`_

   Here you'll find how to deploy a generic httpd service and expose a
   LoadBalancer Service.

#. Create the IP Address Pool

   .. code-block:: yaml

      cat << EOF | oc create -f -
      apiVersion: metallb.io/v1beta1
      kind: IPAddressPool
      metadata:
        name: ipaddrpool-v132
        namespace: metallb-system
      spec:
        addresses:
        - 192.168.132.225-192.168.132.229
      EOF

#. Create the L2 Advertisement

   .. code-block:: yaml

      cat << EOF | oc create -f -
      kind: L2Advertisement
      apiVersion: metallb.io/v1beta1
      metadata:
        name: l2-adv-v132
        namespace: metallb-system
      spec:
        ipAddressPools:
        - ipaddrpool-v132
      EOF

BGP
---

.. seealso:: `Edge Router 4 - BGP <../env/er4.html#bgp>`_

#. Create the IP Address Pool

   .. code-block:: yaml

      cat << EOF | oc create -f -
      apiVersion: metallb.io/v1beta1
      kind: IPAddressPool
      metadata:
        name: ipaddrpool-v245
        namespace: metallb-system
      spec:
        addresses:
        - 192.168.245.201-192.168.245.225
      EOF

#. Create the BGP Peer

   .. code-block:: yaml

      cat << EOF | oc create -f -
      kind: BGPPeer
      apiVersion: metallb.io/v1beta2
      metadata:
        name: bgp-peer-v245
        namespace: metallb-system
      spec:
        myASN: 64512
        peerASN: 64512
        peerAddress: 192.168.132.1
      EOF

#. Creat the BGP Advertisement

   .. code-block:: yaml

      cat << EOF | oc create -f -
      kind: BGPAdvertisement
      apiVersion: metallb.io/v1beta1
      metadata:
        name: bgp-adv-v245
        namespace: metallb-system
      spec:
        ipAddressPools:
        - ipaddrpool-v245
        peers:
        - bgp-peer-v245
      EOF
