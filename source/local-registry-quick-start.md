# Local Registry Quick Start

This document will describe the installation of the Local Storage Operator (LSO)
and OpenShift Data Foundations (ODF). LSO is a pre-requisite for installing ODF
on OpenShift nodes that will use local block devices.

:::{important}
These instructions assume you've configured persistant volume (PV) and
persistant volume claim (PVC). More specifically followed the "LSO & ODF Quick
Start".
:::

1. Configure the local Image Registry storage claim

    1. Change project
       ```
       oc project openshift-image-registry
       ```
    2. Patch the image registry config
       ```
       oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'
       ```
    3. Set the storage class "ocs-storagecluster-cephfs" as default
       ```
       oc patch storageclass ocs-storagecluster-cephfs -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'
       ```    
    4. Verify storage class default
       ```
       oc get sc
       ```
    5. Add PVC claim by editing the config
       ```
       oc edit configs.imageregistry.operator.openshift.io
       
       # Replace the "storage: {}" line with the following
       #
       # storage:
       #   pvc:
       #     claim:
       ```
    6. Check pvc STATUS = "Bound"
       ```
       oc get pvc
       ```

2. Local registry quick start

    1. Set the defaultRoute to true:
       ```
       oc patch configs.imageregistry.operator.openshift.io/cluster --patch '{"spec":{"defaultRoute":true}}' --type=merge
       ```
    2. Get the default registry route:
       ```
       HOST=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')
       ```
    3. Enable the cluster’s default certificate to trust the route using the following commands:
       ```
       oc get secret -n openshift-ingress  router-certs-default -o go-template='{{index .data "tls.crt"}}' | base64 -d | sudo tee /etc/pki/ca-trust/source/anchors/${HOST}.crt  > /dev/null
       ```
    4. Enable the cluster’s default certificate to trust the route using the following commands:
       ```
       sudo update-ca-trust enable
       ```
    5. Log in with podman using the default route:
       ```
       sudo podman login -u kubeadmin -p $(oc whoami -t) $HOST
       ```
