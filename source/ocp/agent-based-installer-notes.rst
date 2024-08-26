Agent-Based Install Notes
=========================

The following are notes on deploying OCP with the NEW (4.12) agent-based
installer. Two files are required to build the ISO, "install-config.yaml" and
"agent-config.yaml".

.. seealso:: For more detail: `Preparing to install with the Agent-based installer
   <https://docs.openshift.com/container-platform/4.12/installing/installing_with_agent_based_installer/preparing-to-install-with-agent-based-installer.html>`_

.. tip:: Check disk performance for etcd with "fio". It's critical to have a
   high performing disk drive for OCP / etcd.

   For more info:
   `How to Use 'fio' to Check Etcd Disk Performance in OCP
   <https://access.redhat.com/solutions/4885641?extIdCarryOver=true&sc_cid=701f2000001OH74AAG%20>`_

   .. code-block:: bash

      podman run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/openshift-scale/etcd-perf

#. Download the latest openshift-install utility found here:

   `OpenShift for x86_64 Installer <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-install-linux.tar.gz>`_

   .. attention:: The link points to the most recent version. Typically you'll
      want a specific version. You can find that here:

      `<https://access.redhat.com/downloads/content/290/>`_

#. Install nmstate

   .. code-block:: bash

      sudo dnf install /usr/bin/nmstatectl -y

#. Create a work subdir

   .. code-block:: bash

      mkdir ~/workdir

#. Create "install-config.yaml" and save in ~/workdir

   .. tip:: In resource-constrained environments, you can use
      `workload partitioning <https://docs.openshift.com/container-platform/4.14/scalability_and_performance/enabling-workload-partitioning.html>`_
      to isolate OpenShift Container Platform services, cluster management
      workloads, and infrastructure pods to run on a reserved set of CPUs.

      To enable "workload partitioning" add "cpuPartitioningMode: AllNodes"
      line right after "baseDomain:" line.

   .. code-block:: yaml
      :caption: install-config.yaml
      :emphasize-lines: 2, 14, 20, 26-30

      apiVersion: v1
      baseDomain: lab.local
      compute:
      - architecture: amd64
        hyperthreading: Enabled
        name: worker
        replicas: 2
      controlPlane:
        architecture: amd64
        hyperthreading: Enabled
        name: master
        replicas: 3
      metadata:
        name: ocp1
      networking:
        clusterNetwork:
        - cidr: 10.128.0.0/14
          hostPrefix: 23
        machineNetwork:
        - cidr: 192.168.122.0/24
        networkType: OVNKubernetes
        serviceNetwork:
        - 172.30.0.0/16
      platform:
        baremetal:
          apiVIP: "192.168.122.110"
          ingressVIP: "192.168.122.111"
      pullSecret: '{"auths":{"mirror.lab.local:8443":{"auth":"aW5pdDpwYXNzd29yZA=="}}}'
      sshKey: |
        ssh-rsa AAAAB3NzaC1yc2EAAAADAQA...
      imageContentSources:
      - mirrors:
        - mirror.lab.local:8443/openshift/release
        source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
      - mirrors:
        - mirror.lab.local:8443/openshift/release-images
        source: quay.io/openshift-release-dev/ocp-release
      additionalTrustBundle: |
        -----BEGIN CERTIFICATE-----
        <Use rootCA.pem from your mirror registry here>
        -----END CERTIFICATE-----

   .. note:: For SNO set "platform:" to "none: {}".

      .. code-block:: yaml

         platform:
           none: {}

#. Create agent-config.yaml and save in ~/workdir

   .. important:: Repeat "-hostname" block for each host in your config.

   .. code-block:: yaml
      :caption: agent-config.yaml - Ethernet Network Example
      :emphasize-lines: 3, 4, 6, 8, 9, 11, 13, 14, 17, 19, 25, 26, 32, 34, 38, 39

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.11
      additionalNTPSources:
      - 192.168.1.68
      hosts:
        - hostname: host11
          role: master
          rootDeviceHints:
            deviceName: "/dev/vda"
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:11
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                mtu: 9000
                state: up
                ipv4:
                  enabled: true
                  dhcp: false
                  address:
                    - ip: 192.168.122.11
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
                  next-hop-interface: enp1s0
                  table-id: 254

   .. code-block:: yaml
      :caption: agent-config.yaml - VLAN-TAG Network Example
      :emphasize-lines: 3, 4, 6, 8, 9, 11, 13, 14, 17-19, 21, 22, 25, 26, 31, 32, 38, 40, 44, 45

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.11
      additionalNTPSources:
      - 192.168.1.68
      hosts:
        - hostname: host11
          role: master
          rootDeviceHints:
            deviceName: "/dev/vda"
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:11
          networkConfig:
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
                    - ip: 192.168.122.11
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

   .. code-block:: yaml
      :caption: agent-config.yaml - Bond with VLAN-TAG Network Example
      :emphasize-lines: 3, 4, 6, 8, 9, 11, 13-16, 19-21, 23-25, 27-29, 31-35, 36-37, 39-41, 46, 47, 53, 55, 59, 60

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.11
      additionalNTPSources:
      - 192.168.1.68
      hosts:
        - hostname: host11
          role: master
          rootDeviceHints:
            deviceName: "/dev/vda"
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:11
            - name: enp2s0
              macAddress: 52:54:00:f4:17:11
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                mtu: 9000
                state: up
              - name: enp2s0
                type: ethernet
                mtu: 9000
                state: up
              - name: bond0
                type: bond
                mtu: 9000
                state: up
                link-aggregation:
                  mode: active-backup
                  port:
                  - enp1s0
                  - enp2s0
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
                    - ip: 192.168.122.11
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
                  next-hop-interface: bond0.122
                  table-id: 254

#. With "openshift-install" downloaded in step 1, run the following command. In
   my case I'm using a "workdir" dir to supply the required yaml files.

   .. tip:: Add the sub directory "openshift" to your workdir for custom
      configs. For example adding operators or setting "core" user passwd.

   .. code-block:: bash

      openshift-install agent create image --dir workdir

#. Boot the VM's with the ISO created in the previous step. Follow the progress
   with the following command:

   .. code-block:: bash

      openshift-install agent wait-for install-complete --dir workdir

.. note:: For my environment I manually set the MAC addresses for the VM's
   primary interface using the following patterns.

   .. code-block:: yaml

      <host mac='52:54:00:f4:16:11' ip='192.168.122.11'/>
      <host mac='52:54:00:f4:16:12' ip='192.168.122.12'/>
      <host mac='52:54:00:f4:16:13' ip='192.168.122.13'/>

      <host mac='52:54:00:f4:16:21' ip='192.168.122.21'/>
      <host mac='52:54:00:f4:16:22' ip='192.168.122.22'/>
      <host mac='52:54:00:f4:16:23' ip='192.168.122.23'/>

      <host mac='52:54:00:f4:16:31' ip='192.168.122.31'/>
      <host mac='52:54:00:f4:16:32' ip='192.168.122.32'/>
      <host mac='52:54:00:f4:16:33' ip='192.168.122.33'/>

      <host mac='52:54:00:f4:16:41' ip='192.168.122.41'/>
      <host mac='52:54:00:f4:16:42' ip='192.168.122.42'/>
      <host mac='52:54:00:f4:16:43' ip='192.168.122.43'/>

      <host mac='52:54:00:f4:16:51' ip='192.168.122.51'/>
      <host mac='52:54:00:f4:16:52' ip='192.168.122.52'/>
      <host mac='52:54:00:f4:16:53' ip='192.168.122.53'/>

Custom Partitioning
-------------------
Here I have a couple of common examples on how to customize the deployment
partitioning; A single block device and four block devices.

.. attention:: This example is "master" nodes only. If you want to apply to
   other machine config pools be sure to create the machine config with the
   appropriate labels.

#. Based on your environment create one of the following butane file/example.

   - One Device (400G)

     .. note:: With a single device the installer will use all the available
        space across 4 partitions. For this to work **"resize"** partition 4
        and create 3 additional partitions, utilizing the space free'd up from
        the resized partition.

     .. note:: By setting **"start_mib: 0"** the partition starts where the
        previous partition ended.

     .. note:: By setting **"size_mib: 0"** all of the avilable space is
        utilized by this partition.

     .. important::

        - **"wipe_partition_entry: true"** - If True, delete existing
          partition.
        - **"wipe_filesystem: true"** - If True, ignition will always wipe any
          preexisting filesystem and create the desired filesystem.
          The old filesystem will be lost.
        - **"with_mount_unit: true"** - Create the mount point.
        - **"mount_options: [defaults, prjquota]"** - The prjquota mount option
          must be enabled for filesystems used for container storage.

     .. code-block:: yaml
        :caption: 98-master-partition.bu - One Device (400G)
        :emphasize-lines: 5, 9, 20, 25, 30, 36, 42, 48

        variant: openshift
        version: 4.14.0
        metadata:
          labels:
            machineconfiguration.openshift.io/role: master
          name: 98-master-partition
        storage:
          disks:
            - device: /dev/disk/by-path/pci-0000:04:00.0
              partitions:
                - number: 1
                  should_exist: true
                - number: 2
                  should_exist: true
                - number: 3
                  should_exist: true
                - number: 4
                  resize: true
                  size_mib: 120000
                - label: var-lib-containers
                  number: 5
                  size_mib: 100000
                  start_mib: 0
                  wipe_partition_entry: true
                - label: var-lib-etcd
                  number: 6
                  size_mib: 100000
                  start_mib: 0
                  wipe_partition_entry: true
                - label: var-lib-prometheus-data
                  number: 7
                  size_mib: 0
                  start_mib: 0
                  wipe_partition_entry: true
          filesystems:
            - device: /dev/disk/by-partlabel/var-lib-containers
              format: xfs
              path: /var/lib/containers
              wipe_filesystem: true
              with_mount_unit: true
              mount_options: [defaults, prjquota]
            - device: /dev/disk/by-partlabel/var-lib-etcd
              format: xfs
              path: /var/lib/etcd
              wipe_filesystem: true
              with_mount_unit: true
              mount_options: [defaults, prjquota]
            - device: /dev/disk/by-partlabel/var-lib-prometheus-data
              format: xfs
              path: /var/lib/prometheus/data
              wipe_filesystem: true
              with_mount_unit: true
              mount_options: [defaults, prjquota]

   - Four Device's (100G each)

     .. note:: With four device's we don't need to identify the first device.
        I'm doing this for consistency but am making NO changes.

     .. note:: By setting **"start_mib: 0"** the partition starts where the
        previous partition ended.

     .. note:: By setting **"size_mib: 0"** all of the avilable space is
        utilized by this partition.

     .. important::

        - **"wipe_table: true"** - Without this the previously installed table
          is used and partition will not get created.
        - **"wipe_partition_entry: true"** - If True, delete existing
          partition.
        - **"wipe_filesystem: true"** - If True, ignition will always wipe any
          preexisting filesystem and create the desired filesystem.
          The old filesystem will be lost.
        - **"with_mount_unit: true"** - Create the mount point.
        - **"mount_options: [defaults, prjquota]"** - The prjquota mount option
          must be enabled for filesystems used for container storage.

     .. code-block:: yaml
        :caption: 98-master-partition.bu - Four Device's (100G each)
        :emphasize-lines: 5, 9, 19, 22, 27, 30, 35, 38, 44, 50, 56

        variant: openshift
        version: 4.14.0
        metadata:
          labels:
            machineconfiguration.openshift.io/role: master
          name: 98-master-partition
        storage:
          disks:
            - device: /dev/disk/by-path/pci-0000:05:00.0
              partitions:
                - number: 1
                  should_exist: true
                - number: 2
                  should_exist: true
                - number: 3
                  should_exist: true
                - number: 4
                  should_exist: true
            - device: /dev/disk/by-path/pci-0000:06:00.0
              wipe_table: true
              partitions:
                - label: var-lib-containers
                  number: 1
                  size_mib: 0
                  start_mib: 0
                  wipe_partition_entry: true
            - device: /dev/disk/by-path/pci-0000:07:00.0
              wipe_table: true
              partitions:
                - label: var-lib-etcd
                  number: 1
                  size_mib: 0
                  start_mib: 0
                  wipe_partition_entry: true
            - device: /dev/disk/by-path/pci-0000:08:00.0
              wipe_table: true
              partitions:
                - label: var-lib-prometheus-data
                  number: 1
                  size_mib: 0
                  start_mib: 0
                  wipe_partition_entry: true
          filesystems:
            - device: /dev/disk/by-partlabel/var-lib-containers
              format: xfs
              path: /var/lib/containers
              wipe_filesystem: true
              with_mount_unit: true
              mount_options: [defaults, prjquota]
            - device: /dev/disk/by-partlabel/var-lib-etcd
              format: xfs
              path: /var/lib/etcd
              wipe_filesystem: true
              with_mount_unit: true
              mount_options: [defaults, prjquota]
            - device: /dev/disk/by-partlabel/var-lib-prometheus-data
              format: xfs
              path: /var/lib/prometheus/data
              wipe_filesystem: true
              with_mount_unit: true
              mount_options: [defaults, prjquota]

#. Create machine config yaml.

   .. code-block:: bash

      butane 98-master-partition.bu -o 98-master-partition.yaml

#. Copy the "yaml" output to your install "working" dir / sub dir "openshift".
   By default agent install consumes the machine config in this sub dir.

Set Core User Passwd
--------------------

For lab purposes it might be beneficial to login as core user with a passwd vs.
cert auth. This process will set / override the default random passwd at
install time.

.. attention:: This example is "master" nodes only. If you want to apply to
   other machine config pools be sure to create the machine config with the
   appropriate labels.

#. Use mkpasswd to generate the encrypted passwd. I'm setting the passwd to
   "core".

   .. note:: If needed:

      .. code-block:: bash

         sudo dnf install mkpasswd

   .. code-block:: bash

      mkpasswd core

#. Create the following butane file, "98-master-core-pass.bu". I'm setting the
   passwd to "core" with the "mkpasswd" utility.

   .. code-block:: yaml
      :caption: 98-master-core-pass.bu
      :emphasize-lines: 5, 10

      variant: openshift
      version: 4.14.0
      metadata:
        labels:
          machineconfiguration.openshift.io/role: master
        name: 98-master-core-pass
      passwd:
        users:
          - name: core
            password_hash: <mkpasswd_output>

#. Create machine config yaml.

   .. code-block:: bash

      butane 98-master-core-pass.bu -o 98-master-core-pass.yaml

#. Copy the "yaml" output to your install "working" dir / sub dir "openshift".
   By default agent install consumes the machine config in this sub dir.

Calico Example
--------------
This is a continuation of the previous section.  Basically adding a subdir to
the working directory and copying the Calico CNI yaml files there, the
installer will consume the new informantion.

.. attention:: In this example I'm not disconnected / using my internal mirror.

#. Create the <assets_directory> and "openshift" subdir.

   .. code-block:: bash

      mkdir -p ./workdir/openshift

#. Create "install-config.yaml" and "agent-config.yaml" files in the
   <assets_directory>.

   .. code-block:: yaml
      :caption: install-config.yaml
      :emphasize-lines: 21

      apiVersion: v1
      baseDomain: lab.local
      compute:
      - architecture: amd64
        hyperthreading: Enabled
        name: worker
        replicas: 2
      controlPlane:
        architecture: amd64
        hyperthreading: Enabled
        name: master
        replicas: 3
      metadata:
        name: ocp5
      networking:
        clusterNetwork:
        - cidr: 10.128.0.0/14
          hostPrefix: 23
        machineNetwork:
        - cidr: 192.168.122.0/24
        networkType: Calico
        serviceNetwork:
        - 172.30.0.0/16
      platform:
        baremetal:
          apiVIP: "192.168.122.150"
          ingressVIP: "192.168.122.151"
      pullSecret: 'ADD_YOUR_PULL_SECRET_HERE'
      sshKey: |
        ssh-rsa AAAAB3NzaC1yc2EAAAADAQA...

   .. code-block:: yaml
      :caption: agent-config.yaml

      apiVersion: v1alpha1
      metadata:
        name: ocp5
      rendezvousIP: 192.168.122.51
      additionalNTPSources:
      - 192.168.1.68
      hosts:
        - hostname: host51
          role: master
          rootDeviceHints:
            deviceName: "/dev/vda"
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:51
          networkConfig:
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
                    - ip: 192.168.122.51
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

   .. important:: Repeat "-hostname" block for each host in your config.

#. Download and extract the Calico yaml to workdir/openshift.

   .. note:: As of this writing v3.27.0 is the latest.

   .. code-block:: bash

      wget -qO- https://github.com/projectcalico/calico/releases/download/v3.27.0/ocp.tgz | \
      tar xvz --strip-components=1 -C ./workdir/openshift

#. Create the ISO

   .. code-block:: bash

      openshift-install agent create image --dir workdir

#. Monitor the install

   .. code-block:: bash

      openshift-install agent wait-for install-complete --dir workdir

#. Once the cluster is up and running, check the Calico operator status.

   .. code-block:: bash

      oc get tigerastatus

IPv6 Only Example
-----------------

.. code-block:: yaml
   :caption: install-config.yaml

   apiVersion: v1
   baseDomain: lab.local
   compute:
   - architecture: amd64
     hyperthreading: Enabled
     name: worker
     replicas: 2
   controlPlane:
     architecture: amd64
     hyperthreading: Enabled
     name: master
     replicas: 3
   metadata:
     name: ocp3
   networking:
     clusterNetwork:
     - cidr: fd02::/48
       hostPrefix: 64
     machineNetwork:
     - cidr: 2600:1702:4c73:f111::0/64
     networkType: OVNKubernetes
     serviceNetwork:
     - fd03::/112
   platform:
     baremetal:
       apiVIPs:
         - 2600:1702:4c73:f111::130
       ingressVIPs:
         - 2600:1702:4c73:f111::131
   pullSecret: '{"auths":{"mirror.lab.local:8443":{"auth":"aW5pdDpwYXNzd29yZA=="}}}'
   sshKey: |
     ssh-rsa AAAAB3NzaC1yc2EAAAADAQA...
   imageContentSources:
   - mirrors:
     - mirror.lab.local:8443/openshift/release
     source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
   - mirrors:
     - mirror.lab.local:8443/openshift/release-images
     source: quay.io/openshift-release-dev/ocp-release
   additionalTrustBundle: |
     -----BEGIN CERTIFICATE-----
     <Use rootCA.pem for mirror registry here>
     -----END CERTIFICATE-----

.. code-block:: yaml
   :caption: agent-config.yaml

   apiVersion: v1alpha1
   metadata:
     name: ocp3
   rendezvousIP: 2600:1702:4c73:f111::31
   hosts:
     - hostname: host31
       role: master
       rootDeviceHints:
         deviceName: "/dev/vda"
       interfaces:
         - name: enp1s0
           macAddress: 52:54:00:f4:16:31
       networkConfig:
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
               enabled: false
               dhcp: false
             ipv6:
               enabled: true
               address:
                 - ip: 2600:1702:4c73:f111::31
                   prefix-length: 64
         dns-resolver:
           config:
             search:
               - lab.local
             server:
               - 2600:1702:4c73:f110::68
         routes:
           config:
             - destination: '::/0'
               next-hop-address: '2600:1702:4c73:f111::1'
               next-hop-interface: enp1s0.122
