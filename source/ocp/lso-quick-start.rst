Local Storage Operator Quick Start
==================================

This document describes the installation of the Local Storage Operator(LSO).
This is a simple way to allocate local storage for the image registry.

Install and Configure the Local Storage Operator
------------------------------------------------

1. From the OCP Web Console go to :menuselection:`Operators --> OperatorHub`

#. In the Filter by keyword box type, "local storage"
#. Select "Local Storage" operator

   .. image:: images/operatorhublocalstorage.png

#. Click "Install"
#. By default, the "openshift-local-storage" namespace will be used. Accept
   the defaults and click "Install"
#. After install completes click "View Operator"
#. Select the "Local Volume Discovery" tab
#. Click "Create Local Volume Discover"
#. Under "Node Selector" select the option based on your environment
#. Click "Create"
#. After this completes go to :menuselection:`Home --> API Explorer`
#. In the search box search for "LocalVolumeDiscoveryResult" and click on
   the discovered object "LocalVolumeDiscoveryResult"
#. Select the "Instances" tab

   .. image:: images/localvolumediscoveryresult.png

#. Click the first instance name, click the YAML tab, and scroll to the bottom
   of the output. The last device, in this labs case "/dev/vdb" should be the 
   correct device. Make note of the "deviceID". Also note this device should
   show as "Available".

   .. important:: Using the "deviceID" will prevent future issues from happening
      if for some reason the order of the drives change.

#. Repeat step 14 for each discovered instance
#. Go to :menuselection:`Operators --> Installed Operators` and select "Local Storage" operator
#. Select the "Local Volume" tab and click "Create Local Volume"

   .. important:: This will automatically create pv's that consume the entire                 
      device. If smaller pv's are required, partition the device before
      creating the Local Volumes.

#. Name the new volume, example "lso-fs"
#. Expand "StorageClassDevice" by clicking the carrot to the right of the section
#. Expand "Device Paths" again by clicking the carrot to the right of the section
#. Add all the deviceID's recording in step 14
#. Name the Storage Class Name, example "lso-fs"
#. Set "Fs Type" = ext4
#. Set "Volume Mode" = Filesystem
#. Set "Requested management state" = Managed
#. Set "LogLevel" = Normal
#. Click Create

   .. image:: images/createlocalvolumeFS.png

Configure the Image Registry storage claim
------------------------------------------

#. Change project

   .. code-block:: bash

      oc project openshift-image-registry

#. Set image registry to Managed by patching the config

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'

#. Add the PVC by editing the image registry config

   .. code-block:: bash

      oc edit configs.imageregistry.operator.openshift.io cluster

      # Replace the "storage: {}" line with the following
      #
      # storage:
      #   pvc:
      #     claim:

#. Check pvc STATUS = "Bound"

   .. code-block:: bash

      oc get pvc

#. The previous steps will automatically create a pvc that needs to be
   replaced.

   .. important:: The pvc needs to match the pv's "storage", "accessModes",
      and "storageClassName".

   First delete the pvc:

   .. code-block:: bash

      oc delete pvc image-registry-storage

   With vi create a new file called "imageregpvc.yaml". Copy & paste the
   following yaml:

   .. code-block:: yaml

      apiVersion: v1
      kind: PersistentVolumeClaim
      metadata:
        annotations:
          imageregistry.openshift.io: "true"
        finalizers:
        - kubernetes.io/pvc-protection
        name: image-registry-storage
        namespace: openshift-image-registry
      spec:
        storageClassName: lso-fs
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 200Gi
       volumeMode: Filesystem

   Create the new pvc:

   .. code-block:: bash

      oc create -f imageregpvc.yaml

Set the Image Registry's default route
--------------------------------------

#. Set the defaultRoute to true

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io/cluster --patch '{"spec":{"defaultRoute":true}}' --type=merge

#. Get the default registry route

   .. code-block:: bash

      HOST=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')

#. Get the cluster’s default certificate and add to the clients local ca-trust

   .. code-block:: bash

      oc get secret -n openshift-ingress router-certs-default -o go-template='{{index .data "tls.crt"}}' | base64 -d | sudo tee

#. Update the clients local ca-trust

   .. code-block:: bash

      sudo update-ca-trust enable

#. Log in with podman using the default route

   .. code-block:: bash

      podman login -u kubeadmin -p $(oc whoami -t) $HOST

