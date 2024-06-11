Advanced Cluster Management
===========================

Install ACM
-----------

Basic ACM install to get started.

.. tip:: Be sure to have enough cpu, memory, and storage. My lab is KVM based.
   For ACM I start with a three node cluster, each node has 16 cores, 32G
   memory, and small 600G ODF/Ceph deployment.

#. From the OCP Console select Operators --> OperatorHub. In the search box
   type "acm".

   .. image:: ./images/acm-operatorhub.png

#. Click Install.

   .. image:: ./images/acm-install.png

#. After install completes, open the newly installed operator. Select
   MultiClusterHub tab and click "Create MultiClusterHub".

   .. image:: ./images/acm-multiclusterhub.png

#. Accept the defaults and click "Create".

   .. image:: ./images/acm-create-multiclusterhub.png

#. Be patient several containers are pulled and started. You can monitor the
   progress by watching the pods in the namespace "multicluster-engine".

   .. code-block:: bash

      oc get pods -n multicluster-engine

Basic Config
------------

Add Host Inventory
------------------

To add hosts to the "Host Inventory" use the following script and CSV file.
Together it creates three objects in the "output" directory.

- Secret
- NMStateConfig
- BareMetalHost

#. Create the following CSV file for your environment.

   .. attention:: In this CSV file example I have 5 VM's. I'm using Sushi Redfish
      emulater for remote management.

   .. code-block:: bash

      HOSTNAME,DRAC-IP,NODE-IP,ETH0,UUID
      host11,192.168.1.72:8000,192.168.122.11,52:54:00:f4:16:11,0ef41f53-b22b-4809-a8e4-6fd76b1385af
      host12,192.168.1.72:8000,192.168.122.12,52:54:00:f4:16:12,9ccd79b0-d21c-494d-a51a-8d08a371cc8f
      host13,192.168.1.72:8000,192.168.122.13,52:54:00:f4:16:13,8ac8719f-12fc-43e9-a04c-e3647af877f9
      host14,192.168.1.72:8000,192.168.122.14,52:54:00:f4:16:14,d3386573-afed-4958-a2ab-2d7f3d68c69d
      host15,192.168.1.72:8000,192.168.122.15,52:54:00:f4:16:15,16d40706-3939-497a-afa0-4ec83ae152a8

#. Create the following script.

   .. important:: You may need to change or add variables for your environment.

   .. code-block:: bash
      :linenos:
      :emphasize-lines: 28,30,31,39,42-45,48,66,88,91,96-98,102,103,105

      #/bin/bash

      # Create output dir if not exists, delete old one if exists.

      if [[ -d output ]]; then
          rm -rf output
          mkdir -p output
      else
          mkdir -p output
      fi

      # Take "nodes" CSV and create bare-metal resources for cluster.

      for host in `cat nodes | grep -v HOSTNAME | awk -F "," '{print $1}'`; do
      HOST=`grep $host nodes | awk -F "," '{print $1}'`;
      BMCIP=`grep $host nodes | awk -F "," '{print $2}'`;
      HOSTIP=`grep $host nodes | awk -F "," '{print $3}'`;
      MAC1=`grep $host nodes | awk -F "," '{print $4}'`;
      UUID=`grep $host nodes | awk -F "," '{print $5}'`;

      # Secret

      cat <<EOF > ./output/$HOST-secret.yaml
      apiVersion: v1
      data:
        password: a25p
        username: a25p
      kind: Secret
      metadata:
        name: bmc-$HOST
        namespace: lablocal
      type: Opaque
      EOF

      # NMStateConfig

      cat <<EOF > ./output/$HOST-nmstate.yaml
      apiVersion: agent-install.openshift.io/v1beta1
      kind: NMStateConfig
      metadata:
        labels:
          agent-install.openshift.io/bmh: $HOST
          infraenvs.agent-install.openshift.io: lablocal
        name: $HOST
        namespace: lablocal
      spec:
        interfaces:
          - macAddress: $MAC1
            name: enp1s0
        config:
          interfaces:
            - name: enp1s0
              type: ethernet
              mtu: 9000
              state: up
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
                  - ip: $HOSTIP
                    prefix-length: 24
              ipv6:
                enabled: false
          dns-resolver:
            config:
              search:
                - lab.local
              server:
                - 192.168.1.68
          routes:
            config:
              - destination: 0.0.0.0/0
                next-hop-address: 192.168.122.1
                next-hop-interface: enp1s0.122
                table-id: 254
      EOF

      # BareMetalHost

      cat <<EOF > ./output/$HOST-baremetal.yaml
      apiVersion: metal3.io/v1alpha1
      kind: BareMetalHost
      metadata:
        annotations:
          bmac.agent-install.openshift.io/hostname: $HOST
          inspect.metal3.io: ""
        finalizers:
          - baremetalhost.metal3.io
        labels:
          infraenvs.agent-install.openshift.io: lablocal
        name: $HOST
        namespace: lablocal
      spec:
        automatedCleaningMode: disabled
        bmc:
          address: redfish-virtualmedia+http://$BMCIP/redfish/v1/Systems/$UUID
          credentialsName: bmc-$HOST
          disableCertificateVerification: true
        bootMACAddress: $MAC1
        customDeploy:
          method: start_assisted_install
        online: true
      EOF

      done;

      echo -e "\n\nTo create the inventory run \"oc create -f output/\"."
