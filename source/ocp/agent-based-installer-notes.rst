Agent-Based Install Notes
=========================

The following are notes on deploying OCP with the NEW (4.12) agent-based
installer. Two files are required to build the ISO, "install-config.yaml" and
"agent-config.yaml".

#. install-config.yaml

   .. code-block:: yaml
      :emphasize-lines: 2, 14, 20, 45-49

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
          hosts:
            - name: host21
              role: master
              bootMACAddress: 52:54:00:f4:16:21
            - name: host22
              role: master
              bootMACAddress: 52:54:00:f4:16:22
            - name: host23
              role: master
              bootMACAddress: 52:54:00:f4:16:23
            - name: host24
              role: worker
              bootMACAddress: 52:54:00:f4:16:24
            - name: host25
              role: worker
              bootMACAddress: 52:54:00:f4:16:25
            - name: host26
              role: woker
              bootMACAddress: 52:54:00:f4:16:26
          apiVIP: "192.168.122.120"
          ingressVIP: "192.168.122.121"
      pullSecret: '{“auths”:{“fake”:{“auth”: “bar”}}}'
      sshKey: |
        ssh-rsa AAAAB3NzaC1yc2EAAAADAQA...

#. agent-config.yaml (repeat "hostname" block for each host).

   .. code-block:: yaml
      :emphasize-lines: 3, 4, 6, 9, 11, 12, 15, 19, 23, 31, 35, 36

      apiVersion: v1alpha1
      metadata:
        name: ocp1
      rendezvousIP: 192.168.122.21
      hosts:
        - hostname: host21
          role: master
          rootDeviceHints:
            deviceName: /dev/sda
          interfaces:
            - name: enp1s0
              macAddress: 52:54:00:f4:16:21
          networkConfig:
            interfaces:
              - name: enp1s0
                type: ethernet
                state: up
                mtu: 9000
                mac-address: 52:54:00:f4:16:21
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
                  - 192.168.122.1
            routes:
              config:
                - destination: 0.0.0.0/0
                  next-hop-address: 192.168.122.1
                  next-hop-interface: enp1s0
                  table-id: 254

#. With the latest "openshift-install" run the following command. In my case
   I'm using a "workdir" with my support yaml files.

   .. code-block:: bash

      ./openshift-install agent create image --dir workdir

#. Boot the VM's with the ISO created in the previous step. Follow the progress
   with the following command:

   .. code-block:: bash

      ./openshift-install agent wait-for install-complete --dir workdir


