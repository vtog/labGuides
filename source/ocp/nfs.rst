External Storage (NFS)
======================

The following example shows how to apply external storage for the Image
Registry Operator.

.. seealso:: `Image Registry Operator <./image-registry.html>`_

.. attention:: The following assumes an NFS share is already created on the
   network and operational. If not see `NFS Server & Client <../env/nfs.html>`_.

Create the PV
-------------

#. Create the PV yaml file

   .. code-block:: bash
      :emphasize-lines: 5,8,10,12-13

      cat << EOF | oc create -f -
      apiVersion: v1
      kind: PersistentVolume
      metadata:
        name: bfg-nfs1
      spec:
        capacity:
          storage: 200Gi
        accessModes:
        - ReadWriteMany
        nfs:
          path: /mirror/nfs
          server: 192.168.1.72
        persistentVolumeReclaimPolicy: Retain
      EOF

#. Verify the PV

   .. code-block:: bash

      oc get pv

      NAME       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS
      bfg-nfs1   200Gi      RWO            Retain           Available

Create the PVC
--------------

.. important:: The pvc needs to match the pv's "accessModes", "storage", and
   "volumeName".

#. Create the PVC yaml file

   .. code-block:: bash
      :emphasize-lines: 13,16,18

      cat << EOF | oc create -f -
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
        accessModes:
        - ReadWriteMany
        resources:
          requests:
            storage: 200Gi
        volumeMode: Filesystem
        volumeName: bfg-nfs1
      EOF

#. Verifiy the PVC

   .. code-block:: bash

      oc get pvc

      NAME                     STATUS   VOLUME     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
      image-registry-storage   Bound    bfg-nfs1   200Gi      RWO                           22h

   .. code-block:: bash

      oc get pv

      NAME       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM
      bfg-nfs1   200Gi      RWO            Retain           Bound       openshift-image-registry/image-registry-storage
