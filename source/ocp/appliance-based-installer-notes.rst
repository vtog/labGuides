Appliance-Based Install Notes
=============================

The following are notes on deploying OCP using the Appliance Builder and
Agent Based Installer.

.. seealso:: My notes are based on the following Red Hat Article. For a more
   thorough explanation of the process see: `OpenShift-based Appliance Builder User
   Guide <https://access.redhat.com/articles/7065136>`_

.. tip:: Check disk performance for etcd with "fio". It's critical to have a
   high performing disk drive for OCP / etcd.

   For more info:
   `How to Use 'fio' to Check Etcd Disk Performance in OCP
   <https://access.redhat.com/solutions/4885641?extIdCarryOver=true&sc_cid=701f2000001OH74AAG%20>`_

   .. code-block:: bash

      podman run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/openshift-scale/etcd-perf

Build the disk image
--------------------

#. Set the environment variables.

   .. important:: Use absolute directory paths.

   .. tip:: For container info and download instructions see:
      `OpenShift-based Appliance Builder
      <https://catalog.redhat.com/software/containers/assisted/agent-preinstall-image-builder-rhel9/65a55174031d94dbea7f2e00?architecture=amd64&image=66314d3a84d042ce9f6acbaf&container-tabs=overview>`_

   .. code-block:: bash

      export APPLIANCE_IMAGE="registry.redhat.io/assisted/agent-preinstall-image-builder-rhel9:1.0-1714506949"
      export APPLIANCE_ASSETS="/home/vince/OCP/appliance-builder"

#. Get the openshift appliance builder.

   .. code-block:: bash

      podman pull $APPLIANCE_IMAGE

#.  Generate the appliance template. A new file, "appliance-config.yaml" is
    created in the $APPLIANCE_ASSETS directory.

   .. code-block:: bash

      podman run --rm -it --pull newer -v $APPLIANCE_ASSETS:/assets:Z $APPLIANCE_IMAGE generate-config

#. Modify "appliance-config.yaml" for your environment.

   .. code-block:: yaml

      apiVersion: v1beta1
      kind: ApplianceConfig
      ocpRelease:
        version: 4.14
        channel: stable
        cpuArchitecture: x86_64
      diskSizeGB: 200
      pullSecret: <your-pull-secret>
      sshKey: <your-ssh-key>
      userCorePass: <your-core-passwd>
      imageRegistry:
        # Default: docker.io/library/registry:2
        # [Optional]
        uri: docker.io/library/registry:2
        # Default: 5005
        # [Optional]
        port: 5005
      # Enable all default CatalogSources (on openshift-marketplace namespace).
      # Should be disabled for disconnected environments.
      # Default: false
      # [Optional]
      enableDefaultSources: false
      # Stop the local registry post cluster installation.
      # Note that additional images and operators won't be available when stopped.
      # Default: false
      # [Optional]
      stopLocalRegistry: false

#. Build the disk image. This will create a "raw" disk image for your cluter
   appliance.

   .. code-block:: bash

      sudo podman run --rm -it --pull newer --privileged --net=host -v $APPLIANCE_ASSETS:/assets:Z $APPLIANCE_IMAGE build

   .. important:: If needed you can rebuild the disk image with another version
      or updated or additional manifests but you must first "clean" the assets
      directory first.

      .. code-block:: bash

         sudo podman run --rm -it -v $APPLIANCE_ASSETS:/assets:Z $APPLIANCE_IMAGE clean

   .. note: The clean command keeps the cache folder under assets intact. To
      clean the entire cache as well, use the --cache flag with the clean
      command.

Clone the appliance disk image
------------------------------

In my environment I'm using libvirt.

#. Convert the raw image to qcow2.

   .. code-block:: bash

      qemu-img convert -O qcow2 appliance.raw appliance-4.14.30.qcow2

#. Create a disk image for each node and copy to the destination storage pool.
   In my case 3 nodes host11-13.

   .. code-block:: bash

      for i in {11..13}; do cp appliance-4.14.30.qcow2 /local/host$i.qcow2; done;

.. tip:: For baremetal you can copy the raw image to the destination drive

   .. code-block:: bash

      dd if=appliance.raw of=/dev/sda bs=1M status=progress


Create the agent install manifests
----------------------------------

#. Download the version specific openshift-install utility. You can find that
   here: `<https://access.redhat.com/downloads/content/290/>`_

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
      pullSecret: '{"auths":{"":{"auth":"dXNlcjpwYXNz"}}}'
      sshKey: |
        <your-ssh-key>

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

      openshift-install agent create config-image --dir workdir

   .. note:: This is not a bootable image. It contains all the necessary
      information to build the cluster. The boot image is contained on the disk
      images created earlier.


#. Boot the VM's with the ISO created in the previous step. Follow the progress
   with the following command:

   .. code-block:: bash

      openshift-install agent wait-for install-complete --dir workdir
