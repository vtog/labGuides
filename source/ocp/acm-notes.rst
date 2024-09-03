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

Simple config to get started. The following steps will create the following
objects:

- Credentials
- Host inventory settings
- Infrastructure environment

Credentials
~~~~~~~~~~~

#. From the CLI create a new project/namespace for your spoke cluster objects.

   .. code-block:: bash

      oc new-project <project_name>

#. Connect to the console and switch from "local-cluster" to "All Clusters".

   .. image:: ./images/acm-allclusters.png

#. Configure credentials. Select "Credentials" then click "Add credentials".

   .. image:: ./images/acm-credentials.png

#. Select Credential Type. In my lab/example I'm using Host Inventory.

   .. image:: ./images/acm-host-inventory.png

#. Enter the basic credential information and click Next.

   .. image:: ./images/acm-basic-info.png

#. Add your "Pull secret" and "SSH public key" and click Next.

   .. note:: If disconnected environment be sure to include/add your on-prem
      registry / mirror credentials.

   .. image:: ./images/acm-pull-secret.png

#. Review and click Add.

Host inventory (Connected)
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. From the console go to Infrastructure --> Host Inventory. Click "Configure
   host inventory settings".

   .. image:: ./images/acm-host-inventory-settings.png

#. Configure host inventory settings and click "Configure".

   .. warning:: For disconnected environments skip to next step.

   .. image:: ./images/acm-configure-host-inventory.png

   .. attention:: Be patient this process will take some time. For a connected
      environment several images need to be pulled down. You can monitor this
      process with the following commands. Wait for the pod to fully start.

      .. code-block:: bash

         oc get pod assisted-image-service-0 -n multicluster-engine

         oc logs assisted-image-service-0 -n multicluster-engine -f

#. Patch the provisioning to watch all name spaces.

   .. code-block:: bash

      oc patch provisioning provisioning-configuration --type merge -p '{"spec":{"watchAllNamespaces": true }}'

Host inventory (Disconnected)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From your terminal:

1. Create the following configmap referencing your disconnected registry.

   .. important:: In my lab I found the following four references were
      required. Your environment may require others. I plan on manually
      adding the other operators/registries post install.

   .. code-block:: yaml
      :emphasize-lines: 4,10-12,17,20,23,26,29,32,35,38

      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: assisted-installer-mirror-config
        namespace: multicluster-engine
        labels:
          app: assisted-service
      data:
        ca-bundle.crt: |
          -----BEGIN CERTIFICATE-----
          <Use rootCA.pem from your mirror registry here>
          -----END CERTIFICATE-----
        registries.conf: |
          unqualified-search-registries = ["registry.access.redhat.com", "docker.io"]
          [[registry]]
             prefix = ""
             location = "quay.io/openshift-release-dev/ocp-v4.0-art-dev"
             mirror-by-digest-only = true
             [[registry.mirror]]
             location = "mirror.lab.local:8443/openshift/release"
          [[registry]]
             prefix = ""
             location = "quay.io/openshift-release-dev/ocp-release"
             mirror-by-digest-only = true
             [[registry.mirror]]
             location = "mirror.lab.local:8443/openshift/release-images"
          [[registry]]
             prefix = ""
             location = "registry.redhat.io/multicluster-engine"
             mirror-by-digest-only = true
             [[registry.mirror]]
             location = "mirror.lab.local:8443/multicluster-engine"
          [[registry]]
             prefix = ""
             location = "registry.redhat.io/rhacm2"
             mirror-by-digest-only = true
             [[registry.mirror]]
             location = "mirror.lab.local:8443/rhacm2"

#. Apply the newly created file.

   .. code-block:: bash

      oc apply -f assisted-installer-mirror-config.yaml

#. Before creating the agent service config we need to identify the variables
   for each version of OCP you plan on deploying. This information will be
   included in the osImages section of the AgentServiceConfig (Host environment
   settings).

   a. Obtain the RHCOS ISO and RootFS IMG from:
      `mirror.openshift.com <https://mirror.openshift.com/pub/openshift-v4/dependencies/rhcos/>`_

      .. important:: Each OCP version may have more then one option. The
         version you plan to deploy will dictate which version to download.
         For example 4.15. If 4.15.22 or lower select 4.15.0. For 4.15.23
         and higher select the 4.15.23. In my case I need both.

         .. image:: ./images/mirror-openshift-415.png

   #. Set the environment variables

      .. code-block:: bash

         OCP_VERSION=4.15.14
         ARCH=x86_64

   #. If needed download the version specific openshift installer.

      .. code-block:: bash

         curl -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$OCP_VERSION/openshift-install-linux.tar.gz -o openshift-install-linux-$OCP_VERSION.tar.gz

   #. Extract the installer.

      .. code-block:: bash

         tar -xzvf openshift-install-linux-$OCP_VERSION.tar.gz
         mv openshift-install openshift-install-$OCP_VERSION
         rm README.md

   #. Extract the RHCOS Live Version. Save this info for next step.

      .. code-block:: bash

         ./openshift-install-$OCP_VERSION coreos print-stream-json | grep location | grep $ARCH | grep iso | cut -d\/ -f10

   #. Repeat steps a - e for each version.

#. Create the AgentServiceConfig with reference to the config map created in
   step A. Adjust your storage requirements as needed, I'm using default
   values. Add each osImage you plan on deploying for spoke clusters. The
   version information from last step will be used here.

   .. code-block:: yaml
      :emphasize-lines: 11,17,23,25,27-41

      apiVersion: agent-install.openshift.io/v1beta1
      kind: AgentServiceConfig
      metadata:
       name: agent
      spec:
        databaseStorage:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 10Gi
        filesystemStorage:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 100Gi
        imageStorage:
          accessModes:
          - ReadWriteOnce
          resources:
            requests:
              storage: 50Gi
        mirrorRegistryRef:
          name: assisted-installer-mirror-config
        osImages:
          - openshiftVersion: "4.15"
            cpuArchitecture: "x86_64"
            version: "415.92.202402201450-0"
            url: "http://192.168.1.72/rhcos/rhcos-4.15.0-x86_64-live.x86_64.iso"
            rootFSUrl: "http://192.168.1.72/rhcos/rhcos-4.15.0-x86_64-live-rootfs.x86_64.img"
          - openshiftVersion: "4.15"
            cpuArchitecture: "x86_64"
            version: "415.92.202407091355-0"
            url: "http://192.168.1.72/rhcos/rhcos-4.15.23-x86_64-live.x86_64.iso"
            rootFSUrl: "http://192.168.1.72/rhcos/rhcos-4.15.23-x86_64-live-rootfs.x86_64.img"
          - openshiftVersion: "4.16"
            cpuArchitecture: "x86_64"
            version: "416.94.202406251923-0"
            url: "http://192.168.1.72/rhcos/rhcos-4.16.3-x86_64-live.x86_64.iso"
            rootFSUrl: "http://192.168.1.72/rhcos/rhcos-4.16.3-x86_64-live-rootfs.x86_64.img"

#. Apply the agent service config yaml to the cluster.

   .. code-block:: bash

      oc apply -f agentserviceconfig.yaml

   .. attention:: Each iso and img defined in the osImages section will be
      download to the cluster. You can monitor this process with the following
      commands. Wait for the pod to fully start.

      .. code-block:: bash

         oc get pod assisted-image-service-0 -n multicluster-engine

         oc logs assisted-image-service-0 -n multicluster-engine -f

#. Patch the provisioning to watch all name spaces.

   .. code-block:: bash

      oc patch provisioning provisioning-configuration --type merge -p '{"spec":{"watchAllNamespaces": true }}'

#. Create the ClusterImageSet for each hosted version of openshift. In my
   example I'm hosting 4.15.14, 4.15.28 and 4.16.8. Save the file and apply
   to cluster "oc apply -f clusterimageset.yaml".

   .. note:: I'm including all three in one file but three ClusterImageSet's
      are created.

   .. code-block:: yaml
      :emphasize-lines: 2,7,9,12,17,19,22,27,29

      apiVersion: hive.openshift.io/v1
      kind: ClusterImageSet
      metadata:
        labels:
          channel: stable
          visible: 'true'
        name: img4.15.14-x86-64-appsub
      spec:
        releaseImage: mirror.lab.local:8443/openshift/release-images:4.15.14-x86_64
      ---
      apiVersion: hive.openshift.io/v1
      kind: ClusterImageSet
      metadata:
        labels:
          channel: stable
          visible: 'true'
        name: img4.15.28-x86-64-appsub
      spec:
        releaseImage: mirror.lab.local:8443/openshift/release-images:4.15.28-x86_64
      ---
      apiVersion: hive.openshift.io/v1
      kind: ClusterImageSet
      metadata:
        labels:
          channel: stable
          visible: 'true'
        name: img4.16.8-x86-64-appsub
      spec:
        releaseImage: mirror.lab.local:8443/openshift/release-images:4.16.8-x86_64

Infrastructure environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. From the console go to Infrastructure --> Host Inventory. Click "Create
   infrastructure environment.

   .. image:: ./images/acm-infra-env.png

#. Enter the information for your infrastructure environment. Click "Create"
   when finished.

   .. note:: Use the previously created credentials in the "Infrastructure
      provider credentials" drop down list.

   .. image:: ./images/acm-create-infra-env.png

Add Host Inventory
------------------

To add hosts to the "Host Inventory" use the following script and CSV file.
Together it creates three objects in the "output" directory.

.. tip:: When removing these objects be sure to do it via the console. Doing
   so via the cli will leave orphaned objects.

- Secret
- NMStateConfig
- BareMetalHost

#. Create the following CSV file for your environment.

   .. attention:: In this CSV file example I have 5 VM's. I'm using Sushi Redfish
      emulater for remote management.

   .. code-block:: bash

      HOST,BMCIP,HOSTIP,MAC1,UUID
      host11,192.168.1.72:8000,192.168.122.11,52:54:00:f4:16:11,0ef41f53-b22b-4809-a8e4-6fd76b1385af
      host12,192.168.1.72:8000,192.168.122.12,52:54:00:f4:16:12,9ccd79b0-d21c-494d-a51a-8d08a371cc8f
      host13,192.168.1.72:8000,192.168.122.13,52:54:00:f4:16:13,8ac8719f-12fc-43e9-a04c-e3647af877f9
      host14,192.168.1.72:8000,192.168.122.14,52:54:00:f4:16:14,d3386573-afed-4958-a2ab-2d7f3d68c69d
      host15,192.168.1.72:8000,192.168.122.15,52:54:00:f4:16:15,16d40706-3939-497a-afa0-4ec83ae152a8

#. Create the following script.

   .. important:: You may need to change or add variables for your environment.

   .. code-block:: bash
      :linenos:
      :emphasize-lines: 29,31,32,40,43-46,49,67,89,92,97-99,103,105,106,108

      #/bin/bash

      # Create output dir if not exists, delete old one if exists.

      if [[ -d output ]]; then
          rm -rf output
          mkdir -p output
      else
          mkdir -p output
      fi

      # Take "nodes" CSV and create bare-metal resources for cluster.

      for host in `cat nodes | grep -v HOST`; do
      HOST=`grep $host nodes | awk -F "," '{print $1}'`;
      BMCIP=`grep $host nodes | awk -F "," '{print $2}'`;
      HOSTIP=`grep $host nodes | awk -F "," '{print $3}'`;
      MAC1=`grep $host nodes | awk -F "," '{print $4}'`;
      UUID=`grep $host nodes | awk -F "," '{print $5}'`;
      done;

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
        automatedCleaningMode: metadata
        rootDeviceHints:
          deviceName: "/dev/vda"
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

#. Run script and create openshift objects.

   .. code-block:: bash

      ./script.sh

   .. code-block:: bash

      oc create -f output/
