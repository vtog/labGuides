Image Registry Operator
=======================

This operator is installed by default with every OpenShift cluster. For it to
work you simply need to allocate storage (PV) and a PVC. This can be
accomplished with the local storage operator and or ODF or External Storage
(NFS).

.. seealso:: `ODF Operator Quick Start <./odf-quick-start.html>`_

   `Local Storage Operator Quick Start <./lso-quick-start.html>`_

   `External Storage (NFS) <./nfs.html>`_

Configure the storage claim
---------------------------

#. Change project

   .. code-block:: bash

      oc project openshift-image-registry

#. Set image registry to Managed by patching the config

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'

#. Add the PVC by editing the image registry config

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"storage":{"pvc":{"claim":""}}}}'

      # Replace the "storage: {}" line with the following
      #
      # spec:
      #   storage:
      #     pvc:
      #       claim:

#. Check pvc STATUS = "Bound". This step may fail if not using a storage class
   with RWX (ReadWriteMany) access mode.

   .. code-block:: bash

      oc get pvc

#. If the pvc is "Pending" due to the default storage class, the pvc will need
   to be modified. The "accessModes" must match. Block type storage uses RWO
   (ReadWriteOnce).

   .. important:: When using the **Local Storage Operator, NOT ODF**. This step
      will need to be taken. The pvc needs to match the pv's
      "storageClassName", "accessModes", and "storage".

   A. Copy the current pvc to yaml file.

      .. code-block:: bash

         oc get -n openshift-image-registry pvc image-registry-storage -o yaml > image-registry-storage.yaml

   #. Delete the pvc.

      .. code-block:: bash

         oc delete -n openshift-image-registry pvc image-registry-storage

   #. Edit the previously saved file "image-registry-storage.yaml".

      .. code-block:: yaml
         :emphasize-lines: 14, 17, 18

         apiVersion: v1
         kind: PersistentVolumeClaim
         metadata:
           annotations:
             imageregistry.openshift.io: "true"
             volume.beta.kubernetes.io/storage-provisioner: openshift-storage.rbd.csi.ceph.com
             volume.kubernetes.io/storage-provisioner: openshift-storage.rbd.csi.ceph.com
           finalizers:
           - kubernetes.io/pvc-protection
           name: image-registry-storage
           namespace: openshift-image-registry
         spec:
           accessModes:
           - ReadWriteOnce
           resources:
             requests:
               storage: 100Gi
           storageClassName: lso-fs
           volumeMode: Filesystem

   #. Create the new pvc:

      .. code-block:: bash

         oc create -f image-registry-storage.yaml

Set the default route
---------------------

#. Set the defaultRoute to true

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io/cluster --type=merge --patch '{"spec":{"defaultRoute":true}}'

#. Get the default registry route

   .. code-block:: bash

      REGROUTE=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')

#. Get the cluster’s default certificate and add to the clients local ca-trust

   .. code-block:: bash

      oc get secret -n openshift-ingress router-certs-default -o go-template='{{index .data "tls.crt"}}' \
      | base64 -d | sudo tee /etc/pki/ca-trust/source/anchors/${REGROUTE}.crt  > /dev/null

#. Update the clients local ca-trust

   .. code-block:: bash

      sudo update-ca-trust

#. Log in with podman using the default route. You'll need to login to your
   cluster with "kubeadmin" first in order to receive a user token.

   .. code-block:: bash

      oc login -u kubeadmin

      podman login -u kubeadmin -p $(oc whoami -t) $REGROUTE

   Should see the following output:

   .. code-block:: bash

      Login Succeeded!

   .. note:: If an error is returned as well, it's because "oc whoami -t" does
      not have a token. Try logging into the cluster first.

Upload Image
------------

#. Log in into OpenShift API with user that has appropriate permissions.

   .. code-block:: bash

      oc login -u kubeadmin

#. Log into registry via external route.

   .. code-block:: bash

      REGROUTE=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')

      podman login -u kubeadmin -p $(oc whoami -t) $REGROUTE

#. Upload image to local repo

   .. code-block:: bash

      podman pull mirror.lab.local:8443/f5devcentral/f5-hello-world

   .. tip:: To import a tarball

      .. code-block:: bash

         podman image load -i <tarball>

#. Tag local image for OCP registry

   .. attention:: The path must start with the project name. In this example
      I'm using project "default".

   .. code-block:: bash

      podman tag mirror.lab.local:8443/f5devcentral/f5-hello-world:latest $REGROUTE/default/f5-hello-world:latest

   .. tip::

      Tag multiple images

      .. code-block:: bash

         for image in $(podman images --format "{{.Repository}}:{{.Tag}}" | grep localhost | sed 's/^localhost\///'); \
         do podman tag $image $REGROUTE/default/$image; done

      Remove new tags

      .. code-block:: bash

         for image in $(podman images --format "{{.Repository}}:{{.Tag}}" | grep -v localhost); \
         do podman rmi $image; done

#. Push local image to OCP registry

   .. attention:: The project must exist in order to upload the image. In this
      example I'm using project "default".

   .. code-block:: bash

      podman push $REGROUTE/default/f5-hello-world:latest

   .. tip:: Push multiple images

      .. code-block:: bash

         for image in $(podman images --format "{{.Repository}}:{{.Tag}}" | grep -v localhost); \
         do podman push $image; done

#. View image on OCP registry

   .. code-block:: bash

      oc get is -n default

   .. image:: images/imageuploadexample.png

#. Access the image/registry directly from a cluster node

   .. code-block:: bash

      ssh core@host11

      oc login -u kubeadmin https://api-int.ocp1.lab.local:6443

      podman login -u kubeadmin -p $(oc whoami -t) image-registry.openshift-image-registry.svc:5000

      podman pull image-registry.openshift-image-registry.svc:5000/default/f5-hello-world

#. Use the internal name for deployments

   .. code-block:: yaml
      :emphasize-lines: 8

      spec:
        containers:
        - env:
          - name: service_name
            value: f5-hello-world-web
          #image: mirror.lab.local:8443/f5devcentral/f5-hello-world:latest
          #image: default-route-openshift-image-registry.apps.ocp1.lab.local/default/f5-hello-world:latest
          image: image-registry.openshift-image-registry.svc:5000/default/f5-hello-world:latest
          imagePullPolicy: Always
          name: f5-hello-world-web
