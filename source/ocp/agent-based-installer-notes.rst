Agent-Based Install Notes
=========================

The following are notes on deploying OCP with the NEW (4.12) agent-based
installer. Two files are required to build the ISO, "install-config.yaml" and
"agent-config.yaml".

.. tip:: Check disk performance for etcd with "fio". It's critical to have a
   high performing disk drive for OCP / etcd.

   For more info:
   `How to Use 'fio' to Check Etcd Disk Performance in OCP
   <https://access.redhat.com/solutions/4885641?extIdCarryOver=true&sc_cid=701f2000001OH74AAG%20>`_

   .. code-block:: bash

      podman run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/openshift-scale/etcd-perf

.. seealso:: For more detail: `Preparing to install with the Agent-based installer
   <https://docs.openshift.com/container-platform/4.12/installing/installing_with_agent_based_installer/preparing-to-install-with-agent-based-installer.html>`_

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

   .. tip:: Optional: To enable workload partitioning add "cpuPartitioningMode:
      AllNodes" line right after "baseDomain:" line.

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
      - 192.168.1.72
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
                  - 192.168.1.72
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
      - 192.168.1.72
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
                  - 192.168.1.72
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
      - 192.168.1.72
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
                  - 192.168.1.72
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

Set Core User Passwd
--------------------

For lab purposes it might be beneficial to login as core user with a passwd vs.
cert auth. This process will set / override the default random passwd at
install time.

.. note:: This example is "master" nodes only. If you want to apply to other
   machine config pools be sure to create the machine config with the
   appropriate labels.

#. Create the following butane file, "98-master-core-pass.bu". I'm setting the
   passwd to "core". Use base64 decode to configure passwd of your choice.

   .. code-block:: bash
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
            password_hash: Y29yZQ==

#. Create machine config yaml

   .. code-block:: bash

      butane --files-dir . 98-master-core-pass.bu > 98-master-core-pass.yaml

#. Copy this file to your openshift install "working" dir / sub dir
   "openshift". By default agent install consumes the machine config in this
   sub dir.

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
      - 192.168.1.72
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
                  - 192.168.1.72
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
               - 2600:1702:4c73:f110::72
         routes:
           config:
             - destination: '::/0'
               next-hop-address: '2600:1702:4c73:f111::1'
               next-hop-interface: enp1s0.122
