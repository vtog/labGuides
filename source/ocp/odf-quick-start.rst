ODF Operator Quick Start
========================

This document will describe the installation of the Local Storage Operator
(LSO) and OpenShift Data Foundations (ODF). LSO is a pre-requisite for
installing ODF on OpenShift nodes that will use local block devices.

.. important:: With 4.11+ ODF added a wizard removing the need to manually
   create all the required objects. The install and configuration process is
   much easier. I've removed my old manual notes and replaced them with a
   wizard walk-through.

.. warning::
   We’ve found that hugepages needs to be disabled before installing ODF
   otherwise noobaa pods won’t start correctly. This can be re-enabled
   afterwards.

Add Local Storage and ODF Operators
-----------------------------------

1. From the OCP Web Console go to :menuselection:`Operators --> OperatorHub`.
#. In the Filter by keyword box type, "local storage".
#. Select **"Local Storage"** operator.
#. Click "Install".
#. By default, the "openshift-local-storage" namespace will be used. Accept the
   defaults and click "Install".
#. After install finishes go back to :menuselection:`Operators -->
   OperatorHub`.
#. In the Filter by keyword box type, "ODF".
#. Select **"OpenShift Data Foundation"** operator.
#. Click "Install".
#. Accept the defaults and click "Install".
#. Go to next section to configure ODF.

Configure ODF
-------------

#. Frome the web console go to :menuselection:`Operators --> Installed
   Operators`.
#. Select "OpenShift Data Foundation".
#. Enable Console plugin.

   .. tip:: Be sure to wait a couple minutes and refresh browser.
      The console should prompt you.

   .. image:: images/enableodfplugin.png

#. Click "Create StorageSystem".
#. Select "Create a new StorageClass using local storage devices".
#. Click Next.

   .. note:: This may take several minutes to discover the available block
      devices.

#. Name LocalVolumeSet name "odf-block".

   .. image:: images/createlocalvolumeset.png

#. Click Next.
#. Are you sure you want to continue? Select Yes for "Create LocalVolumeSet".

   .. note:: This may take several minutes to create the LocalVolumeSet.

#. Confirm Capacity and nodes.

   .. note:: You should see the total "Available raw capacity" of your selected
      nodes.

#. Click Next.
#. Leave defaults for Security and network and click Next.
#. Review the information, if acceptable click "Create StorageSystem".

   .. note:: This can take several minutes to complete.

#. Verify “ocs-storagecluster-cephfs” is created.

   .. code-block:: bash

      oc get sc

   .. attention:: Do NOT attempt the next step until you see the newly created
      storage class.

   .. image:: images/ocgetsc.png

#. Set the default storage class to “ocs-storagecluster-cephfs”.

   .. code-block:: bash

      oc patch storageclass ocs-storagecluster-cephfs --patch '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'

   .. image:: images/ocgetscdef.png

Optional: Disable NooBaa
------------------------
NooBaa is multicloud object gateway and may not be needed in your environment.
The following steps walk through disabling the function freeing up resources.

#. Change to openshift-storage project, or append "-n openshift-storage" to
   each patch command below.

   .. code-block:: bash

      oc project openshift-storage

#. Edit storagecluster ocs-storagecluster and add strategy.

   .. code-block:: bash

      oc patch storagecluster ocs-storagecluster --type merge --patch '{"spec":{"multiCloudGateway":{"reconcileStrategy":"ignore"}}}'

      # oc edit storagecluster ocs-storagecluster
      # spec:
      #   multiCloudGateway:
      #     reconcileStrategy: ignore

#. Edit NooBaa and add allow deletion.

   .. code-block:: bash

      oc patch noobaa noobaa --type merge --patch '{"spec":{"cleanupPolicy":{"allowNoobaaDeletion":true}}}'

      # oc edit noobaa noobaa
      # spec:
      #   cleanupPolicy:
      #     allowNoobaaDeletion: true

#. Remove NooBaa objects.

   .. code-block:: bash

      oc delete noobaas.noobaa.io --all
