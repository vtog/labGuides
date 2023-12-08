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
      :emphasize-lines: 5, 8, 11-13

      cat << EOF > ./pv-bfg-nfs.yaml
      apiVersion: v1
      kind: PersistentVolume
      metadata:
        name: bfg-nfs1
      spec:
        capacity:
          storage: 200Gi
        accessModes:
        - ReadWriteOnce
        nfs:
          path: /mirror/nfs
          server: 192.168.1.72
        persistentVolumeReclaimPolicy: Retain
      EOF

#. Create the new PV

   .. code-block:: bash

      oc create -f pv-bfg-nfs1.yaml

#. Verify the PV

   .. code-block:: bash

      oc get pv

      NAME       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS
      bfg-nfs1   200Gi      RWO            Retain           Available

Create the PVC
--------------

.. important:: The pvc needs to match the pv's "accessModes", and "storage".

#. Create the PVC yaml file

   .. code-block:: bash
      :emphasize-lines: 13, 16

      cat << EOF > ./pvc-image-registry-storage.yaml
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
        - ReadWriteOnce
        resources:
          requests:
            storage: 200Gi
        volumeMode: Filesystem
      EOF

#. Create the new PVC

   .. code-block:: bash

      oc create -f pvc-image-registry-storage.yaml

#. Verifiy the PVC

   .. code-block:: bash

      oc get pvc

      NAME                     STATUS   VOLUME     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
      image-registry-storage   Bound    bfg-nfs1   200Gi      RWO                           22h

   .. code-block:: bash

      oc get pv

      NAME       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM
      bfg-nfs1   200Gi      RWO            Retain           Bound       openshift-image-registry/image-registry-storage

