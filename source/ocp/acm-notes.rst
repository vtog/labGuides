Advanced Cluster Management
===========================

Install ACM
-----------

Basic ACM install to get started.

.. tip:: Be sure to have enough cpu, memory, and storage. My lab is KVM based.
   For ACM I start with a three node cluster, each node has 16 cores, 32G
   memory, and small 600G ODF/Ceph deployment.

#. From the OCP Console select :menuselection:`Operators --> OperatorHub`. In
   the search box type "acm".

   .. image:: ./images/acm-operatorhub.png

#. Click Install.

   .. image:: ./images/acm-install.png

#. After install completes, open the newly installed operator. Select
   MultiClusterHub tab and click "Create MultiClusterHub".

   .. image:: ./images/acm-multiclusterhub.png

#. Accept the defaults and click "Create".

   .. image:: ./images/acm-create-multiclusterhub.png

#. Be patient several containers are pulled and started. You can monitor the
   progress by watching the pods in the "multicluster-engine" and
   "open-cluster-management" namespace.

   .. code-block:: bash

      oc get pods -n open-cluster-management

      oc get pods -n multicluster-engine

Basic / Manual Config
---------------------

Simple config to get started. The following steps will create the following
objects:

- Host inventory (Connected or Disconnected)
- Credentials
- Infrastructure environment
- Add host inventory

.. _host-inventory-connected:

Host inventory (Connected)
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Patch the provisioning-configuration to watch all name spaces.

   .. code-block:: bash

      oc patch provisioning provisioning-configuration --type merge \
        --patch '{"spec":{"watchAllNamespaces": true }}'

#. From the console select :menuselection:`Infrastructure --> Host Inventory`.
   Click :menuselection:`Configure host inventory settings`.

   .. image:: ./images/acm-host-inventory-settings.png

#. Configure host inventory settings and click "Configure".

   .. warning:: For disconnected environments skip to next section.

   .. image:: ./images/acm-configure-host-inventory.png

   .. attention:: Be patient this process will take some time. For a connected
      environment several images need to be pulled down. You can monitor this
      process with the following commands. Wait for the pod to fully start.

      .. code-block:: bash

         oc get pod assisted-image-service-0 -n multicluster-engine

         oc logs assisted-image-service-0 -n multicluster-engine -f

.. _host-inventory-disconnected:

Host inventory (Disconnected)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Patch the provisioning-configuration to watch all name spaces.

   .. code-block:: bash

      oc patch provisioning provisioning-configuration --type merge \
        --patch '{"spec":{"watchAllNamespaces": true }}'

#. Create the following configmap referencing your disconnected registry.

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
         version you plan to deploy will dictate which version to download. For
         example 4.15; If 4.15.22 or lower, select 4.15.0. If 4.15.23 and
         higher, select 4.15.23. In my case I need both.

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

   .. warning:: I've had many issues with discovery when defining multiple
      osImages.  I recommend starting with only defining the oldest needed
      version. Then run node discovery. Then add the additional osImages.

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

Credentials
~~~~~~~~~~~

#. From the CLI create a new project/namespace for your spoke cluster objects.

   .. code-block:: bash

      oc new-project <project_name>

   .. tip:: I recommend making the project_name the domain name with no dots.

      For example: "lab.local" ==  "lablocal"

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

Infrastructure environment
~~~~~~~~~~~~~~~~~~~~~~~~~~

#. From the console select :menuselection:`Infrastructure --> Host Inventory`.
   Click :menuselection:`Create infrastructure environment`.

   .. image:: ./images/acm-infra-env.png

#. Enter the information for your infrastructure environment. Click "Create"
   when finished.

   .. note:: Use the previously created credentials in the "Infrastructure
      provider credentials" drop down list.

   .. image:: ./images/acm-create-infra-env.png

Add host inventory
~~~~~~~~~~~~~~~~~~

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

   .. note:: The Secret username and password are base64 encoded.

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
              mtu: 1500
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

   .. tip:: Monitor BMH progress

      .. code-block:: bash

         oc logs metal3-baremetal-operator-675565dfc-7stdm -n openshift-machine-api --follow

GitOps
------

.. tip:: Clone my github repo. All the files listed below are included, modify
   as needed.

   .. code-block:: bash

      git clone https://github.com/vtog/gitops.git

Install operators
~~~~~~~~~~~~~~~~~

For GitOps two operators are required:

- Red Hat OpenShift GitOps
- Topology Aware Lifecycle Manager

Both operators can be found on the OperatorHub and for this lab the default
config is all that is needed. Simply accept the defaults and click "Install".

Host inventory
~~~~~~~~~~~~~~

Just like the basic/manual config, we need to configure the host inventory
first. This can be done connected or disconnected:

For **connected** see :ref:`host-inventory-connected`

For **disconnected** see :ref:`host-inventory-disconnected`

Environment / Cluster
~~~~~~~~~~~~~~~~~~~~~

From the cli create the following yaml manifests and apply them to your hub
cluster. When finished you'll have a SNO cluster running.

.. tip:: Use the "kustomization.yaml" to create the manifests
   ``oc create -k ./<manifest-dir>``. This process can be used to test the
   manifests for errors before gitops automation.

- 00-namespace.yaml
- 01-unsealed-bmc-secret.yaml
- 02-unsealed-pull-secret.yaml
- 03-agentclusterinstall.yaml
- 04-clusterdeployment.yaml
- 05-klusterlet.yaml
- 06-managedcluster.yaml
- 07-nmstate.yaml
- 08-infraenv.yaml
- 09-baremetalhost.yaml
- kustomization.yaml

.. code-block:: bash
   :caption: 00-namespace.yaml
   :emphasize-lines: 2,4

   apiVersion: v1
   kind: Namespace
   metadata:
     name: ztp-spoke-01

.. code-block:: bash
   :caption: 01-unsealed-bmc-secret.yaml
   :emphasize-lines: 3-5,9,10

   apiVersion: v1
   data:
     password: a25p
     username: a25p
   kind: Secret
   metadata:
     labels:
       app.kubernetes.io/instance: clusters
     name: bmc-secret
     namespace: ztp-spoke-01
   type: Opaque

.. code-block:: bash
   :caption: 02-unsealed-pull-secret.yaml
   :emphasize-lines: 8,9,11,12

   # After creating the secret use the following to set the data with your custom docker config json.
   # oc set data secret/pull-secret --from-file=.dockerconfigjson=/home/vince/.docker/config.json -n ztp-spoke-01
   # or
   # oc create secret docker-registry --from-file=.dockerconfigjson=/home/vince/.docker/config.json pull-secret -n ztp-spoke-01

   apiVersion: v1
   data:
     .dockerconfigjson: ewoJImF1dGhzIjogewoJICAibWlycm9yLmxhYi5sb2NhbDo4NDQzIjogewogICAgICAiYXV0aCI6ICJhVzVwZERwd1lYTnpkMjl5WkE9PSIKICAgIH0KICB9Cn0K
   kind: Secret
   metadata:
     name: pull-secret
     namespace: ztp-spoke-01

.. code-block:: bash
   :caption: 03-agentclusterinstall.yaml
   :emphasize-lines: 2,8,9,11,14,16,22,28

   apiVersion: extensions.hive.openshift.io/v1beta1
   kind: AgentClusterInstall
   metadata:
     annotations:
       agent-install.openshift.io/install-config-overrides: '{"networking":{"networkType":"OVNKubernetes"}}'
       argocd.argoproj.io/sync-wave: '1'
       ran.openshift.io/ztp-gitops-generated: '{}'
     labels:
       app.kubernetes.io/instance: clusters
     name: ztp-spoke-01
     namespace: ztp-spoke-01
   spec:
     clusterDeploymentRef:
       name: ztp-spoke-01
     imageSetRef:
       name: img4.16.8-x86-64-appsub
     networking:
       clusterNetwork:
         - cidr: 10.128.0.0/14
           hostPrefix: 23
       machineNetwork:
         - cidr: 192.168.132.0/24
       serviceNetwork:
         - 172.30.0.0/16
     provisionRequirements:
       controlPlaneAgents: 1
       workerAgents: 0
     sshPublicKey: <redacted>

.. code-block:: bash
   :caption: 04-clusterdeployment.yaml
   :emphasize-lines: 2,4,5,7,8,15,21,23

   apiVersion: hive.openshift.io/v1
   kind: ClusterDeployment
   metadata:
     name: ztp-spoke-01
     namespace: ztp-spoke-01
   spec:
     baseDomain: lab.local
     clusterName: ztp-spoke-01
     controlPlaneConfig:
       servingCertificates: {}
     installed: false
     clusterInstallRef:
       group: extensions.hive.openshift.io
       kind: AgentClusterInstall
       name: ztp-spoke-01
       version: v1beta1
     platform:
       agentBareMetal:
         agentSelector:
           matchLabels:
             cluster-name: "ztp-spoke-01"
     pullSecretRef:
       name: pull-secret

.. code-block:: bash
   :caption: 05-klusterlet.yaml
   :emphasize-lines: 2,4,5,13,16,17

   apiVersion: agent.open-cluster-management.io/v1
   kind: KlusterletAddonConfig
   metadata:
     name: ztp-spoke-01
     namespace: ztp-spoke-01
   spec:
     applicationManager:
       argocdCluster: false
       enabled: true
     certPolicyController:
       enabled: true
     clusterLabels:
       name: ztp-spoke-01
       cloud: Baremetal
       vendor: auto-detect
     clusterName: ztp-spoke-01
     clusterNamespace: ztp-spoke-01
     iamPolicyController:
       enabled: true
     policyController:
       enabled: true
     searchCollector:
       enabled: true
     version: 2.6.2

.. code-block:: bash
   :caption: 06-managedcluster.yaml
   :emphasize-lines: 2,4,5,7

   apiVersion: cluster.open-cluster-management.io/v1
   kind: ManagedCluster
   metadata:
     name: ztp-spoke-01
     namespace: ztp-spoke-01
     labels:
       name: ztp-spoke-01
   spec:
     hubAcceptsClient: true
     leaseDurationSeconds: 60

.. code-block:: bash
   :caption: 07-nmstate.yaml
   :emphasize-lines: 2,4,5,7,10,11,14-16,18,19,22,23,28,29,35,37,41,42

   apiVersion: agent-install.openshift.io/v1beta1
   kind: NMStateConfig
   metadata:
     name: ztp-spoke-01
     namespace: ztp-spoke-01
     labels:
       cluster-name: ztp-spoke-01
   spec:
     interfaces:
       - name: enp1s0
         macAddress: 52:54:00:f4:16:21
     config:
       interfaces:
         - name: enp1s0
           type: ethernet
           mtu: 1500
           state: up
         - name: enp1s0.132
           type: vlan
           state: up
           vlan:
             base-iface: enp1s0
             id: 132
           ipv4:
             enabled: true
             dhcp: false
             address:
               - ip: 192.168.132.21
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
             next-hop-address: 192.168.132.1
             next-hop-interface: enp1s0.132
             table-id: 254

.. code-block:: bash
   :caption: 08-infraenv.yaml
   :emphasize-lines: 2,4,5,10,12-14,17,19,22

   apiVersion: agent-install.openshift.io/v1beta1
   kind: InfraEnv
   metadata:
     name: ztp-spoke-01
     namespace: ztp-spoke-01
     annotations:
       argocd.argoproj.io/sync-options: Validate=false
   spec:
     additionalNTPSources:
       - 192.168.1.68
     clusterRef:
       name: ztp-spoke-01
       namespace: ztp-spoke-01
     sshAuthorizedKey: '<redacted>'
     agentLabelSelector:
       matchLabels:
         cluster-name: ztp-spoke-01
     pullSecretRef:
       name: pull-secret
     nmStateConfigLabelSelector:
       matchLabels:
         cluster-name: ztp-spoke-01

.. code-block:: bash
   :caption: 09-baremetalhost.yaml
   :emphasize-lines: 2,6,8-10,14,16,17,19

   apiVersion: metal3.io/v1alpha1
   kind: BareMetalHost
   metadata:
     annotations:
       inspect.metal3.io: disabled
       bmac.agent-install.openshift.io/hostname: "ztp-spoke-01"
     labels:
       infraenvs.agent-install.openshift.io: "ztp-spoke-01"
     name: ztp-spoke-01
     namespace: ztp-spoke-01
   spec:
     automatedCleaningMode: metadata
     rootDeviceHints:
       deviceName: /dev/vda
     bmc:
       address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/4df1a257-6ab8-4de9-a530-1781da98aa98
       credentialsName: bmc-secret
       disableCertificateVerification: true
     bootMACAddress: '52:54:00:f4:16:21'
     bootMode: UEFI
     online: true

.. code-block:: bash
   :caption: kustomization.yaml
   :emphasize-lines: 2

   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization

   resources:
     - 00-namespace.yaml
     - 01-unsealed-bmc-secret.yaml
     - 02-unsealed-pull-secret.yaml
     - 03-agentclusterinstall.yaml
     - 04-clusterdeployment.yaml
     - 05-klusterlet.yaml
     - 06-managedcluster.yaml
     - 07-nmstateconfig.yaml
     - 08-infraenv.yaml
     - 09-baremetalhost.yaml

Automation
~~~~~~~~~~

#. From the ACM console view select: :menuselection:`Applications` from the
   menu. Click "Create application" and select "Subscription".

   .. image:: ./images/acm-create-app.png

#. Add the name and namespace for the cluster and select "Git".

   .. important:: Use the same name and namespace used in your manifests.
      00-namespace.yaml is not part of the kustomization yaml so creating the
      right namespace is critical.

   .. image:: ./images/acm-create-app2.png

#. Add your repo info for the cluster. In my lab I only need:

   - URL
   - Branch
   - Path

   .. image:: ./images/acm-git.png

#. After adding repo info scroll down to "Cluster sets" and select "default".
   Then click "Create" in the upper right corner.
