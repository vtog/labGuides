# Local Registry Quick Start

This document will describe the installation of the Local Storage Operator (LSO)
and OpenShift Data Foundations (ODF). LSO is a pre-requisite for installing ODF
on OpenShift nodes that will use local block devices.

:::{important}
These instructions assume you've configured a persistant volume (PV). More
specifically followed the "LSO & ODF Quick Start".
:::

1. Create an HTPasswd file using linux

    1. Create your flat file with a user name and hashed password
       ```console
       htpasswd -c -B -b </path/to/users.htpasswd> <user_name> <password>
       ```
    2. Add or delete users as needed
       
       - Add
       ```console
       htpasswd -B -b </path/to/users.htpasswd> <user_name> <password>
       ```
       - Delete
       ```console
       htpasswd -D users.htpasswd <username>
       ```
    3. From the OCP console create the HTPasswd secret and identity provider.

       1. Click on User Administration --> Cluster Settings, click Configuration tab
       2. Filter list "oath" and click the "OAuth" resource
       3. In the Identity providers section click "Add" and select "HTPasswd"
       4. Give the new object a unique name
       5. Click "Browse" and upload the file created earlier
       6. Click "Add"

    4. Test user auth
       ```console
       oc login -u <user_name>
       
       oc whoami
       ```
    5. Update users for an htpasswd identity provider

       1. Get secret
          ```console
          oc get secret htpass-secret -ojsonpath={.data.htpasswd} -n openshift-config | base64 --decode > users.htpasswd
          ```
       2. Add or delete users (see step 2)
       3. Update secret
          ```console
          oc create secret generic htpass-secret --from-file=htpasswd=users.htpasswd --dry-run=client -o yaml -n openshift-config | oc replace -f -
          ```
    6. If you remove a user from htpasswd you must manually remove the user resources from OCP
       ```console
       oc delete user <username>
       
       #AND

       oc delete identity <identity_provider>:<username>
       ```

2. Configure the local Image Registry storage claim

    1. Change project
       ```console
       oc project openshift-image-registry
       ```
    2. Patch the image registry config
       ```console
       oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'
       ```
    3. Set the storage class "ocs-storagecluster-cephfs" as default
       ```console
       oc patch storageclass ocs-storagecluster-cephfs -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'
       ```    
    4. Verify storage class default
       ```console
       oc get sc
       ```
    5. Add PVC claim by editing the config
       ```console
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

3. Local registry quick start

    1. Set the defaultRoute to true:
       ```console
       oc patch configs.imageregistry.operator.openshift.io/cluster --patch '{"spec":{"defaultRoute":true}}' --type=merge
       ```
    2. Get the default registry route:
       ```console
       HOST=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')
       ```
    3. Enable the cluster’s default certificate to trust the route using the following commands:
       ```console
       oc get secret -n openshift-ingress  router-certs-default -o go-template='{{index .data "tls.crt"}}' | base64 -d | sudo tee /etc/pki/ca-trust/source/anchors/${HOST}.crt  > /dev/null
       ```
    4. Enable the cluster’s default certificate to trust the route using the following commands:
       ```console
       sudo update-ca-trust enable
       ```
    5. Log in with podman using the default route:
       ```console
       podman login -u kubeadmin -p $(oc whoami -t) $HOST
       ```
       :::{note}
       Login with the user created with HTPasswd. Be sure to add the proper
       RoleBindings to your project.
       :::

