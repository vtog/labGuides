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

#. Generate the appliance template. A new file, "appliance-config.yaml" is
   created in the $APPLIANCE_ASSETS directory.

   .. code-block:: bash

      podman run --rm -it --pull newer -v $APPLIANCE_ASSETS:/assets:Z $APPLIANCE_IMAGE generate-config

#. Modify "appliance-config.yaml" for your environment.

   .. code-block:: yaml

      apiVersion: v1beta1
      kind: ApplianceConfig
      ocpRelease:
        # OCP release version in major.minor or major.minor.patch format
        # (in case of major.minor - latest patch version will be used)
        # If the specified version is not yet available, the latest supported version will be used.
        version: 4.16
        # OCP release update channel: stable|fast|eus|candidate
        # Default: stable
        # [Optional]
        channel: stable
        # OCP release CPU architecture: x86_64|aarch64|ppc64le
        # Default: x86_64
        # [Optional]
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
      # Additional images to be included in the appliance disk image.
      # [Optional]
      additionalImages:
        - name: registry.redhat.io/ubi8/ubi:latest
        - name: registry.redhat.io/ubi9/ubi:latest
        - name: registry.redhat.io/ubi9/httpd-24:latest
        - name: registry.redhat.io/ubi9/nginx-122:latest
        - name: registry.redhat.io/rhel8/support-tools:latest
        - name: registry.redhat.io/rhel9/support-tools:latest
        - name: registry.redhat.io/openshift4/dpdk-base-rhel8:latest
        - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-rhel9-operator:v4.16
        - name: registry.redhat.io/openshift4/ztp-site-generate-rhel8:v4.16.1
        - name: ghcr.io/k8snetworkplumbingwg/sriov-network-device-plugin:latest
        - name: quay.io/openshift-scale/etcd-perf:latest
        - name: docker.io/centos/tools:latest
        - name: docker.io/f5devcentral/f5-hello-world:latest
        - name: docker.io/library/httpd:latest
        - name: docker.io/library/nginx:latest
      # Operators to be included in the appliance disk image.
      # See examples in https://github.com/openshift/oc-mirror/blob/main/docs/imageset-config-ref.yaml.
      # [Optional]
      operators:
      - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.16
        packages:
          - name: advanced-cluster-management
          - name: cincinnati-operator
          - name: kubernetes-nmstate-operator
          - name: kubevirt-hyperconverged
          - name: local-storage-operator
          - name: lvms-operator
          - name: metallb-operator
          - name: multicluster-engine
          - name: odf-operator
          - name: openshift-gitops-operator
          - name: quay-operator
          - name: skupper-operator
          - name: sriov-network-operator
          - name: topology-aware-lifecycle-manager

#. Build the disk image. This will create a "raw" disk image for your cluster
   appliance.

   .. important:: To successfully run these commands you have to sudo.

   .. code-block:: bash

      sudo podman run --rm -it --pull newer --privileged --net=host -v $APPLIANCE_ASSETS:/assets:Z $APPLIANCE_IMAGE build

   .. tip:: If needed you can rebuild the disk image with another version
      or updated or additional manifests but you must first "clean" the assets
      directory first. The clean command keeps the cache folder under assets
      intact. To clean the entire cache as well, add the **\-\-cache** flag
      with the clean command.

      .. code-block:: bash

         sudo podman run --rm -it -v $APPLIANCE_ASSETS:/assets:Z $APPLIANCE_IMAGE clean

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

To create the install manifests follow the instructions found here:
`Agent-Based Install Notes <../ocp/agent-based-installer-notes.html>`_

#. With "openshift-install" run the following command. In my case I'm using a
   "workdir" dir to supply the required yaml files.

   .. important:: The big difference between this method and "Agent-Based" is
      this command syntax. Substituting the command switch "agent create image"
      for "agent create config-image"

   .. code-block:: bash

      openshift-install agent create config-image --dir workdir

   .. note:: This is not a bootable image. It contains all the necessary
      information to build the cluster. The boot image is contained on the disk
      images created earlier.


#. Boot the VM's with the ISO created in the previous step. Follow the progress
   with the following command:

   .. code-block:: bash

      openshift-install agent wait-for install-complete --dir workdir
