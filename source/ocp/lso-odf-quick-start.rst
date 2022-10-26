Local Storage & ODF Operator Quick Start
========================================

This document will describe the installation of the Local Storage Operator
(LSO) and OpenShift Data Foundations (ODF). LSO is a pre-requisite for
installing ODF on OpenShift nodes that will use local block devices.

.. warning::
   We’ve found that hugepages needs to be disabled before installing ODF
   otherwise noobaa pods won’t start correctly. This can be re-enabled
   afterwards.

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
#. Name the new volume, example "odf-block"
#. Expand "StorageClassDevice" by clicking the carrot to the right of the section
#. Expand "Device Paths" again by clicking the carrot to the right of the section
#. Add all the deviceID's recording in step 14
#. Name the Storage Class Name, example "odf-block"
#. Set "Fs Type" = \<blank\>
#. Set "Volume Mode" = Block
#. Set "Requested management state" = Managed
#. Set "LogLevel" = Normal
#. Click Create

   .. image:: images/createlocalvolume.png

Install and Configure OpenShift Data Foundation (ODF)
-----------------------------------------------------

1. From the OCP Web Console go to :menuselection:`Operators --> OperatorHub`
#. In the Filter by keyword box type, "ODF"
#. Select "OpenShift Data Foundation" operator
#. Click "Install"
#. Accept the defaults and click "Install"
#. After install completes go to :menuselection:`Operators --> Installed Operators`
#. Select "OpenShift Data Foundation"
#. Click "Create StorageSystem"
#. Select "Use an existing StorageClass"
#. Under StorageClass dropdown select "odf-block"

   .. note:: Your name may be different

#. Click Next
#. You should see the total "Available raw capacity" of your selected nodes
#. Click Next
#. Leave defaults and click Next
#. Review the information, if acceptable click "Create StorageSystem"

   .. note:: This can take several minutes to complete.

#. Verify “ocs-storagecluster-cephfs” is created

   .. code-block:: console

      oc get sc

   .. attention:: Do NOT attempt the next step until you see the newly created
      storage class.

   .. image:: images/ocgetsc.png

#. Set the default storage class to “ocs-storagecluster-cephfs”

   .. code-block:: console

      oc patch storageclass ocs-storagecluster-cephfs -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'

   .. image:: images/ocgetscdef.png   

Optional: Disable Noobaa
------------------------

1. Create and the following CRD. "vi disableNoobaa.yaml"

   .. code-block:: yaml

      apiVersion: ocs.openshift.io/v1
      kind: StorageCluster
      metadata:
        name: ocs-storagecluster
        namespace: openshift-storage
      spec:
        multiCloudGateway:
          reconcileStrategy: ignore

#. Apply CRD

   .. code-block:: console

      oc apply -f disableNoobaa.yaml


#. Remove Noobaa objects

   .. code-block:: console

      oc delete noobaas.noobaa.io  --all

Notes
-----

I've noticed deleting PVC sometimes doesn't work and they'll be stuck in the
"Terminating" phase.  The following command will remove them:

.. code-block:: console

   oc patch pvc <PVC_NAME> -p '{"metadata":{"finalizers":null}}'

