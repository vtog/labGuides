IPI Install Notes
=================

Using IPI with redfish has some automation benefits. Here's the
install-config.yaml I used with KVM.

.. attention:: I added dual stack example.

.. important:: I truncated the yaml example. Be sure to add all the hosts.

#. Download the latest openshift-install utility found here:
   `OpenShift mirror site <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest/>`_

#. Extract install utility

   .. code-block:: bash

      tar -xzvf openshift-install-linux.tar.gz -C ~/.local/bin

#. Create a work subdir

   .. code-block:: bash

      mkdir ./workdir

#. Create "install-config.yaml" and save in ./workdir

   .. code-block:: yaml
      :linenos:

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
                    mtu: 1500
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
      imageDigestSources:
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


Remote Worker Node Example
--------------------------

.. code-block:: yaml
   :emphasize-lines: 7,8,58,100,142,184,226
   :linenos:

   apiVersion: v1
   basedomain: lab.local
   metadata:
     name: ocp5
   networking:
     machineNetwork:
     - cidr: 192.168.122.0/24
     - cidr: 192.168.132.0/24
     clusterNetwork:
     - cidr: 10.128.0.0/14
       hostPrefix: 23
     networkType: OVNKubernetes
     serviceNetwork:
     - 172.30.0.0/16
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
         - 192.168.122.150
       ingressVIPs:
         - 192.168.122.151
       provisioningNetwork: "Disabled"
       externalBridge: "bridge0"
       hosts:
         - name: host51.lab.local
           role: master
           bmc:
             address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/06c5182a-7599-42bf-8e2d-395f3aeab1b5
             username: kni
             password: kni
             disableCertificateVerification: True
           bootMACAddress: 52:54:00:f4:16:51
           rootDeviceHints:
             deviceName: "/dev/vda"
           networkConfig:
             interfaces:
               - name: enp1s0
                 type: ethernet
                 state: up
                 mtu: 1500
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
         - name: host52.lab.local
           role: master
           bmc:
             address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/0662cc00-1c67-4519-b7d2-67c3f8ba9ea2
             username: kni
             password: kni
             disableCertificateVerification: True
           bootMACAddress: 52:54:00:f4:16:52
           rootDeviceHints:
             deviceName: "/dev/vda"
           networkConfig:
             interfaces:
               - name: enp1s0
                 type: ethernet
                 state: up
                 mtu: 1500
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
                     - ip: 192.168.122.52
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
         - name: host53.lab.local
           role: master
           bmc:
             address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/26c8d1cb-5340-42c9-a6e0-b680585ae6bb
             username: kni
             password: kni
             disableCertificateVerification: True
           bootMACAddress: 52:54:00:f4:16:53
           rootDeviceHints:
             deviceName: "/dev/vda"
           networkConfig:
             interfaces:
               - name: enp1s0
                 type: ethernet
                 state: up
                 mtu: 1500
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
                     - ip: 192.168.122.53
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
         - name: host54.lab.local
           role: worker
           bmc:
             address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/93cda952-42ee-424e-9977-76a2d652a6c0
             username: kni
             password: kni
             disableCertificateVerification: True
           bootMACAddress: 52:54:00:f4:16:54
           rootDeviceHints:
             deviceName: "/dev/vda"
           networkConfig:
             interfaces:
               - name: enp1s0
                 type: ethernet
                 state: up
                 mtu: 1500
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
                     - ip: 192.168.132.54
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
         - name: host55.lab.local
           role: worker
           bmc:
             address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/05057ca0-094d-4e8f-9eea-1bd95b4e88d5
             username: kni
             password: kni
             disableCertificateVerification: True
           bootMACAddress: 52:54:00:f4:16:55
           rootDeviceHints:
             deviceName: "/dev/vda"
           networkConfig:
             interfaces:
               - name: enp1s0
                 type: ethernet
                 state: up
                 mtu: 1500
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
                     - ip: 192.168.132.55
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

   pullSecret: '{"auths":{"mirror.lab.local:8443":{"auth":"aW5pdDpwYXNzd29yZA=="}}}'
   sshKey: |
     ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDE
   imageDigestSources:
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
