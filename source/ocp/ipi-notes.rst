IPI Install Notes
=================

Using IPI with redfish has some automation benefits. Here's the
install-config.yaml I used with KVM.

.. attention:: I added dual stack example.

.. important:: I truncated the yaml example. Be sure to add all the hosts.

#. Download the latest v4.12.x openshift-install utility found here:
   `OpenShift mirror site <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest>`_

#. Extract install utility

   .. code-block:: bash

      tar -xzvf openshift-install-linux.tar.gz -C ~/.local/bin

#. Create a work subdir

   .. code-block:: bash

      mkdir ./workdir

#. Create "install-config.yaml" and save in ./workdir

   .. code-block:: yaml

      apiVersion: v1
      basedomain: lab.local
      metadata:
        name: ocp4
      networking:
        machineNetwork:
        - cidr: 192.168.1.0/24
        - cidr: 2600:1702:4c73:f110::0/64
        clusterNetwork:
        - cidr: 10.128.0.0/14
          hostPrefix: 23
        - cidr: fd02::/48
          hostPrefix: 64
        networkType: OVNKubernetes
        serviceNetwork:
        - 172.30.0.0/16
        - fd03::/112
      compute:
      - name: worker
        replicas: 2
      controlPlane:
        name: master
        replicas: 3
        platform:
          baremetal: {}
      platform:
        baremetal:
          apiVIPs:
            - 192.168.1.140
            - 2600:1702:4c73:f110::140
          ingressVIPs:
            - 192.168.1.141
            - 2600:1702:4c73:f110::141
          hosts:
            - name: host40.ocp4.lab.local
              role: master
              bmc:
                address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/940a6eaa-4b4f-4297-8182-e24cbfc64460
                username: kni
                password: kni
                disableCertificateVerification: True
              bootMACAddress: 52:54:00:f7:cf:4f
              rootDeviceHints:
                deviceName: "/dev/vda"
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
                        - ip: 192.168.1.40
                          prefix-length: 24
                    ipv6:
                      enabled: true
                      dhcp: false
                      address:
                        - ip: 2600:1702:4c73:f110::40
                          prefix-length: 64
                dns-resolver:
                  config:
                    search:
                      - lab.local
                    server:
                      - 192.168.1.68
                      - 2600:1702:4c73:f110::68
                routes:
                  config:
                    - destination: 0.0.0.0/0
                      next-hop-address: 192.168.1.1
                      next-hop-interface: enp1s0
                      table-id: 254
                    - destination: '::/0'
                      next-hop-address: '2600:1702:4c73:f110::1'
                      next-hop-interface: enp1s0

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

#. With "openshift-install" downloaded in step 1, run the following command to
   create the cluster.

   .. code-block:: bash

      openshift-install create cluster --dir ./workdir --log-level debug
