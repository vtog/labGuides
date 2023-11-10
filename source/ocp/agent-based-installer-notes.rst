Agent-Based Install Notes
=========================

The following are notes on deploying OCP with the NEW (4.12) agent-based
installer. Two files are required to build the ISO, "install-config.yaml" and
"agent-config.yaml".

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

   .. code-block:: yaml
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

   .. note:: For SNO set "platform:" to "none {}".

#. Create agent-config.yaml and save in ~/workdir

   .. important:: Repeat "-hostname" block for each host in your config.

   .. code-block:: yaml
      :caption: Ethernet Network Example
      :emphasize-lines: 3, 4, 6, 7, 9, 10, 13, 14, 16, 21, 28, 32, 33

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.11
      additionalNTPSources:
      - 192.168.1.72
      hosts:
        - hostname: host11
          role: master
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:11
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                state: up
                mtu: 9000
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
      :caption: VLAN-TAG Network Example
      :emphasize-lines: 3, 4, 6, 7, 9, 10, 13, 14, 16, 17, 18, 21, 22, 27, 34, 38, 39

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.11
      additionalNTPSources:
      - 192.168.1.72
      hosts:
        - hostname: host11
          role: master
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:11
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                state: up
                mtu: 9000
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
      :caption: Bond with VLAN-TAG Network Example
      :emphasize-lines: 3, 4, 6, 7, 9-12, 15, 16, 18-20, 22-24, 29-32, 35, 36, 41, 48, 52, 53

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.11
      additionalNTPSources:
      - 192.168.1.72
      hosts:
        - hostname: host11
          role: master
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:11
            - name: enp1s1
              macAddress: 52:54:00:f4:17:11
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                state: up
                mtu: 9000
              - name: enp1s1
                type: ethernet
                state: up
                mtu: 9000
              - name: bond0
                type: bond
                state: up
                link-aggregation:
                  mode: active-backup
                  port:
                  - enp1s0
                  - enp1s1
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

   .. code-block:: bash

      openshift-install agent create image --dir workdir

#. Boot the VM's with the ISO created in the previous step. Follow the progress
   with the following command:

   .. code-block:: bash

      openshift-install agent wait-for install-complete --dir workdir


Example of IPv6 only
--------------------

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
       interfaces:
         - name: enp1s0
           macAddress: 52:54:00:f4:16:31
       networkConfig:
         interfaces:
           - name: enp1s0
             type: ethernet
             state: up
             mtu: 9000
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

