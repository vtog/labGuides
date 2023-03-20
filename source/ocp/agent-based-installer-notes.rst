Agent-Based Install Notes
=========================

The following are notes on deploying OCP with the NEW (4.12) agent-based
installer. Two files are required to build the ISO, "install-config.yaml" and
"agent-config.yaml".

.. seealso:: For more detail: `Preparing to install with the Agent-based installer
   <https://docs.openshift.com/container-platform/4.12/installing/installing_with_agent_based_installer/preparing-to-install-with-agent-based-installer.html>`_

#. Download the latest v4.12.x openshift-install utility found here:
   `OpenShift mirror site <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest>`_

#. Install nmstate

   .. code-block:: bash

      sudo dnf install /usr/bin/nmstatectl -y
#. Create a work subdir

   .. code-block:: bash

      mkdir ~/workdir

#. Create "install-config.yaml" and save in ~/workdir

   .. code-block:: yaml
      :emphasize-lines: 2, 14, 20, 26-30

      apiVersion: v1
      baseDomain: lab.local
      compute:
      - architecture: amd64
        hyperthreading: Enabled
        name: worker
        replicas: 3
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
          apiVIP: "192.168.122.120"
          ingressVIP: "192.168.122.121"
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

#. Create agent-config.yaml and save in ~/workdir

   .. important:: Repeat "-hostname" block for each host of your config.

   .. code-block:: yaml
      :caption: Ethernet Network Example
      :emphasize-lines: 3, 4, 6, 7, 9, 10, 13, 14, 16, 20, 28, 32, 33

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.21
      hosts:
        - hostname: host21
          role: master
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:21
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                state: up
                mtu: 9000
                ipv4:
                  enabled: true
                  address:
                    - ip: 192.168.122.21
                      prefix-length: 24
                  dhcp: false
                ipv6:
                  enabled: false
            dns-resolver:
              config:
                server:
                  - 192.168.1.72
            routes:
              config:
                - destination: 0.0.0.0/0
                  next-hop-address: 192.168.122.1
                  next-hop-interface: enp1s0
                  table-id: 254

   .. code-block:: yaml
      :caption: VLAN Network Example
      :emphasize-lines: 3, 4, 6, 7, 9, 10, 13, 14, 16, 18, 19, 23, 31, 35, 36

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.21
      hosts:
        - hostname: host21
          role: master
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:21
          networkConfig:
            interfaces:
              - name: enp1s0.122
                type: vlan
                state: up
                mtu: 9000
                vlan:
                  base-iface: enp1s0
                  id: 122
                ipv4:
                  enabled: true
                  address:
                    - ip: 192.168.122.21
                      prefix-length: 24
                  dhcp: false
                ipv6:
                  enabled: false
            dns-resolver:
              config:
                server:
                  - 192.168.1.72
            routes:
              config:
                - destination: 0.0.0.0/0
                  next-hop-address: 192.168.122.1
                  next-hop-interface: enp1s0.122
                  table-id: 254

   .. code-block:: yaml
      :caption: Bond with VLAN Network Example
      :emphasize-lines: 3, 4, 6, 7, 9-12, 15, 16, 21-24, 26, 28, 29, 33, 41, 45, 46

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.21
      hosts:
        - hostname: host21
          role: master
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:21
            - name: enp2s0
              macAddress: 52:54:00:f4:17:21
          networkConfig:
            interfaces:
              - name: bond0
                type: bond
                state: up
                link-aggregation:
                  mode: active-backup
                  port:
                  - enp1s0
                  - enp2s0
              - name: bond0.122
                type: vlan
                state: up
                mtu: 9000
                vlan:
                  base-iface: bond0
                  id: 122
                ipv4:
                  enabled: true
                  address:
                    - ip: 192.168.122.21
                      prefix-length: 24
                  dhcp: false
                ipv6:
                  enabled: false
            dns-resolver:
              config:
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

   .. code-block:: bash

      ./openshift-install agent create image --dir workdir

#. Boot the VM's with the ISO created in the previous step. Follow the progress
   with the following command:

   .. code-block:: bash

      ./openshift-install agent wait-for install-complete --dir workdir


